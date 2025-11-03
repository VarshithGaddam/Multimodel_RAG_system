# Design Decisions and Trade-offs

## Overview
This document details the key architectural and implementation decisions made during the development of the Multimodal RAG System, along with their rationale and trade-offs.

## 1. Architecture Decisions

### 1.1 Separate Collections for Text and Images

**Decision:** Use two separate ChromaDB collections with different embedding models.

**Rationale:**
- Text embeddings (MiniLM, 384-dim) and image embeddings (CLIP, 512-dim) have different dimensionalities
- Mixing embeddings in a single collection would require padding or truncation, losing information
- Separate collections allow independent optimization and scaling
- Enables specialized retrieval strategies per modality

**Trade-offs:**
- **Pro:** Better retrieval quality, cleaner architecture, independent scaling
- **Con:** Requires merging results from two sources, slightly more complex querying
- **Con:** Duplicate metadata storage

**Alternatives Considered:**
- Single collection with unified embedding: Rejected due to dimensionality mismatch
- Separate databases: Rejected as overkill for current scale

### 1.2 Dual Embedding Strategy

**Decision:** Use MiniLM-L6-v2 for text and CLIP-ViT-B-32 for multimodal.

**Rationale:**
- MiniLM is optimized for semantic text similarity (trained on sentence pairs)
- CLIP provides cross-modal capabilities (text-to-image search)
- Both models are open-source, well-maintained, and production-ready
- Reasonable model sizes (MiniLM: ~80MB, CLIP: ~600MB)

**Trade-offs:**
- **Pro:** Best-in-class retrieval for each modality
- **Pro:** Cross-modal search capabilities
- **Con:** Higher memory usage (~700MB for both models)
- **Con:** Longer initial startup time for model loading

**Alternatives Considered:**
- Single CLIP model for everything: Rejected as CLIP text-to-text is inferior to specialized models
- Larger models (e.g., BERT-large): Rejected due to size/speed trade-off

### 1.3 FastAPI Framework

**Decision:** Use FastAPI for the REST API.

**Rationale:**
- Modern, fast, and async-capable
- Automatic OpenAPI documentation (Swagger UI)
- Type hints and Pydantic validation
- Excellent developer experience

**Trade-offs:**
- **Pro:** Fast development, great documentation, type safety
- **Pro:** Built-in async support for future scaling
- **Con:** Slightly steeper learning curve than Flask

**Alternatives Considered:**
- Flask: Rejected as FastAPI provides better async support and auto-documentation
- Django: Rejected as too heavyweight for this use case

## 2. Data Processing Decisions

### 2.1 Paragraph-Based Chunking

**Decision:** Split text documents by double newlines (paragraphs).

**Rationale:**
- Preserves semantic coherence (paragraphs are natural semantic units)
- Simple and reliable across different document types
- No complex sentence boundary detection needed
- Works well with embedding models trained on sentence/paragraph-level data

**Trade-offs:**
- **Pro:** Simple, fast, semantically coherent
- **Pro:** No mid-sentence splits
- **Con:** Variable chunk sizes (some paragraphs are very long/short)
- **Con:** May miss cross-paragraph context

**Alternatives Considered:**
- Fixed-size chunking with overlap: Rejected due to potential mid-sentence splits
- Sentence-level chunking: Rejected as too granular, loses context
- Semantic chunking (LLM-based): Rejected due to complexity and latency

### 2.2 PDF Page Rendering

**Decision:** Render each PDF page as an image using pypdfium2.

**Rationale:**
- Handles all PDF types: text-only, image-only, and mixed
- Enables OCR on scanned documents
- Captures visual elements (charts, diagrams) that text extraction misses
- pypdfium2 is pure Python, works reliably on Windows without native dependencies
- 2x scale provides good OCR accuracy without excessive file sizes

**Trade-offs:**
- **Pro:** Comprehensive content capture, handles all PDF types
- **Pro:** No native dependencies, cross-platform
- **Con:** Higher storage requirements (~500KB per page)
- **Con:** Slower processing (~1-2s per page)

**Alternatives Considered:**
- Text extraction only: Rejected as misses visual content
- pdf2image with Poppler: Rejected due to native dependency issues on Windows
- PyMuPDF: Rejected due to licensing concerns (AGPL)

### 2.3 OCR with Graceful Degradation

**Decision:** Use Tesseract OCR with graceful fallback if unavailable.

**Rationale:**
- Tesseract is industry-standard, open-source, and accurate
- Not all deployments may have Tesseract installed
- System should remain functional without OCR (degraded mode)
- OCR is an enhancement, not a core requirement

**Trade-offs:**
- **Pro:** Best-effort OCR without breaking system
- **Pro:** Flexible deployment options
- **Con:** Silent degradation may confuse users
- **Con:** Requires external dependency for full functionality

**Alternatives Considered:**
- Cloud OCR APIs (Google Vision, AWS Textract): Rejected due to cost and privacy concerns
- Require Tesseract: Rejected as too restrictive for deployment

## 3. Retrieval Decisions

### 3.1 Score Normalization Strategy

**Decision:** Min-max normalization per modality before merging.

**Rationale:**
- Different embedding models produce different distance scales
- Cosine distances from MiniLM and CLIP are not directly comparable
- Min-max normalization to [0, 1] provides fair comparison
- Per-modality normalization preserves relative ranking within each modality

**Trade-offs:**
- **Pro:** Fair cross-modal comparison
- **Pro:** Prevents one modality from dominating results
- **Con:** Normalization depends on result set (not absolute scores)
- **Con:** Small result sets may have skewed normalization

**Alternatives Considered:**
- No normalization: Rejected as CLIP scores would dominate
- Z-score normalization: Rejected as assumes normal distribution
- Learned score fusion: Rejected due to complexity and need for training data

### 3.2 Result Merging Strategy

**Decision:** Merge results from both collections, sort by normalized score, return top-k.

**Rationale:**
- Simple and effective for most queries
- Allows both modalities to contribute to results
- User gets best results regardless of modality
- Transparent scoring for debugging

**Trade-offs:**
- **Pro:** Simple, transparent, effective
- **Pro:** Balanced representation of modalities
- **Con:** May return all text or all images if one modality dominates
- **Con:** No diversity enforcement

**Alternatives Considered:**
- Interleaved results (alternating modalities): Rejected as may return lower-quality results
- Separate results per modality: Rejected as requires client-side merging
- Weighted fusion: Rejected as requires query-type classification

### 3.3 Source Attribution Format

**Decision:** Include formatted source string in each result.

**Rationale:**
- Users need to know where results came from
- Formatted string is immediately usable in UI
- Includes key metadata: source path, file type, page/chunk info
- Metadata dict also included for programmatic access

**Trade-offs:**
- **Pro:** User-friendly, immediately usable
- **Pro:** Supports citation and verification
- **Con:** Slight redundancy with metadata dict
- **Con:** Fixed format may not suit all use cases

## 4. Implementation Decisions

### 4.1 Singleton Pattern for Models

**Decision:** Use class-level caching for embedding models.

**Rationale:**
- Models are expensive to load (~2-3 seconds, ~700MB memory)
- Models are stateless and thread-safe
- Single instance per model is sufficient for all requests
- Lazy loading delays initialization until first use

**Trade-offs:**
- **Pro:** Fast subsequent requests, low memory usage
- **Pro:** Lazy loading reduces startup time
- **Con:** First request per model is slower
- **Con:** Global state (though read-only)

**Alternatives Considered:**
- Load models on startup: Rejected due to slow startup
- Per-request model loading: Rejected due to extreme latency
- Model server (separate process): Rejected as overkill for current scale

### 4.2 Synchronous Processing

**Decision:** Use synchronous processing for uploads and queries.

**Rationale:**
- Simpler implementation and debugging
- Sufficient for current scale (< 1000 documents)
- FastAPI supports async, easy to migrate later
- Blocking operations (OCR, PDF rendering) are CPU-bound anyway

**Trade-offs:**
- **Pro:** Simple, easy to debug, sufficient for current scale
- **Pro:** Easier error handling
- **Con:** Blocks request thread during processing
- **Con:** Limited concurrency for uploads

**Future Enhancement:**
- Async processing with task queue (Celery, RQ) for large-scale deployments

### 4.3 Comprehensive Logging

**Decision:** Implement structured logging throughout the application.

**Rationale:**
- Essential for debugging and monitoring
- Tracks document processing pipeline
- Helps identify performance bottlenecks
- Provides audit trail for uploads and queries
- Logs to both file and console for flexibility

**Trade-offs:**
- **Pro:** Excellent observability and debugging
- **Pro:** Production-ready monitoring
- **Con:** Slight performance overhead
- **Con:** Log files can grow large

**Implementation:**
- INFO level for key events (uploads, queries)
- DEBUG level for detailed processing steps
- ERROR level with stack traces for failures

## 5. Storage Decisions

### 5.1 ChromaDB Persistent Storage

**Decision:** Use ChromaDB with persistent storage.

**Rationale:**
- Open-source, lightweight, easy to deploy
- Built-in vector similarity search
- Persistent storage eliminates re-indexing on restart
- Supports metadata filtering
- Good performance for < 1M documents

**Trade-offs:**
- **Pro:** Simple deployment, no separate database server
- **Pro:** Good performance for current scale
- **Con:** Limited scalability compared to Pinecone/Weaviate
- **Con:** No built-in replication or clustering

**Alternatives Considered:**
- Pinecone: Rejected due to cost and cloud dependency
- Weaviate: Rejected as overkill for current scale
- FAISS: Rejected due to lack of metadata support

### 5.2 Metadata Schema

**Decision:** Store comprehensive metadata with each document.

**Rationale:**
- Enables source attribution and citation
- Supports filtering and faceted search (future)
- Tracks document lineage (page, chunk, upload time)
- Facilitates debugging and auditing

**Metadata Fields:**
- `doc_id`: Unique document identifier
- `file_type`: Document type (text, image, pdf_text, pdf_image)
- `source_path`: Original file path
- `uploaded_at`: ISO timestamp
- `page`: Page number (for PDFs)
- `chunk_index`: Chunk number (for text)
- `ocr_text`: Extracted text (for images)
- `image_path`: Rendered image path (for PDF pages)

## 6. Testing Decisions

### 6.1 Unit Testing Strategy

**Decision:** Focus on unit tests for core functions, not integration tests.

**Rationale:**
- Unit tests are fast and reliable
- Core functions (normalization, attribution) are pure and easy to test
- Integration tests require running server and models (slow, flaky)
- Manual testing via Swagger UI for end-to-end validation

**Coverage:**
- Embedding generation and normalization
- Score normalization and merging
- Source attribution formatting
- Storage operations (with test database)

**Trade-offs:**
- **Pro:** Fast, reliable, easy to run
- **Pro:** Good coverage of core logic
- **Con:** Doesn't test full end-to-end flow
- **Con:** Doesn't catch integration issues

**Future Enhancement:**
- Add integration tests with test fixtures
- Add performance benchmarks

## 7. Performance Considerations

### 7.1 Current Performance Characteristics

**Measured Performance:**
- Text upload: ~100ms per document
- Image upload: ~500ms per image (including OCR)
- PDF upload: ~1-2s per page (text + rendering + OCR)
- Query: ~200-500ms for top-5 results

**Bottlenecks:**
1. PDF page rendering (pypdfium2)
2. OCR processing (Tesseract)
3. Embedding generation (model inference)

### 7.2 Optimization Strategies Implemented

1. **Model Caching:** Singleton pattern for embedding models
2. **Batch Embedding:** Process multiple chunks in single call
3. **Normalized Embeddings:** Pre-normalized for faster cosine similarity
4. **Persistent Storage:** No re-indexing on restart

### 7.3 Future Optimizations

1. **Async Processing:** Task queue for uploads
2. **Caching Layer:** Redis for frequent queries
3. **Batch Uploads:** Process multiple files in parallel
4. **Model Quantization:** Reduce model size and inference time
5. **GPU Acceleration:** Use CUDA for embedding generation

## 8. Security Considerations

### 8.1 Current Security Measures

1. **File Type Validation:** Whitelist of supported formats
2. **Error Handling:** No sensitive information in error messages
3. **Input Validation:** Pydantic models for request validation
4. **Graceful Degradation:** System remains functional on errors

### 8.2 Future Security Enhancements

1. **File Size Limits:** Prevent DoS via large uploads
2. **Rate Limiting:** Prevent abuse of API endpoints
3. **Authentication:** API keys or OAuth for access control
4. **Content Filtering:** Detect and block malicious content
5. **Encryption:** Encrypt sensitive documents at rest

## 9. Scalability Roadmap

### Current Scale
- **Documents:** 1,000s
- **Queries:** 10s per second
- **Storage:** GBs

### Future Scale Targets
- **Documents:** 100,000s
- **Queries:** 100s per second
- **Storage:** TBs

### Scaling Strategy
1. **Phase 1 (Current):** Single-server deployment
2. **Phase 2:** Async processing, caching, pagination
3. **Phase 3:** Distributed vector database (Weaviate/Milvus)
4. **Phase 4:** Microservices architecture, load balancing

## Conclusion

The design decisions prioritize simplicity, reliability, and developer experience while maintaining production-ready quality. The architecture is modular and extensible, allowing for future enhancements without major refactoring. Trade-offs favor current scale and ease of deployment over premature optimization.
