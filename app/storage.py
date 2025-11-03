"""
Vector storage module using ChromaDB.

Manages persistent storage of text and image embeddings in separate collections
to maintain embedding space consistency.
"""

from typing import Any, Dict, List, Tuple
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR = "data/chroma"
TEXT_COLLECTION = "documents_text"
IMAGE_COLLECTION = "documents_image"


def get_chroma_client() -> chromadb.Client:
	"""
	Get or create a persistent ChromaDB client.
	
	Returns:
		chromadb.Client: Persistent client with anonymized telemetry disabled
	"""
	logger.debug(f"Initializing ChromaDB client at {CHROMA_PERSIST_DIR}")
	client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(anonymized_telemetry=False))
	return client


def get_collections() -> Tuple[Any, Any]:
	"""
	Get or create text and image collections.
	
	Returns:
		Tuple[Collection, Collection]: Text collection and image collection
	"""
	client = get_chroma_client()
	text = client.get_or_create_collection(name=TEXT_COLLECTION, metadata={"hnsw:space": "cosine"})
	image = client.get_or_create_collection(name=IMAGE_COLLECTION, metadata={"hnsw:space": "cosine"})
	logger.debug(f"Retrieved collections: {TEXT_COLLECTION}, {IMAGE_COLLECTION}")
	return text, image


def upsert_text(ids: List[str], embeddings, metadatas: List[Dict[str, Any]], documents: List[str]) -> None:
	"""
	Insert or update text documents in the text collection.
	
	Args:
		ids: Unique identifiers for each document chunk
		embeddings: Numpy array of embeddings
		metadatas: List of metadata dictionaries
		documents: List of text content
	"""
	text, _ = get_collections()
	logger.info(f"Upserting {len(ids)} text documents")
	text.upsert(ids=ids, embeddings=embeddings.tolist(), metadatas=metadatas, documents=documents)


def upsert_images(ids: List[str], embeddings, metadatas: List[Dict[str, Any]]) -> None:
	"""
	Insert or update images in the image collection.
	
	Args:
		ids: Unique identifiers for each image
		embeddings: Numpy array of embeddings
		metadatas: List of metadata dictionaries
	"""
	_, image = get_collections()
	logger.info(f"Upserting {len(ids)} images")
	image.upsert(ids=ids, embeddings=embeddings.tolist(), metadatas=metadatas)


def query_text(query_embedding, top_k: int = 5) -> Dict[str, Any]:
	"""
	Query the text collection for similar documents.
	
	Args:
		query_embedding: Query embedding vector
		top_k: Number of results to return
		
	Returns:
		Dict containing ids, distances, metadatas, and documents
	"""
	text, _ = get_collections()
	logger.debug(f"Querying text collection with top_k={top_k}")
	return text.query(query_embeddings=[query_embedding.tolist()], n_results=top_k)


def query_images(query_embedding, top_k: int = 5) -> Dict[str, Any]:
	"""
	Query the image collection for similar images.
	
	Args:
		query_embedding: Query embedding vector
		top_k: Number of results to return
		
	Returns:
		Dict containing ids, distances, and metadatas
	"""
	_, image = get_collections()
	logger.debug(f"Querying image collection with top_k={top_k}")
	return image.query(query_embeddings=[query_embedding.tolist()], n_results=top_k)


