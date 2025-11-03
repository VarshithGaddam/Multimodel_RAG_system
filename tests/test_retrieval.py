"""
Unit tests for retrieval module.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.retrieval import _normalize_scores, _format_source_attribution


class TestRetrieval(unittest.TestCase):
	"""Test cases for retrieval functions."""
	
	def test_normalize_scores_empty(self):
		"""Test score normalization with empty list."""
		scores = []
		normalized = _normalize_scores(scores)
		self.assertEqual(normalized, [])
		
	def test_normalize_scores_single(self):
		"""Test score normalization with single score."""
		scores = [0.5]
		normalized = _normalize_scores(scores)
		self.assertEqual(normalized, [1.0])
		
	def test_normalize_scores_range(self):
		"""Test score normalization with range of scores."""
		scores = [0.1, 0.5, 0.9]
		normalized = _normalize_scores(scores)
		
		# Check range [0, 1]
		self.assertAlmostEqual(min(normalized), 0.0, places=5)
		self.assertAlmostEqual(max(normalized), 1.0, places=5)
		
	def test_normalize_scores_identical(self):
		"""Test score normalization with identical scores."""
		scores = [0.5, 0.5, 0.5]
		normalized = _normalize_scores(scores)
		
		# All should be 1.0 when identical
		self.assertTrue(all(s == 1.0 for s in normalized))
		
	def test_format_source_attribution_text(self):
		"""Test source attribution formatting for text."""
		metadata = {
			"file_type": "text",
			"source_path": "data/uploads/test.txt",
			"chunk_index": 0,
			"uploaded_at": "2024-01-01T00:00:00"
		}
		
		attribution = _format_source_attribution(metadata)
		
		self.assertIn("test.txt", attribution)
		self.assertIn("text", attribution)
		self.assertIn("Chunk: 0", attribution)
		
	def test_format_source_attribution_pdf(self):
		"""Test source attribution formatting for PDF."""
		metadata = {
			"file_type": "pdf_text",
			"source_path": "data/uploads/document.pdf",
			"page": 5,
			"chunk_index": 2
		}
		
		attribution = _format_source_attribution(metadata)
		
		self.assertIn("document.pdf", attribution)
		self.assertIn("Page: 5", attribution)
		self.assertIn("Chunk: 2", attribution)
		
	def test_format_source_attribution_image(self):
		"""Test source attribution formatting for image."""
		metadata = {
			"file_type": "image",
			"source_path": "data/uploads/photo.jpg",
			"uploaded_at": "2024-01-01T00:00:00"
		}
		
		attribution = _format_source_attribution(metadata)
		
		self.assertIn("photo.jpg", attribution)
		self.assertIn("image", attribution)


if __name__ == '__main__':
	unittest.main()
