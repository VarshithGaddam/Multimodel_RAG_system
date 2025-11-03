# Multimodal RAG System

A production-ready Retrieval-Augmented Generation system that processes and queries multiple data formats including text documents, images, and PDFs with mixed content. Built with FastAPI and ChromaDB for efficient multimodal search.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Sample Queries](#sample-queries)
- [Design Decisions](#design-decisions)
- [Testing](#testing)
- [Performance](#performance)

## Features

### Core Capabilities
- **Multimodal Ingestion**: Process text files (`.txt`), images (`.png`, `.jpg`, `.jpeg`), and PDFs with text, images, or mixed content
- **Advanced PDF Processing**: Extract text per page, render pages as images, and maintain document structure
- **OCR Integration**: Extract text from images and scanned PDFs using Tesseract
- **Vector Storage**: Persistent ChromaDB storage with separate collections for text and images
- **Dual Embedding Models**:
  - Text: `all-MiniLM-L6-v2` (384 dimensions)
  - Multimodal: `clip-ViT-B-32` (512 dimensions) for cross-modal retrieval
- **Smart Retrieval**: Multimodal query processing with score normalization and result merging
- **Source Attribution**: Comprehensive metadata tracking with formatted source citations
- **Comprehensive Logging**: Structured logging to both file and console

### Technical Features
- RESTful API with FastAPI
- Automatic chunking strategies (paragraph-based for text)
- Normalized relevance scores
- Error handling and graceful degradation
- Modular, well-documented codebase

## Architecture

### System Overview
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Server              │
│  ┌──────────┐      ┌─────────────┐ │
│  │  Upload  │      │    Query    │ │
│  │ Endpoint │      │  Endpoint   │ │
│  └────┬─────┘      └──────┬──────┘ │
└───────┼────────────────────┼────────┘
        │                    │
        ▼                    ▼
┌──────────────┐      ┌──────────────┐
│  Ingestion   │      │  Retrieval   │
│    Module    │      │    Module    │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────────────────────────┐
│      Embedding Models            │
│  ┌────────────┐  ┌─────────────┐│
│  │ MiniLM-L6  │  │  CLIP ViT   ││
│  └────────────┘  └─────────────┘│
└──────────────┬───────────────────┘
               │
               ▼
        ┌─────────────┐
        │  ChromaDB   │
        │  ┌────┐ ┌──┐│
        │  │Text│ │Im││
        │  └────┘ └──┘│
        └─────────────┘
```

### Module Structure
```
app/
├── main.py              # FastAPI application and endpoints
├── ingestion.py         # Document processing and storage
├── retrieval.py         # Multimodal query and result merging
├── embeddings.py        # Embedding model management
├── storage.py           # ChromaDB interface
└── utils/
    ├── pdf_utils.py     # PDF text/image extraction
    └── ocr_utils.py     # Tesseract OCR wrapper
```

### Data Flow

**Upload Flow:**
1. Client uploads file via `/upload` endpoint
2. File saved to `data/uploads/`
3. Content type detection and routing
4. Processing based on file type:
   - **Text**: Paragraph-based chunking → Text embeddings → Store in text collection
   - **Image**: CLIP embeddings + OCR → Store in image collection
   - **PDF**: Text extraction + page rendering → Both collections
5. Return document ID and ingestion stats

**Query Flow:**
1. Client sends query via `/query` endpoint
2. Generate text embedding (MiniLM) for text search
3. Generate CLIP text embedding for image search
4. Query both collections in parallel
5. Normalize scores per modality
6. Merge and rank results
7. Format with source attribution
8. Return top-k results

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Tesseract OCR (for image text extraction)

### 1. Clone Repository
```bash
git clone <repository-url>
cd drec-ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**Windows:**
- Download installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Install and add to PATH, or set environment variable:
  ```bash
  set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
  ```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

## API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00",
  "service": "Multimodal RAG System"
}
```

#### `POST /upload`
Upload and process a document.

**Supported Formats:**
- Text: `.txt`
- Images: `.png`, `.jpg`, `.jpeg`
- PDFs: `.pdf` (text, images, or mixed)

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "ok",
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "text_chunks": 15,
  "embedded_images": 3
}
```

#### `POST /query`
Query documents across modalities.

**Request:**
```json
{
  "query": "machine learning algorithms",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "machine learning algorithms",
  "total_results": 5,
  "results": [
    {
      "id": "txt::doc-id::0",
      "score": 0.95,
      "modality": "text",
      "document": "Machine learning is a subset of AI...",
      "metadata": {
        "doc_id": "doc-id",
        "file_type": "text",
        "source_path": "data/uploads/ai_overview.txt",
        "chunk_index": 0
      },
      "source": "Source: data/uploads/ai_overview.txt | Type: text | Chunk: 0"
    }
  ]
}
```

## Sample Queries

### Example 1: Specific Factual Query
```json
{
  "query": "What is deep learning?",
  "top_k": 3
}
```
**Expected Results:** Text chunks explaining deep learning concepts, neural networks, and related topics.

### Example 2: Vague/Exploratory Query
```json
{
  "query": "cloud computing",
  "top_k": 5
}
```
**Expected Results:** Mixed results about cloud services, deployment models, and infrastructure.

### Example 3: Cross-Modal Query
```json
{
  "query": "diagram showing data flow",
  "top_k": 5
}
```
**Expected Results:** Images containing diagrams, charts, or visualizations, plus related text descriptions.

### Example 4: Technical Query
```json
{
  "query": "Python programming functions and classes",
  "top_k": 5
}
```
**Expected Results:** Code examples, documentation, and explanations about Python OOP.

## Design Decisions

### 1. Separate Collections for Text and Images
**Decision:** Use two ChromaDB collections with different embedding models.

**Rationale:**
- Text and image embeddings have different dimensionalities (384 vs 512)
- Maintains embedding space consistency
- Allows independent optimization of each modality
- Enables parallel querying for better performance

**Trade-off:** Requires merging and normalizing results from two sources, but provides better retrieval quality.

### 2. Dual Embedding Strategy
**Decision:** Use MiniLM for text-to-text and CLIP for cross-modal retrieval.

**Rationale:**
- MiniLM is optimized for semantic text similarity
- CLIP enables text-to-image search through shared embedding space
- Provides both specialized and cross-modal capabilities

**Trade-off:** Higher memory usage (two models), but significantly better retrieval accuracy.

### 3. Paragraph-Based Chunking
**Decision:** Split text documents by double newlines (paragraphs).

**Rationale:**
- Preserves semantic coherence
- Simple and reliable across different document types
- Balances chunk size for embedding quality

**Alternative Considered:** Fixed-size chunking with overlap was considered but rejected due to potential mid-sentence splits.

### 4. PDF Page Rendering
**Decision:** Render each PDF page as an image using pypdfium2.

**Rationale:**
- Handles scanned PDFs and image-heavy documents
- Enables OCR on all content
- Works reliably on Windows without native dependencies
- Captures visual elements that text extraction misses

**Trade-off:** Higher storage requirements, but ensures no content is missed.

### 5. Score Normalization
**Decision:** Normalize scores per modality before merging.

**Rationale:**
- Different embedding models produce different distance scales
- Ensures fair comparison between text and image results
- Prevents one modality from dominating results

**Implementation:** Min-max normalization to [0, 1] range per modality.

### 6. Comprehensive Logging
**Decision:** Implement structured logging throughout the application.

**Rationale:**
- Essential for debugging and monitoring
- Tracks document processing pipeline
- Helps identify performance bottlenecks
- Provides audit trail for uploads and queries

### 7. Graceful OCR Degradation
**Decision:** Continue processing if Tesseract is unavailable.

**Rationale:**
- System remains functional without OCR
- Prevents deployment issues
- OCR is enhancement, not requirement

## Testing

### Running Unit Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_embeddings.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Test Coverage
- `test_embeddings.py`: Embedding generation and normalization
- `test_storage.py`: ChromaDB operations and persistence
- `test_retrieval.py`: Score normalization and source attribution

### Manual Testing
Use the interactive Swagger UI at `http://localhost:8000/docs` to:
1. Upload sample documents from `samples/` directory
2. Test various query types
3. Verify response formats and scores

## Performance

### Benchmarks
- **Upload Processing**: 
  - Text: ~100ms per document
  - Images: ~500ms per image (including OCR)
  - PDFs: ~1-2s per page (text extraction + rendering)
  
- **Query Response Time**: 
  - Average: ~200-500ms for top-5 results
  - Includes dual embedding generation and collection queries

### Optimization Strategies
1. **Model Caching**: Singleton pattern for embedding models
2. **Batch Processing**: Process multiple chunks in single embedding call
3. **Persistent Storage**: ChromaDB persistence eliminates re-indexing
4. **Normalized Embeddings**: Pre-normalized for faster cosine similarity

### Scalability Considerations
- **Current**: Suitable for 1000s of documents
- **Bottlenecks**: PDF rendering, OCR processing
- **Future**: Add async processing, caching layer, and pagination

## Sample Data

The `samples/` directory contains example documents:
- `samples/text/`: 5 text files covering AI, Python, Data Science, Cloud Computing, and Web Development
- `samples/images/`: Upload your own images for testing
- `samples/pdfs/`: Upload your own PDFs for testing

Upload these via the `/upload` endpoint to populate the database.

## Future Enhancements

### Planned Features
- [ ] Hybrid search combining dense and sparse (BM25) retrieval
- [ ] Reranking with cross-encoder models
- [ ] Query expansion and reformulation
- [ ] Caching layer for frequent queries
- [ ] Batch upload endpoint
- [ ] Additional file formats (DOCX, XLSX, PPTX)
- [ ] Simple web UI for testing
- [ ] Conversation memory for multi-turn queries
- [ ] Document summarization
- [ ] Guardrails for content filtering
- [ ] LLM traceability and observability
- [ ] Async processing with task queue
- [ ] Pagination for large result sets

## License
MIT

## Contributing
Contributions welcome! Please open an issue or submit a pull request.

## Contact
For questions or issues, please open a GitHub issue.


