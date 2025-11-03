"""
Embedding generation module for text and image data.

This module provides singleton access to embedding models and functions
to generate embeddings for text and images using sentence-transformers.
"""

from typing import List, Union, Optional
from PIL import Image
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingModels:
	"""
	Singleton manager for embedding models.
	
	Maintains lazy-loaded instances of text and CLIP models to avoid
	redundant model loading and reduce memory footprint.
	"""
	_text_model: Optional[SentenceTransformer] = None
	_clip_model: Optional[SentenceTransformer] = None

	@classmethod
	def get_text_model(cls) -> SentenceTransformer:
		"""
		Get or initialize the text embedding model.
		
		Returns:
			SentenceTransformer: all-MiniLM-L6-v2 model for text embeddings
		"""
		if cls._text_model is None:
			logger.info("Loading text embedding model: all-MiniLM-L6-v2")
			cls._text_model = SentenceTransformer("all-MiniLM-L6-v2")
		return cls._text_model

	@classmethod
	def get_clip_model(cls) -> SentenceTransformer:
		"""
		Get or initialize the CLIP model for multimodal embeddings.
		
		Returns:
			SentenceTransformer: clip-ViT-B-32 model for text and image embeddings
		"""
		if cls._clip_model is None:
			logger.info("Loading CLIP model: clip-ViT-B-32")
			cls._clip_model = SentenceTransformer("clip-ViT-B-32")
		return cls._clip_model


def embed_text(texts: List[str]) -> np.ndarray:
	"""
	Generate embeddings for text using the text-specific model.
	
	Args:
		texts: List of text strings to embed
		
	Returns:
		np.ndarray: Normalized embeddings of shape (len(texts), embedding_dim)
	"""
	model = EmbeddingModels.get_text_model()
	logger.debug(f"Generating text embeddings for {len(texts)} texts")
	embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
	return embeddings


def embed_clip_text(texts: List[str]) -> np.ndarray:
	"""
	Generate CLIP embeddings for text (for cross-modal retrieval).
	
	Args:
		texts: List of text strings to embed
		
	Returns:
		np.ndarray: Normalized CLIP embeddings of shape (len(texts), embedding_dim)
	"""
	model = EmbeddingModels.get_clip_model()
	logger.debug(f"Generating CLIP text embeddings for {len(texts)} texts")
	embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
	return embeddings


def embed_image(image: Union[Image.Image, str]) -> np.ndarray:
	"""
	Generate CLIP embeddings for an image.
	
	Args:
		image: PIL Image object or path to image file
		
	Returns:
		np.ndarray: Normalized CLIP embeddings of shape (1, embedding_dim)
	"""
	model = EmbeddingModels.get_clip_model()
	logger.debug(f"Generating image embedding")
	# model.encode supports PIL Image directly for CLIP models
	embeddings = model.encode([image], normalize_embeddings=True, convert_to_numpy=True)
	return embeddings


