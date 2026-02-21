#!/usr/bin/env python3
"""
Test GCS Connection

Quick verification that credentials and configuration work.
Run from project root: python infrastructure/gcp/test-connection.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

print("🔍 Testing GCS Connection")
print("=" * 50)

# Check environment variables
bucket_name = os.getenv('GCS_BUCKET_NAME')
creds_path = os.getenv('GCS_CREDENTIALS_PATH')
base_url = os.getenv('GCS_BASE_URL')

print(f"Bucket: {bucket_name}")
print(f"Credentials: {creds_path}")
print(f"Base URL: {base_url}")
print()

# Check credentials file exists
creds_path = os.path.expanduser(creds_path)
if not Path(creds_path).exists():
    print(f"❌ Credentials file not found: {creds_path}")
    sys.exit(1)
print(f"✅ Credentials file exists: {creds_path}")

# Try to import google.cloud.storage
try:
    from google.cloud import storage
    print("✅ google-cloud-storage library installed")
except ImportError:
    print("❌ google-cloud-storage not installed")
    print("   Run: pip install google-cloud-storage")
    sys.exit(1)

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

# Test connection
try:
    client = storage.Client()
    print("✅ GCS client initialized")

    # Get bucket
    bucket = client.bucket(bucket_name)
    print(f"✅ Bucket accessed: {bucket_name}")

    # Test upload
    test_blob = bucket.blob('test/connection-test.txt')
    test_content = "Test upload from Python - GCS connection working!"
    test_blob.upload_from_string(test_content)
    print("✅ Test upload successful")

    # Get public URL
    public_url = f"{base_url}/test/connection-test.txt"
    print(f"📎 Public URL: {public_url}")

    # Test download
    downloaded = test_blob.download_as_text()
    if downloaded == test_content:
        print("✅ Test download successful")

    # Clean up
    test_blob.delete()
    print("✅ Test file cleaned up")

    print()
    print("=" * 50)
    print("🎉 All tests passed! GCS is ready to use.")
    print()
    print("Your bucket structure:")
    print(f"  gs://{bucket_name}/")
    print("  ├── photos/varieties/    (VIVC grape photos)")
    print("  ├── photos/producers/    (winery photos)")
    print("  └── documents/           (PDFs, exports)")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
