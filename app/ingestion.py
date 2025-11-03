"""
Document ingestion module for processing and storing various file types.

Handles text files, images, and PDFs with text/image/mixed content.
Extracts embeddings and stores them in ChromaDB with comprehensive metadata.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import logging

from fastapi import UploadFile, HTTPException
from PIL import Image

from app.embeddings import embed_text, embed_image
from app.storage import upsert_text, upsert_images
from app.utils.ocr_utils import ocr_image
from app.utils.pdf_utils import extract_pdf_text_per_page, extract_pdf_images

logger = logging.getLogger(__name__)

SUPPORTED_TEXT = {"text/plain"}
SUPPORTED_IMAGES = {"image/png", "image/jpeg", "image/jpg"}
SUPPORTED_PDF = {"application/pdf"}


async def process_upload(file: UploadFile) -> Dict[str, Any]:
	"""
	Process an uploaded file and store it in the vector database.
	
	Routes files to appropriate handlers based on content type:
	- Text files: paragraph-based chunking
	- Images: CLIP embeddings + OCR
	- PDFs: text extraction + page rendering for OCR
	
	Args:
		file: Uploaded file from FastAPI
		
	Returns:
		Dict containing ingestion status and metadata
		
	Raises:
		HTTPException: If file type is unsupported or processing fails
	"""
	content_type = file.content_type or ""
	filename = file.filename or f"upload_{uuid.uuid4()}"
	upload_dir = "data/uploads"
	os.makedirs(upload_dir, exist_ok=True)
	stored_path = os.path.join(upload_dir, filename)

	logger.info(f"Processing upload: {filename} (type: {content_type})")

	try:
		# Save file to disk
		with open(stored_path, "wb") as f:
			content = await file.read()
			f.write(content)
		logger.debug(f"Saved file to {stored_path} ({len(content)} bytes)")

		if content_type in SUPPORTED_TEXT or filename.lower().endswith(".txt"):
			return await _ingest_text(stored_path)
		elif content_type in SUPPORTED_IMAGES or filename.lower().endswith((".png", ".jpg", ".jpeg")):
			return await _ingest_image(stored_path)
		elif content_type in SUPPORTED_PDF or filename.lower().endswith(".pdf"):
			return await _ingest_pdf(stored_path)
		else:
			logger.warning(f"Unsupported file type: {content_type}")
			raise HTTPException(status_code=415, detail=f"Unsupported file type: {content_type}")
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error processing upload {filename}: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


async def _ingest_text(path: str) -> Dict[str, Any]:
	"""
	Ingest a plain text file with paragraph-based chunking.
	
	Args:
		path: Path to the text file
		
	Returns:
		Dict with ingestion status and document ID
	"""
	logger.info(f"Ingesting text file: {path}")
	
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		text = f.read().strip()

	if not text:
		logger.warning(f"Empty text file: {path}")
		raise HTTPException(status_code=400, detail="Empty text file")

	# Simple chunking by paragraphs
	chunks: List[str] = [c.strip() for c in text.split("\n\n") if c.strip()]
	logger.debug(f"Split text into {len(chunks)} chunks")
	
	emb = embed_text(chunks)
	doc_id = str(uuid.uuid4())
	timestamp = datetime.utcnow().isoformat()
	ids = [f"txt::{doc_id}::{i}" for i in range(len(chunks))]
	metas = [
		{
			"doc_id": doc_id,
			"file_type": "text",
			"source_path": path,
			"chunk_index": i,
			"uploaded_at": timestamp,
		}
		for i in range(len(chunks))
	]
	upsert_text(ids=ids, embeddings=emb, metadatas=metas, documents=chunks)
	logger.info(f"Successfully ingested text file with {len(chunks)} chunks, doc_id={doc_id}")
	return {"status": "ok", "ingested_chunks": len(chunks), "doc_id": doc_id}


async def _ingest_image(path: str) -> Dict[str, Any]:
	"""
	Ingest an image file with CLIP embeddings and OCR text extraction.
	
	Args:
		path: Path to the image file
		
	Returns:
		Dict with ingestion status and document ID
	"""
	logger.info(f"Ingesting image file: {path}")
	
	try:
		image = Image.open(path).convert("RGB")
		image_emb = embed_image(image)
		doc_id = str(uuid.uuid4())
		timestamp = datetime.utcnow().isoformat()
		ocr_text = ocr_image(image) or ""
		
		ids = [f"img::{doc_id}"]
		metas = [{
			"doc_id": doc_id,
			"file_type": "image",
			"source_path": path,
			"uploaded_at": timestamp,
			"ocr_text": ocr_text,
		}]
		upsert_images(ids=ids, embeddings=image_emb, metadatas=metas)
		logger.info(f"Successfully ingested image, doc_id={doc_id}, OCR chars={len(ocr_text)}")
		return {"status": "ok", "ingested_images": 1, "doc_id": doc_id, "ocr_chars": len(ocr_text)}
	except Exception as e:
		logger.error(f"Error ingesting image {path}: {e}", exc_info=True)
		raise


async def _ingest_pdf(path: str) -> Dict[str, Any]:
	"""
	Ingest a PDF file with text extraction and page rendering.
	
	Handles PDFs with:
	- Pure text content
	- Pure image content (scanned documents)
	- Mixed text and image content
	
	Args:
		path: Path to the PDF file
		
	Returns:
		Dict with ingestion status, document ID, and counts
	"""
	logger.info(f"Ingesting PDF file: {path}")
	
	doc_id = str(uuid.uuid4())
	timestamp = datetime.utcnow().isoformat()

	try:
		# Extract text per page
		pages = extract_pdf_text_per_page(path)
		text_chunks: List[str] = []
		text_metas: List[Dict[str, Any]] = []
		for page_num, page_text in pages:
			if page_text:
				# Paragraph split per page
				chunks = [c.strip() for c in page_text.split("\n\n") if c.strip()]
				for idx, chunk in enumerate(chunks):
					text_chunks.append(chunk)
					text_metas.append({
						"doc_id": doc_id,
						"file_type": "pdf_text",
						"source_path": path,
						"uploaded_at": timestamp,
						"page": page_num,
						"chunk_index": idx,
					})
		logger.debug(f"Extracted {len(text_chunks)} text chunks from PDF")

		# Extract embedded images (render pages)
		extract_dir = os.path.join("data/extracted", os.path.splitext(os.path.basename(path))[0])
		image_records = extract_pdf_images(path, extract_dir)
		image_metas: List[Dict[str, Any]] = []
		image_embeddings_list = []
		image_ids: List[str] = []
		
		for rec in image_records:
			img_path = rec["path"]
			img = Image.open(img_path).convert("RGB")
			ocr_text = ocr_image(img) or ""
			emb = embed_image(img)
			image_embeddings_list.append(emb[0])
			image_ids.append(f"pdfimg::{doc_id}::p{rec['page']}::{os.path.basename(img_path)}")
			image_metas.append({
				"doc_id": doc_id,
				"file_type": "pdf_image",
				"source_path": path,
				"uploaded_at": timestamp,
				"page": rec["page"],
				"image_path": img_path,
				"ocr_text": ocr_text,
			})
		logger.debug(f"Rendered {len(image_embeddings_list)} page images from PDF")

		# Upserts
		if text_chunks:
			text_emb = embed_text(text_chunks)
			text_ids = [f"pdftext::{doc_id}::p{m['page']}::c{m['chunk_index']}" for m in text_metas]
			upsert_text(ids=text_ids, embeddings=text_emb, metadatas=text_metas, documents=text_chunks)

		if image_embeddings_list:
			import numpy as np
			arr = np.vstack(image_embeddings_list)
			upsert_images(ids=image_ids, embeddings=arr, metadatas=image_metas)

		logger.info(f"Successfully ingested PDF, doc_id={doc_id}, text_chunks={len(text_chunks)}, images={len(image_embeddings_list)}")
		return {
			"status": "ok",
			"doc_id": doc_id,
			"text_chunks": len(text_chunks),
			"embedded_images": len(image_embeddings_list),
		}
	except Exception as e:
		logger.error(f"Error ingesting PDF {path}: {e}", exc_info=True)
		raise


