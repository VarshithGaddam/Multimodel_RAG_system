"""
Multimodal retrieval module for querying text and image collections.

Implements cross-modal search by querying both text and image collections,
normalizing scores, and merging results with proper source attribution.
"""

from typing import Any, Dict, List
import math
import logging
from PIL import Image

from app.embeddings import embed_text, embed_clip_text
from app.storage import query_text, query_images

logger = logging.getLogger(__name__)


def _normalize_scores(scores: List[float]) -> List[float]:
	"""
	Normalize scores to [0, 1] range using min-max normalization.
	
	Args:
		scores: List of raw similarity scores
		
	Returns:
		List of normalized scores
	"""
	if not scores:
		return []
	mn = min(scores)
	mx = max(scores)
	if math.isclose(mx, mn):
		return [1.0 for _ in scores]
	return [(s - mn) / (mx - mn) for s in scores]


def _format_source_attribution(metadata: Dict[str, Any]) -> str:
	"""
	Format metadata into a human-readable source attribution string.
	
	Args:
		metadata: Document metadata dictionary
		
	Returns:
		Formatted source string
	"""
	file_type = metadata.get("file_type", "unknown")
	source_path = metadata.get("source_path", "unknown")
	
	parts = [f"Source: {source_path}", f"Type: {file_type}"]
	
	if "page" in metadata:
		parts.append(f"Page: {metadata['page']}")
	if "chunk_index" in metadata:
		parts.append(f"Chunk: {metadata['chunk_index']}")
	if "uploaded_at" in metadata:
		parts.append(f"Uploaded: {metadata['uploaded_at']}")
		
	return " | ".join(parts)


async def multimodal_query(query: str, top_k: int = 5) -> Dict[str, Any]:
	"""
	Execute a multimodal query across text and image collections.
	
	This function performs dual retrieval:
	1. Text search using text embeddings
	2. Cross-modal search using CLIP text-to-image embeddings
	
	Results are normalized, merged, and ranked by relevance score.
	
	Args:
		query: Natural language query string
		top_k: Number of top results to return
		
	Returns:
		Dict containing query string and ranked results with source attribution
	"""
	logger.info(f"Processing multimodal query: '{query}' with top_k={top_k}")
	
	# Text collection search
	text_emb = embed_text([query])[0]
	text_results = query_text(text_emb, top_k=top_k)
	logger.debug(f"Text search returned {len(text_results.get('ids', [[]])[0])} results")

	# Image collection search using CLIP text encoder
	clip_text_emb = embed_clip_text([query])[0]
	image_results = query_images(clip_text_emb, top_k=top_k)
	logger.debug(f"Image search returned {len(image_results.get('ids', [[]])[0])} results")

	merged: List[Dict[str, Any]] = []

	# Normalize distances/similarities: Chroma returns distances for cosine by default; smaller is better
	# Convert to similarity = 1 - distance for ease of merging, then normalize per modality
	text_scores_raw = []
	if text_results.get("distances"):
		text_scores_raw = [1.0 - d for d in text_results["distances"][0]]
	text_scores = _normalize_scores(text_scores_raw)

	image_scores_raw = []
	if image_results.get("distances"):
		image_scores_raw = [1.0 - d for d in image_results["distances"][0]]
	image_scores = _normalize_scores(image_scores_raw)

	# Process text results
	for i, _id in enumerate(text_results.get("ids", [[]])[0]):
		metadata = text_results.get("metadatas", [[]])[0][i] if text_results.get("metadatas") else {}
		merged.append({
			"id": _id,
			"score": text_scores[i] if i < len(text_scores) else 0.0,
			"modality": "text",
			"document": text_results.get("documents", [[]])[0][i] if text_results.get("documents") else None,
			"metadata": metadata,
			"source": _format_source_attribution(metadata),
		})

	# Process image results
	for i, _id in enumerate(image_results.get("ids", [[]])[0]):
		metadata = image_results.get("metadatas", [[]])[0][i] if image_results.get("metadatas") else {}
		merged.append({
			"id": _id,
			"score": image_scores[i] if i < len(image_scores) else 0.0,
			"modality": "image",
			"document": None,
			"metadata": metadata,
			"source": _format_source_attribution(metadata),
			"ocr_text": metadata.get("ocr_text", ""),
		})

	# Sort merged results by score desc and keep top_k
	merged.sort(key=lambda x: x["score"], reverse=True)
	final_results = merged[:top_k]
	
	logger.info(f"Returning {len(final_results)} merged results")
	return {"query": query, "results": final_results, "total_results": len(final_results)}


