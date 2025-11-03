# API Examples and Usage Guide

This document provides comprehensive examples of using the Multimodal RAG System API.

## Table of Contents
- [Getting Started](#getting-started)
- [Upload Examples](#upload-examples)
- [Query Examples](#query-examples)
- [Advanced Usage](#advanced-usage)
- [Error Handling](#error-handling)

## Getting Started

### Start the Server
```bash
uvicorn app.main:app --reload --port 8000
```

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

## Upload Examples

### Example 1: Upload Text File

**cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/text/sample1_ai_overview.txt"
```

**Python:**
```python
import requests

url = "http://localhost:8000/upload"
files = {'file': open('samples/text/sample1_ai_overview.txt', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "status": "ok",
  "ingested_chunks": 5,
  "doc_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Example 2: Upload Image

**cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/images/diagram.png"
```

**Python:**
```python
import requests

url = "http://localhost:8000/upload"
files = {'file': open('samples/images/diagram.png', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "status": "ok",
  "ingested_images": 1,
  "doc_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "ocr_chars": 245
}
```

### Example 3: Upload PDF

**cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/pdfs/research_paper.pdf"
```

**Python:**
```python
import requests

url = "http://localhost:8000/upload"
files = {'file': open('samples/pdfs/research_paper.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "status": "ok",
  "doc_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "text_chunks": 42,
  "embedded_images": 8
}
```

### Example 4: Batch Upload (Python)

```python
import requests
from pathlib import Path

url = "http://localhost:8000/upload"
sample_dir = Path("samples/text")

results = []
for file_path in sample_dir.glob("*.txt"):
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f)}
        response = requests.post(url, files=files)
        results.append({
            'filename': file_path.name,
            'status': response.status_code,
            'result': response.json()
        })

for result in results:
    print(f"{result['filename']}: {result['result']['doc_id']}")
```

## Query Examples

### Example 1: Simple Text Query

**cURL:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5
  }'
```

**Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {
    "query": "What is machine learning?",
    "top_k": 5
}
response = requests.post(url, json=payload)
results = response.json()

print(f"Query: {results['query']}")
print(f"Total results: {results['total_results']}\n")

for i, result in enumerate(results['results'], 1):
    print(f"Result {i}:")
    print(f"  Score: {result['score']:.4f}")
    print(f"  Modality: {result['modality']}")
    print(f"  Source: {result['source']}")
    if result.get('document'):
        print(f"  Content: {result['document'][:100]}...")
    print()
```

**Response:**
```json
{
  "query": "What is machine learning?",
  "total_results": 5,
  "results": [
    {
      "id": "txt::a1b2c3d4::0",
      "score": 0.9234,
      "modality": "text",
      "document": "Machine Learning is a subset of AI that provides systems the ability to automatically learn and improve from experience...",
      "metadata": {
        "doc_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "file_type": "text",
        "source_path": "data/uploads/sample1_ai_overview.txt",
        "chunk_index": 0,
        "uploaded_at": "2024-01-01T12:00:00"
      },
      "source": "Source: data/uploads/sample1_ai_overview.txt | Type: text | Chunk: 0 | Uploaded: 2024-01-01T12:00:00"
    }
  ]
}
```

### Example 2: Cross-Modal Query (Text to Image)

**Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {
    "query": "diagram showing neural network architecture",
    "top_k": 5
}
response = requests.post(url, json=payload)
results = response.json()

for result in results['results']:
    if result['modality'] == 'image':
        print(f"Found image: {result['metadata']['source_path']}")
        print(f"  Score: {result['score']:.4f}")
        print(f"  OCR Text: {result.get('ocr_text', 'N/A')[:100]}")
```

### Example 3: Specific Factual Query

**Query:** "What are the benefits of cloud computing?"

**Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {
    "query": "What are the benefits of cloud computing?",
    "top_k": 3
}
response = requests.post(url, json=payload)
results = response.json()

# Extract and display relevant information
for result in results['results']:
    if result['modality'] == 'text':
        print(f"Score: {result['score']:.4f}")
        print(f"Content: {result['document']}\n")
```

**Expected Results:**
- Text chunks discussing cost savings, scalability, reliability
- High relevance scores (> 0.8) for direct matches

### Example 4: Vague/Exploratory Query

**Query:** "artificial intelligence"

**Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {
    "query": "artificial intelligence",
    "top_k": 10
}
response = requests.post(url, json=payload)
results = response.json()

# Group results by modality
text_results = [r for r in results['results'] if r['modality'] == 'text']
image_results = [r for r in results['results'] if r['modality'] == 'image']

print(f"Text results: {len(text_results)}")
print(f"Image results: {len(image_results)}")
```

**Expected Results:**
- Broader range of results covering AI, ML, DL, NLP, etc.
- Mix of text and images
- Scores more distributed (0.5 - 0.9)

### Example 5: Technical Query

**Query:** "Python functions and classes"

**Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {
    "query": "Python functions and classes",
    "top_k": 5
}
response = requests.post(url, json=payload)
results = response.json()

# Display results with source attribution
for i, result in enumerate(results['results'], 1):
    print(f"\n{i}. {result['source']}")
    print(f"   Score: {result['score']:.4f}")
    if result.get('document'):
        # Extract relevant sentences
        doc = result['document']
        if 'function' in doc.lower() or 'class' in doc.lower():
            print(f"   Relevant content found")
```

### Example 6: Query with Different top_k Values

**Python:**
```python
import requests

url = "http://localhost:8000/query"
query_text = "data science"

for top_k in [3, 5, 10]:
    payload = {"query": query_text, "top_k": top_k}
    response = requests.post(url, json=payload)
    results = response.json()
    
    print(f"\nTop-{top_k} results:")
    print(f"  Total: {results['total_results']}")
    print(f"  Score range: {results['results'][0]['score']:.4f} - {results['results'][-1]['score']:.4f}")
```

## Advanced Usage

### Example 1: Filter Results by Modality

**Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {"query": "machine learning", "top_k": 10}
response = requests.post(url, json=payload)
results = response.json()

# Filter for text-only results
text_results = [r for r in results['results'] if r['modality'] == 'text']

# Filter for image-only results
image_results = [r for r in results['results'] if r['modality'] == 'image']

print(f"Text results: {len(text_results)}")
print(f"Image results: {len(image_results)}")
```

### Example 2: Extract Source Documents

**Python:**
```python
import requests
from collections import defaultdict

url = "http://localhost:8000/query"
payload = {"query": "artificial intelligence", "top_k": 20}
response = requests.post(url, json=payload)
results = response.json()

# Group results by source document
by_source = defaultdict(list)
for result in results['results']:
    source_path = result['metadata'].get('source_path', 'unknown')
    by_source[source_path].append(result)

# Display documents with most relevant results
for source, source_results in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n{source}: {len(source_results)} results")
    avg_score = sum(r['score'] for r in source_results) / len(source_results)
    print(f"  Average score: {avg_score:.4f}")
```

### Example 3: Build a Simple Search Interface

**Python:**
```python
import requests

def search(query, top_k=5):
    """Simple search function."""
    url = "http://localhost:8000/query"
    payload = {"query": query, "top_k": top_k}
    response = requests.post(url, json=payload)
    return response.json()

def display_results(results):
    """Display search results in a readable format."""
    print(f"\nQuery: {results['query']}")
    print(f"Found {results['total_results']} results\n")
    print("=" * 80)
    
    for i, result in enumerate(results['results'], 1):
        print(f"\n{i}. [{result['modality'].upper()}] Score: {result['score']:.4f}")
        print(f"   {result['source']}")
        
        if result['modality'] == 'text' and result.get('document'):
            content = result['document'][:200] + "..." if len(result['document']) > 200 else result['document']
            print(f"   {content}")
        elif result['modality'] == 'image' and result.get('ocr_text'):
            ocr = result['ocr_text'][:200] + "..." if len(result['ocr_text']) > 200 else result['ocr_text']
            print(f"   OCR: {ocr}")
        
        print("-" * 80)

# Interactive search
while True:
    query = input("\nEnter search query (or 'quit' to exit): ")
    if query.lower() == 'quit':
        break
    
    results = search(query)
    display_results(results)
```

### Example 4: Compare Query Results

**Python:**
```python
import requests

def compare_queries(queries, top_k=5):
    """Compare results for multiple queries."""
    url = "http://localhost:8000/query"
    
    all_results = {}
    for query in queries:
        payload = {"query": query, "top_k": top_k}
        response = requests.post(url, json=payload)
        all_results[query] = response.json()
    
    # Compare
    for query, results in all_results.items():
        print(f"\nQuery: '{query}'")
        print(f"  Results: {results['total_results']}")
        print(f"  Top score: {results['results'][0]['score']:.4f}")
        print(f"  Modalities: {set(r['modality'] for r in results['results'])}")

# Example usage
queries = [
    "machine learning",
    "deep learning",
    "neural networks"
]
compare_queries(queries)
```

## Error Handling

### Example 1: Handle Upload Errors

**Python:**
```python
import requests

def safe_upload(file_path):
    """Upload file with error handling."""
    url = "http://localhost:8000/upload"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f)}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        elif response.status_code == 415:
            return {'success': False, 'error': 'Unsupported file type'}
        else:
            return {'success': False, 'error': response.text}
            
    except FileNotFoundError:
        return {'success': False, 'error': 'File not found'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Cannot connect to server'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Usage
result = safe_upload('samples/text/sample1.txt')
if result['success']:
    print(f"Upload successful: {result['data']['doc_id']}")
else:
    print(f"Upload failed: {result['error']}")
```

### Example 2: Handle Query Errors

**Python:**
```python
import requests

def safe_query(query, top_k=5):
    """Query with error handling."""
    url = "http://localhost:8000/query"
    
    try:
        payload = {"query": query, "top_k": top_k}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': response.text}
            
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Cannot connect to server'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Usage
result = safe_query("machine learning")
if result['success']:
    print(f"Found {result['data']['total_results']} results")
else:
    print(f"Query failed: {result['error']}")
```

### Example 3: Retry Logic

**Python:**
```python
import requests
import time

def upload_with_retry(file_path, max_retries=3):
    """Upload file with retry logic."""
    url = "http://localhost:8000/upload"
    
    for attempt in range(max_retries):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f)}
                response = requests.post(url, files=files, timeout=30)
                
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 415:
                # Don't retry for unsupported file types
                raise ValueError("Unsupported file type")
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    raise Exception(f"Failed after {max_retries} attempts")
```

## Health Check

### Example: Monitor Server Health

**Python:**
```python
import requests
import time

def check_health():
    """Check if server is healthy."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is healthy")
            print(f"  Status: {data['status']}")
            print(f"  Service: {data['service']}")
            print(f"  Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"✗ Server returned error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server")
        return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

# Continuous monitoring
while True:
    check_health()
    time.sleep(60)  # Check every minute
```

## Performance Tips

1. **Batch Uploads**: Upload multiple files in parallel using threading
2. **Reuse Connections**: Use `requests.Session()` for multiple requests
3. **Adjust top_k**: Use smaller top_k values for faster queries
4. **Cache Results**: Cache frequent queries on client side
5. **Monitor Logs**: Check `logs/app.log` for performance insights

## Next Steps

- Explore the interactive Swagger UI at `http://localhost:8000/docs`
- Run the demo script: `python demo.py`
- Check the logs for detailed processing information
- Experiment with different query types and parameters
