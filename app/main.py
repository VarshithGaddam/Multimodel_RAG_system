"""
FastAPI application for Multimodal RAG System.

Provides endpoints for document upload, multimodal querying, and health checks.
Supports text files, images, and PDFs with mixed content.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from datetime import datetime

from app.ingestion import process_upload
from app.retrieval import multimodal_query

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler("logs/app.log"),
		logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)

app = FastAPI(
	title="Multimodal RAG System",
	version="0.1.0",
	description="A Retrieval-Augmented Generation system for text, images, and PDFs"
)


class QueryRequest(BaseModel):
	"""Request model for document queries."""
	query: str
	top_k: int = 5


@app.on_event("startup")
async def on_startup() -> None:
	"""Initialize application on startup."""
	logger.info("Starting Multimodal RAG System")
	# Ensure data directories exist
	for path in ["data/uploads", "data/extracted", "data/chroma", "logs"]:
		os.makedirs(path, exist_ok=True)
	logger.info("Data directories initialized")


@app.get("/health")
async def health() -> dict:
	"""
	Health check endpoint.
	
	Returns:
		Dict with status and timestamp
	"""
	return {
		"status": "ok",
		"timestamp": datetime.utcnow().isoformat(),
		"service": "Multimodal RAG System"
	}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> JSONResponse:
	"""
	Upload and process a document.
	
	Supported formats:
	- Text files (.txt)
	- Images (.png, .jpg, .jpeg)
	- PDFs (.pdf) with text, images, or mixed content
	
	Args:
		file: Uploaded file
		
	Returns:
		JSONResponse with ingestion status and document ID
		
	Raises:
		HTTPException: If file type is unsupported or processing fails
	"""
	logger.info(f"Upload request received: {file.filename}")
	try:
		result = await process_upload(file)
		logger.info(f"Upload successful: {file.filename}")
		return JSONResponse(content=result)
	except HTTPException:
		raise
	except Exception as exc:
		logger.error(f"Upload failed for {file.filename}: {exc}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))


@app.post("/query")
async def query_documents(payload: QueryRequest) -> JSONResponse:
	"""
	Query documents across text and image modalities.
	
	Performs multimodal search using:
	- Text embeddings for text documents
	- CLIP embeddings for cross-modal text-to-image search
	
	Args:
		payload: Query request with query string and top_k parameter
		
	Returns:
		JSONResponse with ranked results and source attribution
		
	Raises:
		HTTPException: If query processing fails
	"""
	logger.info(f"Query request: '{payload.query}' (top_k={payload.top_k})")
	try:
		results = await multimodal_query(payload.query, top_k=payload.top_k)
		logger.info(f"Query successful, returned {results.get('total_results', 0)} results")
		return JSONResponse(content=results)
	except HTTPException:
		raise
	except Exception as exc:
		logger.error(f"Query failed: {exc}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(exc))
