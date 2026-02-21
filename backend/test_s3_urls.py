import boto3
from botocore.config import Config
from datetime import timedelta
import urllib.request
import ssl

# Disable SSL verification for testing (local cert issue)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Testing S3 presigned URL generation and access...\n")

# Test with the exact same configuration as our service
s3_config = Config(
    region_name='eu-north-1',
    s3={'addressing_style': 'virtual'},
    signature_version='s3v4'
)

s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIAXGTLFONP5R2KJTBL',
    aws_secret_access_key='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',
    region_name='eu-north-1',
    config=s3_config
)

# Test 1: Generate URL for test file
print("Test 1: test_finance_doc.txt")
url1 = s3_client.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'synapse-finance-rohit',
        'Key': 'test_finance_doc.txt'
    },
    ExpiresIn=3600
)
print(f"URL: {url1[:80]}...")

try:
    response = urllib.request.urlopen(url1, context=ctx)
    content = response.read().decode('utf-8')
    print(f"✅ SUCCESS! Content: {content[:50]}...\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 2: Generate URL for PDF
print("Test 2: QFIX-PAYMENT-RECEIPT-X4FXHSF00000025 (1).pdf")
url2 = s3_client.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'synapse-finance-rohit',
        'Key': 'QFIX-PAYMENT-RECEIPT-X4FXHSF00000025 (1).pdf'
    },
    ExpiresIn=3600
)
print(f"URL: {url2[:80]}...")

try:
    response = urllib.request.urlopen(url2, context=ctx)
    print(f"✅ SUCCESS! PDF size: {len(response.read())} bytes\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 3: Try without Config to compare
print("Test 3: Without Config (for comparison)")
s3_basic = boto3.client(
    's3',
    aws_access_key_id='AKIAXGTLFONP5R2KJTBL',
    aws_secret_access_key='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',
    region_name='eu-north-1'
)
url3 = s3_basic.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'synapse-finance-rohit',
        'Key': 'test_finance_doc.txt'
    },
    ExpiresIn=3600
)
print(f"URL: {url3[:80]}...")

try:
    response = urllib.request.urlopen(url3, context=ctx)
    content = response.read().decode('utf-8')
    print(f"✅ SUCCESS! Content: {content[:50]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")
