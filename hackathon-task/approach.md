# Our Approach – Adobe Hackathon Challenge

We built an intelligent PDF processing system that can understand and extract structured information from documents. In Round 1A, our system automatically detects titles and headings (H1, H2, H3) from raw PDFs using layout-based features and a trained ML model. In Round 1B, we extended this system to find the most relevant content based on a user's role (persona) and task (job-to-be-done), using semantic search powered by embeddings and a vector database.

## Round 1A: PDF Outline Extraction

### Objective:
Extract the document title and a structured outline of headings (H1, H2, H3) from raw PDFs.

### Key Steps:
1. **Text Extraction (`extract.py`)**
   - We use **PyMuPDF** to extract text with font size, style, position, and bounding box data.
   - Multiprocessing speeds up extraction for large PDFs.

2. **Line Grouping & Feature Engineering (`parser.py`)**
   - Groups text lines by vertical position and layout.
   - Extracted features include:
     - Font size relative to modal size
     - Centering and spacing
     - Bold/capital formatting
     - Numbering patterns (e.g., 1., 2.1.)

3. **Heading Classification**
   - A **Random Forest model** classifies each line into:
     - `Title`, `H1`, `H2`, `H3`, or `Other`
   - The model is trained and serialized using `scikit-learn`.

4. **Output Generation**
   - Hierarchical structure is built using heading levels and stored in the required JSON format.
   - Docker container automatically processes all files.



## Round 1B: Persona-Driven Document Intelligence

### Objective:
Given a persona and job-to-be-done, extract the most relevant sections from multiple documents.

### Key Steps:
1. **Section Extraction**
   - Reuses the JSON outline from Round 1A.
   - Extracts text under each heading using strict start/end page logic.
   - Stores:
     - `title`, `page_number`, `document_name`, `content`, etc.

2. **Embedding and Indexing (ChromaDB)**
   - Each section is embedded using **SentenceTransformer (`all-MiniLM-L6-v2`)**.
   - Combined `section_title + content` is stored in **ChromaDB** with full metadata.

3. **Semantic Querying**
   - The persona + job are converted into a query string.
   - Top relevant sections are retrieved using vector similarity.
   - Generic sections (e.g., "Acknowledgements", "Table of Contents") are filtered out.

4. **Ranking & Output**
   - Top-k sections are ranked by similarity.
   - `importance_rank` is assigned based on match score.
   - Final structured output JSON includes:
     - Metadata (persona, job, documents)
     - Relevant sections
     - Sub-section analysis




