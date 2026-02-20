#!/bin/bash

# Semantic Storage Gateway - Quick Start Script
# This script sets up and runs the backend server

echo "🚀 Semantic Storage Gateway - Quick Start"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: Start MinIO before running the server!"
echo ""
echo "Start MinIO with:"
echo "  minio server ~/minio-data --console-address ':9001'"
echo ""
echo "OR with Docker:"
echo "  docker run -p 9000:9000 -p 9001:9001 \\"
echo "    -e 'MINIO_ROOT_USER=minioadmin' \\"
echo "    -e 'MINIO_ROOT_PASSWORD=minioadmin' \\"
echo "    quay.io/minio/minio server /data --console-address ':9001'"
echo ""
echo "=========================================="
echo ""
echo "Press ENTER to start the backend server..."
read

# Start the server
echo "🚀 Starting FastAPI server..."
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
