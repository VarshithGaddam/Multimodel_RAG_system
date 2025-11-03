"""
Unit tests for storage module.
"""

import unittest
import numpy as np
import sys
import os
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.storage import (
	get_chroma_client,
	get_collections,
	upsert_text,
	upsert_images,
	query_text,
	query_images
)


class TestStorage(unittest.TestCase):
	"""Test cases for storage functions."""
	
	@classmethod
	def setUpClass(cls):
		"""Set up test database."""
		# Use a test-specific directory
		import app.storage as storage
		storage.CHROMA_PERSIST_DIR = "data/chroma_test"
		
	@classmethod
	def tearDownClass(cls):
		"""Clean up test database."""
		if os.path.exists("data/chroma_test"):
			shutil.rmtree("data/chroma_test")
			
	def test_get_chroma_client(self):
		"""Test ChromaDB client initialization."""
		client = get_chroma_client()
		self.assertIsNotNone(client)
		
	def test_get_collections(self):
		"""Test collection retrieval."""
		text_col, image_col = get_collections()
		self.assertIsNotNone(text_col)
		self.assertIsNotNone(image_col)
		
	def test_upsert_and_query_text(self):
		"""Test text upsert and query operations."""
		# Create test embeddings
		embeddings = np.random.rand(2, 384).astype(np.float32)
		embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
		
		ids = ["test_text_1", "test_text_2"]
		documents = ["First test document", "Second test document"]
		metadatas = [
			{"doc_id": "doc1", "file_type": "text"},
			{"doc_id": "doc2", "file_type": "text"}
		]
		
		# Upsert
		upsert_text(ids, embeddings, metadatas, documents)
		
		# Query
		query_emb = embeddings[0]
		results = query_text(query_emb, top_k=2)
		
		self.assertIn("ids", results)
		self.assertGreater(len(results["ids"][0]), 0)
		
	def test_upsert_and_query_images(self):
		"""Test image upsert and query operations."""
		# Create test embeddings
		embeddings = np.random.rand(2, 512).astype(np.float32)
		embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
		
		ids = ["test_img_1", "test_img_2"]
		metadatas = [
			{"doc_id": "img1", "file_type": "image"},
			{"doc_id": "img2", "file_type": "image"}
		]
		
		# Upsert
		upsert_images(ids, embeddings, metadatas)
		
		# Query
		query_emb = embeddings[0]
		results = query_images(query_emb, top_k=2)
		
		self.assertIn("ids", results)
		self.assertGreater(len(results["ids"][0]), 0)


if __name__ == '__main__':
	unittest.main()
