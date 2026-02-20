# 🚀 QUICK START - For Your Friend

Hey! Here's how to get everything running on your Mac:

## Step 1: Pull Latest Changes

```bash
cd Synapse-Storage  # or wherever you cloned it
git pull origin master
```

## Step 2: Start MinIO (Easy Way - Docker)

```bash
# Make sure Docker Desktop is running, then:
docker-compose up -d

# Verify it's working:
curl http://localhost:9000/minio/health/live
# Should return: ok
```

**MinIO Console:** http://localhost:9001 (login: minioadmin / minioadmin)

## Step 3: Start Backend

```bash
cd backend

# First time setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Every time after that, just:
source venv/bin/activate
uvicorn main:app --reload
```

**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

## Step 4: Start Frontend

```bash
cd frontend

# First time:
npm install

# Every time:
npm run dev
```

**Frontend:** http://localhost:3000

## Done! 🎉

You should now have:
- ✅ MinIO running (object storage)
- ✅ Backend API running (FastAPI server)
- ✅ Frontend running (Next.js UI)

## What's New?

### 1. **Similarity Filter**
Search results now have a minimum similarity slider (default 50%). This filters out irrelevant results!

**Try it:**
1. Go to Search tab
2. Search for "tax information"
3. Adjust the "Min Similarity" slider
4. See how results change

### 2. **No More Duplicates**
ChromaDB was cleaned up. Each document now appears only once.

### 3. **Scores Are Visible**
Check the colored bars in search results:
- 🟢 Green (80-100%): Excellent match
- 🟡 Yellow (60-79%): Good match  
- 🔴 Red (<60%): Weak match

## Troubleshooting

### "Connection refused" on backend
MinIO isn't running. Run: `docker-compose up -d`

### "Port already in use"
Something else is using the port. Find and kill it:
```bash
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :9000  # MinIO
kill -9 <PID>
```

### ChromaDB errors
Reset the collection:
```bash
curl -X POST http://localhost:8000/admin/reset-collection
```
Then re-upload documents via the Upload tab.

## Files to Read

- **FIXES_APPLIED.md** - What was fixed and why
- **MAC_SETUP.md** - Detailed Mac setup guide
- **TECHNICAL_EXPLAINED.md** - How ChromaDB/MinIO work
- **API_TESTING_GUIDE.md** - API examples

## Next Features to Implement

See **TECHNICAL_EXPLAINED.md** section "Features to Add to WIN the Hackathon":
1. Document preview in search results
2. Analytics dashboard
3. Batch upload
4. Search history
5. Export results as CSV

## Test Search Now!

```bash
# Test via terminal:
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "tax documents", "top_k": 5, "min_similarity": 0.5}'

# Or use the UI at http://localhost:3000
```

Good luck with the hackathon! 🏆
