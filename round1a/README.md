# PDF Outline Extractor - Round 1A Solution

## Approach

Our solution uses an ML approach to extract structured outlines from PDF documents. The system combines text extraction, feature engineering, and classification to identify document titles and hierarchical headings (H1, H2, H3).

### Key Components

1. **Text Extraction (`extract.py`)**

   - Uses PyMuPDF to extract text with positional and formatting information
   - Implements multiprocessing for faster processing of large documents
   - Captures font information, bounding boxes, and page positions

2. **Feature Engineering (`parser.py`)**

   - Groups text snippets into logical lines based on vertical positioning
   - Engineers features including:
     - Font size analysis (relative to document modal font size)
     - Text formatting (bold, all caps, numbering patterns)
     - Spatial positioning (centering, spacing)
     - Content characteristics (length, patterns)

3. **Classification**
   - Uses a pre-trained Random Forest classifier to predict text line types
   - Categories: Title, H1, H2, H3, and regular text
   - Features are standardized and processed through scikit-learn pipeline

### Models and Libraries Used

- **PyMuPDF**: High-performance PDF text extraction
- **scikit-learn**: Random Forest classifier and preprocessing
- **pandas**: Data manipulation and feature engineering
- **joblib**: Model serialization and loading

## How to Build and Run

### Building the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-outline-extractor:v1 .
```

### Running the Solution

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:v1
```

### Expected Behavior

- The container automatically processes all PDF files in `/app/input`
- For each `filename.pdf`, generates `filename.json` in `/app/output`
- Output follows the specified JSON format with title and hierarchical outline

### File Structure

```
/
├── Dockerfile
├── requirements.txt
├── main.py                 # Entry point for Docker execution
├── extract.py             # PDF text extraction with multiprocessing
├── parser.py              # Feature engineering and ML classification
├── random_forest_model.pkl # Pre-trained classifier
├── label_encoder.pkl      # Label encoding for categories
└── README.md             # This file
```

## Performance Characteristics

- **Speed**: Typically processes 50-page PDFs in under 10 seconds
- **Memory**: Efficient processing with multiprocessing optimization
- **Model Size**: ~200MB total including dependencies
- **Accuracy**: Trained on diverse document types for robust heading detection
- **Offline**: No external API dependencies
