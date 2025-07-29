# Round 1B: Persona-Driven Document Intelligence

## Overview

Our solution implements an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done. The system uses semantic search with ChromaDB and on-device LLM processing to deliver contextual insights.

---

## Approach

### 1\. **Document Processing Pipeline**

- **PDF Text Extraction**: Uses LangChain's PyPDFLoader to extract text from PDF documents.
- **Section Extraction**: Uses pre-computed document outlines (from Round 1A) to extract structured sections.
- **Content Processing**: Removes heading duplicates and handles multi-page section content.

### 2\. **Semantic Search & Ranking**

- **Vector Database**: ChromaDB with SentenceTransformer embeddings (`all-MiniLM-L6-v2`).
- **Query Construction**: Combines persona and job-to-be-done into semantic queries.
- **Relevance Scoring**: Uses cosine similarity to rank sections by relevance.

### 3\. **Intelligent Sub-section Analysis**

- **Content Segmentation**: Splits top sections into meaningful paragraphs.
- **LLM Refinement**: Uses Gemma 3 1B model for persona-specific text summarization.
- **Contextual Processing**: Generates refined text from the persona's perspective.

---

## Workflow

---

## Models and Libraries Used

### Core Dependencies

- **ChromaDB (0.5.23)**: Vector database for semantic search.
- **sentence-transformers (3.3.1)**: Text embeddings for similarity search.
- **langchain-community (0.3.13)**: PDF processing utilities.
- **llama-cpp-python (0.3.2)**: On-device LLM inference.

### Model Details

- **Embedding Model**: `all-MiniLM-L6-v2` (22MB) - Fast and accurate sentence embeddings.
- **LLM Model**: `google-gemma-3-1b-it-qat-q4_0-gguf-small` (\~800MB) - Quantized instruction-tuned model.
- **Total Model Size**: \~822MB (within 1GB constraint).

---

## Docker Usage

### Building the Image

```bash
docker build --platform linux/amd64 -t round1b-solution:latest .
```

### Input Preparation

Before running the container, you must prepare the `input` directory with all the necessary files in the correct format. The container expects this directory to be mounted at `/app/input`.

1.  **Create the Input Directory**: In your project root, create a directory named `input`.

2.  **Place Your Files**: Add your PDF documents and their corresponding outline JSON files into the `input` directory.

    - **PDF Files**: The raw PDF documents to be analyzed.
    - **Outline Files**: For each PDF, you must include its outline file, which is the JSON output from **Round 1A**. The naming should be consistent (e.g., `mydoc.pdf` and `mydoc_outline.json`).

3.  **Create `input.json`**: Create a main `input.json` file inside the `input` directory. This file defines the persona, the job-to-be-done, and lists the documents to be processed.

**File Structure Example:**

```
input/
├── input.json                 # Main input file with persona and job
├── E0CCG5S312.pdf             # PDF document
├── E0CCG5S312.json            # Corresponding outline from Round 1A
├── another_doc.pdf
└── another_doc_outline.json
```

**`input.json` Format:**

This file orchestrates the analysis. The `pdf_path` and `outline_path` should be the filenames of the files you placed in the `input` directory.

```json
{
  "persona": "Business Analyst",
  "job_to_be_done": "Tell the main points of Agile methodology",
  "documents": [
    {
      "pdf_path": "E0CCG5S312.pdf",
      "outline_path": "E0CCG5S312.json",
      "document_type": "Business"
    }
  ]
}
```

**Outline File (`*_outline.json`) Format:**

This file is a direct output from the Round 1A process. It contains the hierarchical structure of the document.

```json
{
  "title": "Overview  Foundation Level Extensions  ",
  "outline": [
    {
      "level": "H1",
      "text": "Revision History ",
      "page": 2
    },
    {
      "level": "H2",
      "text": "2.1 Intended Audience ",
      "page": 6
    }
  ]
}
```

### Running the Container

Once the `input` directory is set up, run the Docker container. This command mounts your local `input` and `output` directories into the container.

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  round1b-solution:latest
```

---

### Output JSON Format

```json
{
  "metadata": {
    "input_documents": ["document1.pdf"],
    "persona": "Business Analyst",
    "job_to_be_done": "Analyze market trends",
    "processing_timestamp": "2025-07-28T23:15:28.197945",
    "processing_time_seconds": 45.2,
    "total_sections_found": 15
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "page_number": 5,
      "section_title": "Market Analysis",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "document1.pdf",
      "page_number": 5,
      "section_title": "Market Analysis - Part 1",
      "refined_text": "Key market trends indicate...",
      "importance_rank": 1
    }
  ]
}
```

---

## Performance Characteristics

- **Processing Time**: \~30-50 seconds for 3-5 documents (within 60s constraint).
- **Memory Usage**: \~2-3GB RAM during peak processing.
- **Model Loading**: \~5-10 seconds initial startup time.
- **CPU Only**: Optimized for AMD64 architecture without GPU dependencies.

---

## Key Features

1.  **Generic Solution**: Handles diverse domains (research, business, education).
2.  **Persona-Aware**: Tailors content extraction to specific user roles.
3.  **Hierarchical Processing**: Section-level and sub-section-level analysis.
4.  **Offline Processing**: No internet connectivity required.
5.  **Scalable Architecture**: Batch processing with configurable parameters.

---

## Project Structure

```
├── main.py              # Docker-compatible main entry point
├── extraction.py        # PDF content extraction logic
├── processor.py         # PDF text processing utilities
├── chroma.py           # ChromaDB operations
├── dbManager.py        # Database configuration
├── llm.py              # LLM processing utilities
├── models.py           # Data models and structures
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
└── README.md          # This file
```
