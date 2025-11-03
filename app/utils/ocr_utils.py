"""
OCR utilities using Tesseract for text extraction from images.

Provides graceful fallback when Tesseract is not available.
"""

from typing import Optional
import os
import logging
from PIL import Image
import pytesseract
from pytesseract import TesseractNotFoundError

logger = logging.getLogger(__name__)

# Allow optional override of Tesseract path via env var TESSERACT_CMD
_tess_cmd = os.getenv("TESSERACT_CMD")
if _tess_cmd:
	pytesseract.pytesseract.tesseract_cmd = _tess_cmd
	logger.info(f"Using Tesseract from: {_tess_cmd}")


def ocr_image(image: Image.Image, lang: str = "eng") -> str:
	"""
	Extract text from an image using Tesseract OCR.
	
	Args:
		image: PIL Image object to process
		lang: Language code for OCR (default: "eng")
		
	Returns:
		Extracted text string, or empty string if OCR fails
	"""
	try:
		text = pytesseract.image_to_string(image, lang=lang)
		extracted = text.strip()
		logger.debug(f"OCR extracted {len(extracted)} characters")
		return extracted
	except TesseractNotFoundError:
		logger.warning("Tesseract not found; proceeding without OCR text")
		return ""
	except Exception as e:
		logger.error(f"OCR error: {e}")
		return ""
