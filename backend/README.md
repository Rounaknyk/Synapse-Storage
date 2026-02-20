# 🚀 Semantic Storage Gateway - Backend

AI-powered document storage and semantic search system built for hackathons.

## 🏗️ Architecture

```
MinIO (Object Storage) → FastAPI → SentenceTransformers → ChromaDB
```

## 📦 Tech Stack

- **FastAPI** - High-performance API framework
- **SentenceTransformers** - Local embeddings (all-MiniLM-L6-v2)
- **ChromaDB** - Persistent vector database
- **MinIO** - S3-compatible object storage
- **boto3** - S3 communication

## 🗂️ Project Structure

```
backend/
├── main.py                 # FastAPI application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── services/
│   ├── embedding.py       # Embedding generation
│   ├── storage.py         # MinIO operations
│   ├── search.py          # ChromaDB operations
│   └── classifier.py      # Document classification
└── utils/
    └── text_extractor.py  # Text extraction from files
```

## ⚡ Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start MinIO (in separate terminal)

```bash
# Using Homebrew (macOS)
brew install minio
minio server ~/minio-data --console-address ":9001"

# Or using Docker
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"
```

MinIO will be available at:
- API: http://localhost:9000
- Console: http://localhost:9001

### 3. Start Backend Server

```bash
uvicorn main:app --reload
```

Server will start at: **http://localhost:8000**

API docs available at: **http://localhost:8000/docs**

## 📡 API Endpoints

### 1. Upload Document
```http
POST /upload
Content-Type: multipart/form-data

file: <PDF, TXT, or MD file>
```

**Response:**
```json
{
  "success": true,
  "message": "File uploaded and indexed successfully",
  "file_name": "invoice.pdf",
  "document_type": "finance",
  "bucket_name": "finance"
}
```

### 2. Search Documents
```http
POST /search
Content-Type: application/json

{
  "query": "tax documents from last quarter",
  "top_k": 3
}
```

**Response:**
```json
[
  {
    "file_name": "Q4_taxes.pdf",
    "bucket_name": "finance",
    "document_type": "finance",
    "upload_time": "2026-02-20T10:30:00",
    "similarity_score": 0.87
  }
]
```

### 3. Download File
```http
GET /download/{bucket_name}/{file_name}
```

**Response:**
```json
{
  "file_name": "invoice.pdf",
  "bucket_name": "finance",
  "download_url": "http://localhost:9000/finance/invoice.pdf?..."
}
```

### 4. List All Documents
```http
GET /documents
```

### 5. Health Check
```http
GET /
```

## 🧪 Testing with Postman

### Test Upload
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

### Test Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "financial reports", "top_k": 3}'
```

### Test Download
```bash
curl -X GET "http://localhost:8000/download/finance/document.pdf"
```

## 🏷️ Document Classification

Documents are automatically classified based on keywords:

- **Finance**: invoice, tax, revenue, balance, payment, transaction, financial
- **Legal**: agreement, contract, clause, terms, legal, liability, party
- **General**: Everything else

## 🔧 Configuration

Edit `.env` file:

```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
```

## 📊 System Features

✅ Automatic bucket creation on startup  
✅ Persistent vector database  
✅ Semantic similarity search  
✅ Multi-format support (PDF, TXT, MD)  
✅ Automatic document classification  
✅ Presigned URL generation for secure downloads  
✅ No authentication (hackathon-ready)  
✅ CORS enabled for frontend integration  

## 🐛 Troubleshooting

### MinIO Connection Error
- Ensure MinIO is running on port 9000
- Check credentials in `.env` file

### Embedding Model Download
- First run will download ~90MB model
- Subsequent runs use cached model

### ChromaDB Permission Error
- Ensure write permissions in project directory
- Delete `chroma_db/` folder and restart

## 🚀 Next Steps

1. ✅ Test all endpoints in Postman
2. ✅ Upload sample documents
3. ✅ Verify search functionality
4. ✅ Test download URLs
5. 🎯 Build frontend interface

## 📝 Notes

- Single-user system (no auth)
- All storage is local (no cloud)
- Optimized for demo/hackathon
- Production-ready code structure

---

**Built with ❤️ for hackathons**
