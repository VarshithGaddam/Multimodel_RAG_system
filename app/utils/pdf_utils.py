"""
PDF processing utilities for text and image extraction.

Handles extraction of text content and rendering of PDF pages as images
for OCR processing.
"""

from typing import List, Tuple, Dict
import os
from io import BytesIO
import logging

from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image

logger = logging.getLogger(__name__)


def extract_pdf_text_per_page(pdf_path: str) -> List[Tuple[int, str]]:
	"""
	Extract text content from each page of a PDF.
	
	Args:
		pdf_path: Path to the PDF file
		
	Returns:
		List of tuples containing (page_number, text_content)
	"""
	pages: List[Tuple[int, str]] = []
	try:
		reader = PdfReader(pdf_path)
		logger.info(f"Extracting text from {len(reader.pages)} pages in {pdf_path}")
		for idx, page in enumerate(reader.pages, start=1):
			text = page.extract_text() or ""
			pages.append((idx, text.strip()))
		logger.debug(f"Extracted text from {len(pages)} pages")
	except Exception as e:
		logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
		raise
	return pages


def extract_pdf_images(pdf_path: str, output_dir: str) -> List[Dict]:
	"""
	Render each PDF page as an image for OCR processing.
	
	This approach is robust on Windows and avoids native builds by using
	pypdfium2 to render pages at 2x scale for better OCR accuracy.
	
	Args:
		pdf_path: Path to the PDF file
		output_dir: Directory to save rendered page images
		
	Returns:
		List of dictionaries containing page number and image path
	"""
	os.makedirs(output_dir, exist_ok=True)
	records: List[Dict] = []
	try:
		pdf = pdfium.PdfDocument(pdf_path)
		logger.info(f"Rendering {len(pdf)} pages from {pdf_path} as images")
		for page_index in range(len(pdf)):
			page = pdf[page_index]
			bitmap = page.render(scale=2.0)  # reasonable scale for OCR
			pil_image: Image.Image = bitmap.to_pil().convert("RGB")
			filename = f"page{page_index + 1}.png"
			out_path = os.path.join(output_dir, filename)
			pil_image.save(out_path)
			records.append({
				"page": page_index + 1,
				"path": out_path,
			})
		logger.debug(f"Rendered {len(records)} page images to {output_dir}")
	except Exception as e:
		logger.error(f"Error rendering PDF pages from {pdf_path}: {e}")
		raise
	return records
