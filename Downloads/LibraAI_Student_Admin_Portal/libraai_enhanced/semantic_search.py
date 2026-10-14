"""Semantic book retrieval with optional Sentence Transformers and fallbacks."""
import re
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None


def _text(book):
    return " ".join(str(book.get(k, "")) for k in ("title", "author", "category", "description"))


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class SemanticSearch:
    """Search books by semantic similarity where available.

    By default, attempts a compact Sentence Transformers model. If unavailable,
    uses TF-IDF; if sklearn is also unavailable, falls back to token overlap.
    """
    def __init__(self, books, model_name="all-MiniLM-L6-v2", use_transformer=True):
        self.books = list(books)
        self.texts = [_text(book) for book in self.books]
        self.model = None
        self.vectorizer = None
        self.matrix = None
        self.backend = "token-overlap"
        if use_transformer and SentenceTransformer is not None and self.texts:
            try:
                self.model = SentenceTransformer(model_name)
                self.matrix = self.model.encode(self.texts, normalize_embeddings=True)
                self.backend = "sentence-transformers"
            except Exception:
                self.model = None
        if self.model is None and TfidfVectorizer is not None and self.texts:
            try:
                self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
                self.matrix = self.vectorizer.fit_transform(self.texts)
                self.backend = "tf-idf fallback"
            except Exception:
                self.vectorizer = None
                self.matrix = None

    def search(self, query, top_k=6, category=None, author=None):
        query = str(query or "").strip()
        if not query:
            return []
        if self.backend == "sentence-transformers":
            q = self.model.encode([query], normalize_embeddings=True)[0]
            scores = np.asarray(self.matrix @ q).reshape(-1)
        elif self.backend == "tf-idf fallback":
            q = self.vectorizer.transform([query])
            scores = cosine_similarity(q, self.matrix).reshape(-1)
        else:
            qt = _tokens(query)
            scores = []
            for text in self.texts:
                tokens = _tokens(text)
                scores.append(len(qt & tokens) / max(1, len(qt | tokens)))
            scores = np.asarray(scores)

        ranked = []
        for i, score in enumerate(scores):
            book = self.books[i]
            if category and book.get("category") != category:
                continue
            if author and author.lower() not in book.get("author", "").lower():
                continue
            result = dict(book)
            result["score"] = float(score)
            ranked.append(result)
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:max(0, int(top_k))]

    def recommend_books(self, selected_book, books=None, top_k=5, exclude_selected=True):
        """Recommend books related to a selected book's title/description."""
        catalog = list(books) if books is not None else self.books
        if isinstance(selected_book, dict):
            query = _text(selected_book)
            selected_id = selected_book.get("id")
            selected_title = selected_book.get("title")
        else:
            selected_title = str(selected_book)
            selected_id = None
            query = selected_title
            for b in catalog:
                if b.get("title") == selected_title:
                    query = _text(b)
                    selected_id = b.get("id")
                    break
        # Reuse this engine when it covers the same catalog; otherwise create a
        # lightweight engine for the provided catalog.
        engine = self if catalog == self.books else SemanticSearch(catalog, use_transformer=False)
        results = engine.search(query, top_k=len(catalog))
        output = []
        for result in results:
            if exclude_selected and ((selected_id is not None and result.get("id") == selected_id) or result.get("title") == selected_title):
                continue
            output.append(result)
            if len(output) >= top_k:
                break
        return output
