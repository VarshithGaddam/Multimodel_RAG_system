"""
Demo script for Multimodal RAG System.

This script demonstrates the upload and query functionality of the system.
Run the server first: uvicorn app.main:app --reload --port 8000
"""

import requests
import json
import os
from pathlib import Path


BASE_URL = "http://localhost:8000"


def check_health():
	"""Check if the server is running."""
	try:
		response = requests.get(f"{BASE_URL}/health")
		if response.status_code == 200:
			print("✓ Server is running")
			print(f"  Response: {response.json()}")
			return True
		else:
			print("✗ Server returned error")
			return False
	except requests.exceptions.ConnectionError:
		print("✗ Cannot connect to server. Make sure it's running:")
		print("  uvicorn app.main:app --reload --port 8000")
		return False


def upload_file(file_path):
	"""Upload a file to the system."""
	if not os.path.exists(file_path):
		print(f"✗ File not found: {file_path}")
		return None
		
	print(f"\nUploading: {file_path}")
	
	with open(file_path, 'rb') as f:
		files = {'file': (os.path.basename(file_path), f)}
		response = requests.post(f"{BASE_URL}/upload", files=files)
		
	if response.status_code == 200:
		result = response.json()
		print(f"✓ Upload successful")
		print(f"  Doc ID: {result.get('doc_id')}")
		if 'ingested_chunks' in result:
			print(f"  Text chunks: {result['ingested_chunks']}")
		if 'embedded_images' in result:
			print(f"  Images: {result['embedded_images']}")
		if 'ocr_chars' in result:
			print(f"  OCR characters: {result['ocr_chars']}")
		return result
	else:
		print(f"✗ Upload failed: {response.status_code}")
		print(f"  Error: {response.text}")
		return None


def query_documents(query_text, top_k=5):
	"""Query the document collection."""
	print(f"\nQuerying: '{query_text}'")
	
	payload = {
		"query": query_text,
		"top_k": top_k
	}
	
	response = requests.post(f"{BASE_URL}/query", json=payload)
	
	if response.status_code == 200:
		result = response.json()
		print(f"✓ Query successful")
		print(f"  Total results: {result.get('total_results', 0)}")
		
		for i, res in enumerate(result.get('results', []), 1):
			print(f"\n  Result {i}:")
			print(f"    Score: {res['score']:.4f}")
			print(f"    Modality: {res['modality']}")
			print(f"    Source: {res.get('source', 'N/A')}")
			
			if res['modality'] == 'text' and res.get('document'):
				doc_preview = res['document'][:100] + "..." if len(res['document']) > 100 else res['document']
				print(f"    Content: {doc_preview}")
			elif res['modality'] == 'image' and res.get('ocr_text'):
				ocr_preview = res['ocr_text'][:100] + "..." if len(res['ocr_text']) > 100 else res['ocr_text']
				print(f"    OCR Text: {ocr_preview}")
				
		return result
	else:
		print(f"✗ Query failed: {response.status_code}")
		print(f"  Error: {response.text}")
		return None


def main():
	"""Run the demo."""
	print("=" * 60)
	print("Multimodal RAG System - Demo")
	print("=" * 60)
	
	# Check server health
	if not check_health():
		return
	
	print("\n" + "=" * 60)
	print("Demo 1: Upload Sample Text Files")
	print("=" * 60)
	
	# Upload sample text files
	sample_dir = Path("samples/text")
	if sample_dir.exists():
		text_files = list(sample_dir.glob("*.txt"))[:3]  # Upload first 3
		for file_path in text_files:
			upload_file(str(file_path))
	else:
		print("✗ Sample directory not found. Please create samples/text/ with .txt files")
	
	print("\n" + "=" * 60)
	print("Demo 2: Query Examples")
	print("=" * 60)
	
	# Example queries
	queries = [
		"What is machine learning?",
		"Python programming",
		"cloud computing services",
	]
	
	for query in queries:
		query_documents(query, top_k=3)
	
	print("\n" + "=" * 60)
	print("Demo 3: Upload PDF (if available)")
	print("=" * 60)
	
	# Try to upload a PDF if available
	pdf_dir = Path("data/uploads")
	if pdf_dir.exists():
		pdf_files = list(pdf_dir.glob("*.pdf"))
		if pdf_files:
			print(f"Found existing PDF: {pdf_files[0]}")
			print("(Already uploaded, skipping)")
		else:
			print("No PDF files found in data/uploads/")
	
	print("\n" + "=" * 60)
	print("Demo Complete!")
	print("=" * 60)
	print("\nNext steps:")
	print("1. Visit http://localhost:8000/docs for interactive API documentation")
	print("2. Upload your own documents via the /upload endpoint")
	print("3. Try different queries via the /query endpoint")
	print("4. Check logs/app.log for detailed logging")


if __name__ == "__main__":
	main()
