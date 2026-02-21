import requests
import urllib.request
import ssl
import json

# Disable SSL verification for local testing
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Testing download endpoint...\n")

# Get presigned URL from backend
response = requests.get("http://localhost:8000/download/finance/test_finance_doc.txt")
data = response.json()
download_url = data["download_url"]

print(f"Backend returned URL:")
print(f"{download_url[:100]}...\n")

# Test if URL works
try:
    response = urllib.request.urlopen(download_url, context=ctx)
    content = response.read().decode('utf-8')
    print(f"✅ URL WORKS! Content: {content[:70]}...")
except Exception as e:
    print(f"❌ URL FAILED: {e}")
