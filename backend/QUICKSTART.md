# ⚡ QUICK START GUIDE

## 🚀 Get Running in 3 Steps

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start MinIO
Choose ONE option:

**Option A - Using Homebrew (macOS):**
```bash
brew install minio
minio server ~/minio-data --console-address ":9001"
```

**Option B - Using Docker:**
```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"
```

### Step 3: Start Backend
```bash
uvicorn main:app --reload
```

**Done!** 🎉

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

---

## 📡 API Quick Test

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_docs/finance_report.md"
```

### 2. Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "tax documents", "top_k": 3}'
```

### 3. Download
```bash
curl "http://localhost:8000/download/finance/finance_report.md"
```

---

## 🎯 Test with Sample Docs

Three sample documents are included in `sample_docs/`:
- `finance_report.md` → Auto-classified as "finance"
- `legal_contract.md` → Auto-classified as "legal"  
- `general_roadmap.md` → Auto-classified as "general"

Upload them all to test the system!

---

## 🔧 Postman Testing

1. Import `Postman_Collection.json` into Postman
2. All endpoints pre-configured
3. Start testing immediately

---

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI app + endpoints
├── config.py            # Settings & configuration
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── services/
│   ├── embedding.py     # AI embeddings
│   ├── storage.py       # MinIO operations
│   ├── search.py        # ChromaDB queries
│   └── classifier.py    # Auto-categorization
├── utils/
│   └── text_extractor.py # PDF/TXT/MD parsing
├── sample_docs/         # Test documents
├── test_api.py          # Python test script
└── start.sh             # Quick start script
```

---

## 🐛 Troubleshooting

### "Connection refused to MinIO"
→ Start MinIO first (see Step 2 above)

### "Module not found"
→ Run `pip install -r requirements.txt`

### "ChromaDB permission error"
→ Delete `chroma_db/` folder and restart

### "Model downloading..."
→ First run downloads 90MB model (one-time only)

---

## 📊 What Gets Created Automatically

On first run, the system auto-creates:
- ✅ MinIO buckets: `finance`, `legal`, `general`
- ✅ ChromaDB collection: `documents`
- ✅ Persistent vector database in `chroma_db/`

---

## 🎯 Next Steps

1. ✅ Test all endpoints in Postman
2. ✅ Upload your own documents
3. ✅ Try different search queries
4. 🎯 Build frontend interface
5. 🎯 Add more file type support
6. 🎯 Deploy to cloud

---

## 💡 Pro Tips

- Use the `/docs` endpoint for interactive API testing
- Check `DEMO_SCRIPT.md` for presentation ideas
- Read `README.md` for detailed documentation
- Sample docs are perfect for testing classification

---

## 🆘 Need Help?

1. Check the API docs: http://localhost:8000/docs
2. Run health check: `curl http://localhost:8000/`
3. List documents: `curl http://localhost:8000/documents`
4. View logs in terminal where server is running

---

**Built for hackathons. Production-ready code. Ship it! 🚀**
