"""
Unit tests for embedding generation module.
"""

import unittest
import numpy as np
from PIL import Image
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.embeddings import embed_text, embed_clip_text, embed_image, EmbeddingModels


class TestEmbeddings(unittest.TestCase):
	"""Test cases for embedding functions."""
	
	def test_embed_text_single(self):
		"""Test text embedding generation for single text."""
		texts = ["This is a test sentence."]
		embeddings = embed_text(texts)
		
		self.assertIsInstance(embeddings, np.ndarray)
		self.assertEqual(embeddings.shape[0], 1)
		self.assertGreater(embeddings.shape[1], 0)
		
	def test_embed_text_multiple(self):
		"""Test text embedding generation for multiple texts."""
		texts = ["First sentence.", "Second sentence.", "Third sentence."]
		embeddings = embed_text(texts)
		
		self.assertEqual(embeddings.shape[0], 3)
		
	def test_embed_text_normalization(self):
		"""Test that text embeddings are normalized."""
		texts = ["Test normalization"]
		embeddings = embed_text(texts)
		
		# Check if embeddings are approximately normalized (L2 norm ≈ 1)
		norm = np.linalg.norm(embeddings[0])
		self.assertAlmostEqual(norm, 1.0, places=5)
		
	def test_embed_clip_text(self):
		"""Test CLIP text embedding generation."""
		texts = ["A photo of a cat"]
		embeddings = embed_clip_text(texts)
		
		self.assertIsInstance(embeddings, np.ndarray)
		self.assertEqual(embeddings.shape[0], 1)
		
	def test_embed_image(self):
		"""Test image embedding generation."""
		# Create a simple test image
		img = Image.new('RGB', (100, 100), color='red')
		embeddings = embed_image(img)
		
		self.assertIsInstance(embeddings, np.ndarray)
		self.assertEqual(embeddings.shape[0], 1)
		self.assertGreater(embeddings.shape[1], 0)
		
	def test_embedding_models_singleton(self):
		"""Test that embedding models use singleton pattern."""
		model1 = EmbeddingModels.get_text_model()
		model2 = EmbeddingModels.get_text_model()
		
		# Should be the same instance
		self.assertIs(model1, model2)
		
	def test_different_texts_different_embeddings(self):
		"""Test that different texts produce different embeddings."""
		texts = ["Machine learning", "Artificial intelligence"]
		embeddings = embed_text(texts)
		
		# Embeddings should not be identical
		self.assertFalse(np.allclose(embeddings[0], embeddings[1]))


if __name__ == '__main__':
	unittest.main()
