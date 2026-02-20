"""
Quick test script for the Semantic Storage Gateway
Run after starting the server with: uvicorn main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if server is running"""
    print("\n🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_upload(file_path):
    """Test file upload"""
    print(f"\n📤 Testing upload: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_search(query, top_k=3):
    """Test semantic search"""
    print(f"\n🔎 Testing search: '{query}'")
    payload = {
        "query": query,
        "top_k": top_k
    }
    response = requests.post(
        f"{BASE_URL}/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_download(bucket_name, file_name):
    """Test file download URL generation"""
    print(f"\n📥 Testing download: {bucket_name}/{file_name}")
    response = requests.get(f"{BASE_URL}/download/{bucket_name}/{file_name}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Download URL: {data['download_url']}")
    else:
        print(f"Response: {response.json()}")
    return response.status_code == 200

def test_list_documents():
    """Test listing all documents"""
    print("\n📋 Testing list documents...")
    response = requests.get(f"{BASE_URL}/documents")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Semantic Storage Gateway - Test Suite")
    print("=" * 60)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Server not running! Start with: uvicorn main:app --reload")
        exit(1)
    
    print("\n✅ Server is running!")
    print("\n" + "=" * 60)
    print("Manual Testing Guide:")
    print("=" * 60)
    
    print("\n1️⃣  Upload a file:")
    print("   test_upload('/path/to/your/document.pdf')")
    
    print("\n2️⃣  Search for documents:")
    print("   test_search('financial reports')")
    
    print("\n3️⃣  Download a file:")
    print("   test_download('finance', 'document.pdf')")
    
    print("\n4️⃣  List all documents:")
    print("   test_list_documents()")
    
    print("\n" + "=" * 60)
    print("💡 Tip: Import this file and use the functions:")
    print("   from test_api import test_upload, test_search")
    print("=" * 60 + "\n")
