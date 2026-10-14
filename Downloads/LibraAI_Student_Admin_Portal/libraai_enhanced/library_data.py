"""Book catalog and simulated 10x10 library layout for LibraAI."""

GRID_SIZE = 10
ENTRANCE = (0, 0)

# Simulated shelves/walls that cannot be traversed. Keep book access positions
# walkable; these coordinates represent the aisle-side position for each book.
OBSTACLES = {
    (2, 2), (2, 3), (2, 4),
    (4, 5), (5, 5), (6, 5),
    (7, 2), (7, 3), (7, 4),
    (4, 8), (5, 8),
}

# Each position is the walkable aisle cell from which the shelf/book is reached.
BOOKS = [
    {"id": "B001", "title": "Artificial Intelligence: A Modern Approach", "author": "Stuart Russell and Peter Norvig", "category": "Artificial Intelligence", "description": "A comprehensive introduction to intelligent agents, search, reasoning, planning, and machine learning.", "shelf": "A1", "position": (1, 1)},
    {"id": "B002", "title": "Deep Learning", "author": "Ian Goodfellow, Yoshua Bengio and Aaron Courville", "category": "Deep Learning", "description": "Neural networks, representation learning, optimization, and deep learning methods.", "shelf": "A2", "position": (1, 4)},
    {"id": "B003", "title": "Pattern Recognition and Machine Learning", "author": "Christopher Bishop", "category": "Machine Learning", "description": "Probabilistic models, classification, regression, clustering, and pattern recognition.", "shelf": "A3", "position": (1, 6)},
    {"id": "B004", "title": "Hands-On Machine Learning", "author": "Aurélien Géron", "category": "Machine Learning", "description": "Practical machine learning workflows, model training, neural networks, and deployment.", "shelf": "A4", "position": (1, 8)},
    {"id": "B005", "title": "Natural Language Processing with Python", "author": "Steven Bird, Ewan Klein and Edward Loper", "category": "NLP", "description": "Text processing, language structure, tokenization, tagging, and natural language applications.", "shelf": "B1", "position": (3, 0)},
    {"id": "B006", "title": "Speech and Language Processing", "author": "Daniel Jurafsky and James Martin", "category": "NLP", "description": "Language models, speech, syntax, semantics, information extraction, and conversational systems.", "shelf": "B2", "position": (3, 2)},
    {"id": "B007", "title": "Computer Networking: A Top-Down Approach", "author": "James Kurose and Keith Ross", "category": "Computer Networks", "description": "Internet protocols, application layers, routing, transport, wireless networks, and security.", "shelf": "B3", "position": (3, 6)},
    {"id": "B008", "title": "Computer Networks", "author": "Andrew Tanenbaum and David Wetherall", "category": "Computer Networks", "description": "Network architecture, protocols, routing algorithms, network services, and distributed systems.", "shelf": "B4", "position": (3, 8)},
    {"id": "B009", "title": "Operating System Concepts", "author": "Abraham Silberschatz, Peter Galvin and Greg Gagne", "category": "Operating Systems", "description": "Processes, threads, scheduling, memory management, file systems, and operating system design.", "shelf": "C1", "position": (5, 1)},
    {"id": "B010", "title": "Modern Operating Systems", "author": "Andrew Tanenbaum and Herbert Bos", "category": "Operating Systems", "description": "Operating system structure, concurrency, memory, storage, virtualization, and security.", "shelf": "C2", "position": (5, 3)},
    {"id": "B011", "title": "Database System Concepts", "author": "Abraham Silberschatz, Henry Korth and S. Sudarshan", "category": "Database Systems", "description": "Relational databases, SQL, transactions, indexing, query processing, and database design.", "shelf": "C3", "position": (5, 7)},
    {"id": "B012", "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "category": "Data Engineering", "description": "Reliable, scalable data systems, distributed databases, streams, replication, and consistency.", "shelf": "C4", "position": (6, 7)},
    {"id": "B013", "title": "Introduction to Algorithms", "author": "Thomas H. Cormen and others", "category": "Algorithms", "description": "Algorithm design, graph algorithms, data structures, dynamic programming, and complexity.", "shelf": "D1", "position": (8, 0)},
    {"id": "B014", "title": "Data Structures and Algorithm Analysis", "author": "Mark Allen Weiss", "category": "Data Structures", "description": "Lists, trees, heaps, graphs, sorting, searching, and algorithm analysis.", "shelf": "D2", "position": (8, 3)},
    {"id": "B015", "title": "Computer Vision: Algorithms and Applications", "author": "Richard Szeliski", "category": "Computer Vision", "description": "Image formation, feature detection, recognition, image alignment, and visual understanding.", "shelf": "D3", "position": (8, 5)},
    {"id": "B016", "title": "Data Mining: Concepts and Techniques", "author": "Jiawei Han, Micheline Kamber and Jian Pei", "category": "Data Science", "description": "Data preprocessing, frequent patterns, classification, clustering, and mining large datasets.", "shelf": "D4", "position": (8, 8)},
    {"id": "B017", "title": "Computer Security: Principles and Practice", "author": "William Stallings and Lawrie Brown", "category": "Cybersecurity", "description": "Security principles, cryptography, access control, network defense, and secure systems.", "shelf": "E1", "position": (0, 5)},
    {"id": "B018", "title": "Cryptography and Network Security", "author": "William Stallings", "category": "Cybersecurity", "description": "Encryption, hash functions, digital signatures, authentication, TLS, and network security.", "shelf": "E2", "position": (0, 8)},
    {"id": "B019", "title": "Software Engineering", "author": "Ian Sommerville", "category": "Software Engineering", "description": "Software requirements, architecture, design, testing, maintenance, and development processes.", "shelf": "E3", "position": (6, 0)},
    {"id": "B020", "title": "Python for Data Analysis", "author": "Wes McKinney", "category": "Programming", "description": "Python, pandas, data cleaning, transformation, analysis, and practical data workflows.", "shelf": "E4", "position": (9, 6)},
]


# Additional catalog records to make the demo resemble a university technical library.
# Inventory counts are simulated demonstration data, not a live library database.
_EXTRA_BOOKS = [
("Clean Code", "Robert C. Martin", "Software Engineering", "Practical principles for writing readable, maintainable, and testable software."),
("The Pragmatic Programmer", "David Thomas and Andrew Hunt", "Programming", "Software craftsmanship, debugging, automation, and practical development habits."),
("Design Patterns", "Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides", "Software Engineering", "Reusable object-oriented design patterns and software architecture."),
("Refactoring", "Martin Fowler", "Software Engineering", "Improving code structure safely through systematic refactoring techniques."),
("Effective Java", "Joshua Bloch", "Programming", "Best practices for robust, efficient, and maintainable Java applications."),
("Fluent Python", "Luciano Ramalho", "Programming", "Python data model, functions, collections, concurrency, and idiomatic programming."),
("Learning Python", "Mark Lutz", "Programming", "Core Python syntax, data types, functions, classes, and scripting."),
("Automate the Boring Stuff with Python", "Al Sweigart", "Programming", "Practical Python automation for files, spreadsheets, web tasks, and everyday workflows."),
("Computer Organization and Design", "David A. Patterson and John L. Hennessy", "Computer Architecture", "Processor design, instruction sets, memory hierarchy, and computer performance."),
("Computer Architecture: A Quantitative Approach", "John L. Hennessy and David A. Patterson", "Computer Architecture", "Quantitative analysis of processor architecture, parallelism, and memory systems."),
("Digital Design and Computer Architecture", "David Money Harris and Sarah L. Harris", "Computer Architecture", "Digital logic, processor datapaths, control units, and hardware design."),
("Discrete Mathematics and Its Applications", "Kenneth H. Rosen", "Mathematics", "Logic, proofs, sets, combinatorics, graph theory, and discrete structures."),
("Introduction to the Theory of Computation", "Michael Sipser", "Theory of Computation", "Automata, computability, formal languages, and computational complexity."),
("Compilers: Principles, Techniques, and Tools", "Alfred V. Aho and others", "Compiler Design", "Lexical analysis, parsing, semantic analysis, optimization, and code generation."),
("Modern Compiler Implementation in C", "Andrew W. Appel", "Compiler Design", "Compiler construction, intermediate representations, register allocation, and code generation."),
("Database Internals", "Alex Petrov", "Database Systems", "Storage engines, distributed systems, database indexes, and transaction processing."),
("SQL Antipatterns", "Bill Karwin", "Database Systems", "Common database design mistakes and practical ways to avoid them."),
("Fundamentals of Database Systems", "Ramez Elmasri and Shamkant Navathe", "Database Systems", "Database modeling, relational systems, SQL, normalization, and transactions."),
("Distributed Systems", "Maarten van Steen and Andrew S. Tanenbaum", "Distributed Systems", "Distributed architectures, communication, consistency, replication, and fault tolerance."),
("Designing Distributed Systems", "Brendan Burns", "Distributed Systems", "Reusable patterns for scalable and resilient distributed applications."),
("Computer Systems: A Programmer's Perspective", "Randal E. Bryant and David R. O'Hallaron", "Systems Programming", "Machine-level programs, memory, linking, exceptional control flow, and concurrency."),
("The Linux Programming Interface", "Michael Kerrisk", "Operating Systems", "Linux system calls, processes, files, signals, memory, and threads."),
("Linux Kernel Development", "Robert Love", "Operating Systems", "Kernel architecture, process management, scheduling, and Linux internals."),
("TCP/IP Illustrated, Volume 1", "W. Richard Stevens and others", "Computer Networks", "TCP/IP protocols, packet behavior, transport, and network troubleshooting."),
("Computer Security: Art and Science", "Matt Bishop", "Cybersecurity", "Security models, access control, cryptography, and system protection."),
("The Web Application Hacker's Handbook", "Dafydd Stuttard and Marcus Pinto", "Cybersecurity", "Web application vulnerabilities, testing methods, and defensive security concepts."),
("Practical Malware Analysis", "Michael Sikorski and Andrew Honig", "Cybersecurity", "Static and dynamic malware analysis, reverse engineering, and investigation workflows."),
("Introduction to Information Retrieval", "Christopher D. Manning, Prabhakar Raghavan and Hinrich Schütze", "Information Retrieval", "Indexing, ranking, text retrieval, evaluation, and search engines."),
("Speech and Language Processing", "Daniel Jurafsky and James H. Martin", "NLP", "Natural language processing, language models, syntax, semantics, and speech."),
("Natural Language Processing with Transformers", "Lewis Tunstall, Leandro von Werra and Thomas Wolf", "NLP", "Transformer models, fine-tuning, datasets, and NLP application development."),
("Information Theory, Inference, and Learning Algorithms", "David J. C. MacKay", "Machine Learning", "Information theory, probabilistic inference, coding, and learning algorithms."),
("The Elements of Statistical Learning", "Trevor Hastie, Robert Tibshirani and Jerome Friedman", "Machine Learning", "Statistical learning, regression, classification, model selection, and ensembles."),
("Machine Learning: A Probabilistic Perspective", "Kevin P. Murphy", "Machine Learning", "Probabilistic models, inference, graphical models, and machine learning methods."),
("Hands-On Unsupervised Learning Using Python", "Ankur A. Patel", "Data Science", "Practical clustering, dimensionality reduction, and unsupervised learning workflows."),
("Python Data Science Handbook", "Jake VanderPlas", "Data Science", "NumPy, pandas, Matplotlib, machine learning, and scientific Python tools."),
("Practical Statistics for Data Scientists", "Peter Bruce, Andrew Bruce and Peter Gedeck", "Data Science", "Statistical reasoning, sampling, experiments, regression, and data analysis."),
("Computer Vision: A Modern Approach", "David A. Forsyth and Jean Ponce", "Computer Vision", "Image formation, feature extraction, recognition, and visual geometry."),
("Multiple View Geometry in Computer Vision", "Richard Hartley and Andrew Zisserman", "Computer Vision", "Camera geometry, 3D reconstruction, and multi-view visual analysis."),
("Deep Learning for Computer Vision", "Rajalingappaa Shanmugamani", "Computer Vision", "Convolutional networks and deep-learning methods for image understanding."),
("Reinforcement Learning: An Introduction", "Richard S. Sutton and Andrew G. Barto", "Artificial Intelligence", "Agents, reward signals, value functions, and reinforcement learning algorithms."),
("Artificial Intelligence: Foundations of Computational Agents", "David L. Poole and Alan K. Mackworth", "Artificial Intelligence", "Search, planning, reasoning, uncertainty, and intelligent-agent design."),
("Algorithms", "Robert Sedgewick and Kevin Wayne", "Algorithms", "Algorithm analysis, sorting, searching, graphs, and practical implementations."),
("The Algorithm Design Manual", "Steven S. Skiena", "Algorithms", "Algorithmic problem solving, design techniques, graph algorithms, and heuristics."),
("Grokking Algorithms", "Aditya Y. Bhargava", "Algorithms", "Accessible visual introduction to searching, sorting, graphs, and optimization."),
("Introduction to Graph Theory", "Douglas B. West", "Mathematics", "Graph structures, connectivity, coloring, matchings, and graph algorithms."),
("Computer Graphics: Principles and Practice", "John F. Hughes and others", "Computer Graphics", "Rendering, geometric modeling, shading, animation, and graphics pipelines."),
("Interaction Design: Beyond Human-Computer Interaction", "Yvonne Rogers, Helen Sharp and Jenny Preece", "Human-Computer Interaction", "User-centered design, interaction principles, usability, and prototyping."),
("Don't Make Me Think", "Steve Krug", "Human-Computer Interaction", "Practical usability principles for intuitive websites and digital products."),
("The Mythical Man-Month", "Frederick P. Brooks Jr.", "Project Management", "Software project planning, team coordination, complexity, and delivery."),
("Software Testing", "Ron Patton", "Software Engineering", "Test planning, test cases, defect identification, and software quality."),
]

# Assign unused walkable aisle access points to the added titles.
_used_positions = {tuple(b["position"]) for b in BOOKS}
_free_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                   if (r, c) not in OBSTACLES and (r, c) not in _used_positions and (r, c) != ENTRANCE]
for i, (title, author, category, description) in enumerate(_EXTRA_BOOKS, start=21):
    if not _free_positions:
        break
    position = _free_positions.pop(0)
    BOOKS.append({
        "id": f"B{i:03d}", "title": title, "author": author,
        "category": category, "description": description,
        "shelf": f"{chr(65 + ((i - 1) // 10) % 5)}{((i - 1) % 10) + 1}",
        "position": position,
    })

# Simulated circulation inventory. Status is derived from copy counts.
# These values are demo data; a real deployment should use a database.
for index, book in enumerate(BOOKS):
    total = 2 + (index % 4 == 0) + (index % 7 == 0)
    # A deterministic mix of available, limited, and currently borrowed titles.
    available = total if index % 5 not in (0, 1) else (1 if total > 1 else 0)
    if index % 11 == 0:
        available = 0
    book["total_copies"] = int(total)
    book["available_copies"] = int(available)
    book["borrowed_copies"] = int(total - available)
    book["availability"] = "Available" if available == total else ("Limited" if available > 0 else "Borrowed / Unavailable")
    book["isbn"] = f"978-{1 + (index % 9)}-{(index * 1731 + 24000) % 90000:05d}-{(index * 37 + 101) % 1000:03d}-{(index % 9) + 1}"
    book["publication_year"] = 2008 + ((index * 3) % 18)
    book["language"] = "English"
    book["loan_period_days"] = 14


def get_categories():
    return sorted({book["category"] for book in BOOKS})


def is_walkable(position):
    x, y = position
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and position not in OBSTACLES
