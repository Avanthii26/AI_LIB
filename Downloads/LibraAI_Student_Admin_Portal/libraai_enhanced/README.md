# LibraAI — Enhanced Library Book Discovery and Route Planner

## Features
- Natural-language book search using Sentence Transformers when available, with TF-IDF and token-overlap fallbacks.
- Related-book recommendations.
- Obstacle-aware A* pathfinding on a 10×10 four-directional grid.
- Hill Climbing to improve the order of selected shelf locations.
- Original-vs-optimized route cost comparison and exhaustive benchmark for up to 8 selected books.
- Streamlit pages for Home, Discover Books, AI Navigation, Library Catalog, and Library Insights.

## Run on Windows
1. Open Command Prompt or PowerShell in this folder.
2. Create a virtual environment (recommended):
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Run the app:
   ```powershell
   streamlit run app.py
   ```

The Sentence Transformers model may download the first time it is used. If it is unavailable, search falls back to TF-IDF when scikit-learn is installed.

## Files
- `app.py`: Streamlit UI and integration.
- `library_data.py`: sample book catalog, entrance, grid and obstacles.
- `semantic_search.py`: semantic retrieval and related-book recommendations.
- `hill_climbing.py`: route ordering optimization and exhaustive benchmark.
- `astar.py`: obstacle-aware A* search.

## Important
This is a simulated map and sample catalog. Update book positions and obstacles together so shelf access cells remain walkable. The exhaustive benchmark is factorial and is intentionally limited to small selections. Hill Climbing is a local-search algorithm and is not guaranteed to find a globally optimal order.
