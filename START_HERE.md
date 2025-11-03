# 🚀 START HERE - Multimodal RAG System

Welcome! This is your entry point to the Multimodal RAG System.

## What is This?

A production-ready Retrieval-Augmented Generation (RAG) system that can:
- 📄 Process text documents, images, and PDFs
- 🔍 Search across all content types simultaneously
- 🎯 Return relevant results with source attribution
- ⚡ Fast queries (~200-500ms)
- 🛠️ Production-ready with logging, error handling, and tests

## Quick Navigation

### 🏃 Want to Get Started Immediately?
→ Read [QUICKSTART.md](QUICKSTART.md) (5 minutes to running system)

### 📚 Want Complete Documentation?
→ Read [README.md](README.md) (comprehensive guide)

### 💻 Want API Examples?
→ Read [API_EXAMPLES.md](API_EXAMPLES.md) (code examples)

### 🏗️ Want to Understand Design?
→ Read [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) (architecture & rationale)

### ✅ Want to See Requirements Coverage?
→ Read [ASSIGNMENT_CHECKLIST.md](ASSIGNMENT_CHECKLIST.md) (requirements tracking)

### 📋 Want Submission Summary?
→ Read [SUBMISSION_SUMMARY.md](SUBMISSION_SUMMARY.md) (executive summary)

## 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
uvicorn app.main:app --reload --port 8000

# 3. Open browser
# http://localhost:8000/docs
```

That's it! You now have a running multimodal search system.

## 2-Minute Demo

```bash
# Run the demo script
python demo.py
```

This will:
1. Check server health
2. Upload sample documents
3. Run example queries
4. Show results

## What Can It Do?

### Upload Documents
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_document.pdf"
```

### Search Everything
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

### Get Results
```json
{
  "query": "machine learning",
  "total_results": 5,
  "results": [
    {
      "score": 0.92,
      "modality": "text",
      "document": "Machine learning is...",
      "source": "Source: ai_overview.txt | Type: text"
    }
  ]
}
```

## Project Structure

```
drec-ai/
├── 📱 app/              # Application code
├── 🧪 tests/            # Unit tests
├── 📦 samples/          # Sample data
├── 💾 data/             # Storage
├── 📝 logs/             # Logs
├── 📖 README.md         # Main docs
├── 🚀 QUICKSTART.md     # Quick start
├── 💻 API_EXAMPLES.md   # API guide
├── 🏗️ DESIGN_DECISIONS.md  # Architecture
└── ▶️ demo.py           # Demo script
```

## Key Features

✅ **Multimodal Search** - Text, images, and PDFs in one query  
✅ **Smart Retrieval** - Dual embedding strategy (MiniLM + CLIP)  
✅ **Source Attribution** - Know where results came from  
✅ **Production Ready** - Logging, error handling, tests  
✅ **Well Documented** - 6 comprehensive guides  
✅ **Easy to Use** - Interactive Swagger UI  

## Technology Stack

- **Framework**: FastAPI (modern, fast, async)
- **Vector DB**: ChromaDB (persistent, efficient)
- **Embeddings**: sentence-transformers (MiniLM + CLIP)
- **PDF**: pypdf + pypdfium2 (cross-platform)
- **OCR**: Tesseract (optional, for images)

## Common Tasks

### Upload a File
1. Go to http://localhost:8000/docs
2. Click `POST /upload`
3. Click "Try it out"
4. Choose file
5. Click "Execute"

### Search Documents
1. Go to http://localhost:8000/docs
2. Click `POST /query`
3. Click "Try it out"
4. Enter query: "machine learning"
5. Set top_k: 5
6. Click "Execute"

### Run Tests
```bash
python run_tests.py
```

### Check Logs
```bash
# Windows
type logs\app.log

# macOS/Linux
cat logs/app.log
```

## Supported File Types

- 📄 **Text**: `.txt`
- 🖼️ **Images**: `.png`, `.jpg`, `.jpeg`
- 📑 **PDFs**: `.pdf` (text, images, or mixed)

## API Endpoints

- `GET /health` - Check if server is running
- `POST /upload` - Upload a document
- `POST /query` - Search documents

## Performance

- Text upload: ~100ms
- Image upload: ~500ms (with OCR)
- PDF upload: ~1-2s per page
- Query: ~200-500ms

## Need Help?

### Server won't start?
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Check if port 8000 is available
# Try a different port:
uvicorn app.main:app --reload --port 8001
```

### Can't connect?
```bash
# Make sure server is running
# Check http://localhost:8000/health
curl http://localhost:8000/health
```

### Tests failing?
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
python run_tests.py
```

### OCR not working?
OCR is optional. The system works without it, but won't extract text from images.

To install Tesseract:
- **Windows**: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## What's Next?

1. ✅ **Get it running** - Follow QUICKSTART.md
2. 📚 **Read the docs** - Understand the system
3. 🧪 **Run the demo** - See it in action
4. 💻 **Try the API** - Upload your own files
5. 🔍 **Explore queries** - Test different searches

## Documentation Index

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| [START_HERE.md](START_HERE.md) | This file - entry point | 2 min |
| [QUICKSTART.md](QUICKSTART.md) | Get running fast | 5 min |
| [README.md](README.md) | Complete documentation | 15 min |
| [API_EXAMPLES.md](API_EXAMPLES.md) | API usage examples | 10 min |
| [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) | Architecture details | 20 min |
| [ASSIGNMENT_CHECKLIST.md](ASSIGNMENT_CHECKLIST.md) | Requirements coverage | 5 min |
| [SUBMISSION_SUMMARY.md](SUBMISSION_SUMMARY.md) | Executive summary | 5 min |

## Quick Commands Reference

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Run demo
python demo.py

# Run tests
python run_tests.py

# Run tests with coverage
python run_tests.py --coverage

# Check health
curl http://localhost:8000/health

# Upload file
curl -X POST "http://localhost:8000/upload" -F "file=@file.txt"

# Query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "search term", "top_k": 5}'
```

## Architecture at a Glance

```
Upload → Process → Embed → Store → Query → Retrieve → Rank → Return
   ↓        ↓        ↓       ↓       ↓        ↓        ↓       ↓
  File   Extract  Vector  ChromaDB  Text   Results  Merge  JSON
         Text/    Models           +Image  from DB  Scores Response
         Images                    Search
```

## Sample Queries to Try

1. **Specific**: "What is machine learning?"
2. **Vague**: "artificial intelligence"
3. **Cross-modal**: "diagram showing architecture"
4. **Technical**: "Python functions and classes"
5. **Exploratory**: "cloud computing benefits"

## Success Criteria

✅ Server starts without errors  
✅ Health check returns 200 OK  
✅ Can upload text file  
✅ Can upload image  
✅ Can upload PDF  
✅ Can query and get results  
✅ Results include source attribution  
✅ Tests pass  

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Use different port: `--port 8001` |
| Module not found | Install dependencies: `pip install -r requirements.txt` |
| Tesseract not found | Install Tesseract or skip OCR |
| Slow first query | Normal - models loading (~2-3s) |
| Out of memory | Close other apps, need ~2GB RAM |

## Contact & Support

- 📖 Check documentation in this repo
- 🐛 Found a bug? Check logs in `logs/app.log`
- ❓ Have questions? Review the guides
- 💡 Want to contribute? Code is modular and extensible

## License

MIT License - See project for details

---

**Ready to start?** → Go to [QUICKSTART.md](QUICKSTART.md)

**Want details?** → Go to [README.md](README.md)

**Need examples?** → Go to [API_EXAMPLES.md](API_EXAMPLES.md)

---

*Built with ❤️ for the Multimodal RAG Assignment*
