# Quick Start Guide

Get the Multimodal RAG System up and running in 5 minutes.

## Prerequisites

- Python 3.9+
- pip
- Tesseract OCR (optional, for image text extraction)

## Installation

### 1. Clone and Navigate
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

This will install:
- FastAPI and Uvicorn (web framework)
- ChromaDB (vector database)
- sentence-transformers (embedding models)
- PyTorch (deep learning)
- PDF and OCR libraries

**Note:** First installation may take 5-10 minutes as it downloads embedding models (~700MB).

### 4. Install Tesseract (Optional)

**Windows:**
1. Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Skip Tesseract:** The system works without OCR, but won't extract text from images.

## Running the Server

### Start the API Server
```bash
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Access the API
- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## First Steps

### 1. Check Server Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00",
  "service": "Multimodal RAG System"
}
```

### 2. Upload a Sample Document

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@samples/text/sample1_ai_overview.txt"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/upload"
files = {'file': open('samples/text/sample1_ai_overview.txt', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Click on `POST /upload`
3. Click "Try it out"
4. Choose a file
5. Click "Execute"

### 3. Query the Document

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 5}'
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {"query": "What is machine learning?", "top_k": 5}
response = requests.post(url, json=payload)

results = response.json()
for i, result in enumerate(results['results'], 1):
    print(f"{i}. Score: {result['score']:.4f}")
    print(f"   {result['source']}")
    print(f"   {result['document'][:100]}...\n")
```

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Click on `POST /query`
3. Click "Try it out"
4. Enter your query and top_k value
5. Click "Execute"

## Run the Demo

We've included a demo script that uploads sample files and runs example queries:

```bash
python demo.py
```

This will:
1. Check server health
2. Upload sample text files
3. Run example queries
4. Display results

## Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app
```

## Common Issues

### Issue: "Cannot connect to server"
**Solution:** Make sure the server is running:
```bash
uvicorn app.main:app --reload --port 8000
```

### Issue: "Tesseract not found"
**Solution:** Either install Tesseract or set the path:
```bash
# Windows
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# macOS/Linux
export TESSERACT_CMD=/usr/local/bin/tesseract
```

Or skip OCR - the system will work without it.

### Issue: "Module not found"
**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
# Activate venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Issue: Slow first query
**Solution:** This is normal. The first query loads embedding models (~2-3 seconds). Subsequent queries are fast (~200-500ms).

### Issue: Out of memory
**Solution:** The embedding models require ~2GB RAM. Close other applications or use a machine with more memory.

## Next Steps

1. **Upload More Documents:**
   - Add your own text files to `samples/text/`
   - Add images to `samples/images/`
   - Add PDFs to `samples/pdfs/`
   - Upload via `/upload` endpoint

2. **Explore the API:**
   - Read [API_EXAMPLES.md](API_EXAMPLES.md) for detailed examples
   - Try different query types
   - Experiment with top_k values

3. **Understand the System:**
   - Read [README.md](README.md) for architecture details
   - Read [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) for design rationale
   - Check logs in `logs/app.log`

4. **Customize:**
   - Modify chunking strategy in `app/ingestion.py`
   - Adjust embedding models in `app/embeddings.py`
   - Add custom metadata fields

## Quick Reference

### Supported File Types
- Text: `.txt`
- Images: `.png`, `.jpg`, `.jpeg`
- PDFs: `.pdf` (text, images, or mixed)

### API Endpoints
- `GET /health` - Health check
- `POST /upload` - Upload document
- `POST /query` - Query documents

### Directory Structure
```
drec-ai/
├── app/              # Application code
├── data/             # Data storage
│   ├── uploads/      # Uploaded files
│   ├── extracted/    # PDF page images
│   └── chroma/       # Vector database
├── logs/             # Application logs
├── samples/          # Sample documents
└── tests/            # Unit tests
```

### Useful Commands
```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Run demo
python demo.py

# Run tests
python -m pytest tests/ -v

# Check logs
cat logs/app.log  # macOS/Linux
type logs\app.log  # Windows
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review [API_EXAMPLES.md](API_EXAMPLES.md) for usage examples
- Check logs in `logs/app.log` for errors
- Open an issue on GitHub

## What's Next?

Now that you have the system running, try:
1. Uploading different types of documents
2. Experimenting with various queries
3. Exploring the interactive Swagger UI
4. Reading the design decisions document
5. Running the unit tests

Happy searching! 🚀
