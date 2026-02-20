# Quick Setup Instructions for Mac

## Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed (for frontend)
- Docker installed (for MinIO)

## Step 1: Start MinIO (Object Storage)

The easiest way to run MinIO on Mac is using Docker:

```bash
# Start MinIO using docker-compose
docker-compose up -d

# Verify MinIO is running
curl http://localhost:9000/minio/health/live
```

**MinIO Console:** http://localhost:9001  
**Login:** minioadmin / minioadmin

### Alternative: Install MinIO Locally (without Docker)

```bash
# Install using Homebrew
brew install minio/stable/minio

# Start MinIO
minio server ~/minio-data --console-address ':9001'
```

## Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend API:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

## Step 3: Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend:** http://localhost:3000

## Troubleshooting

### MinIO Connection Error
If you see "Connection refused" errors:

1. Check if MinIO is running:
   ```bash
   docker ps | grep minio
   # OR
   curl http://localhost:9000/minio/health/live
   ```

2. Restart MinIO:
   ```bash
   docker-compose restart
   ```

### Port Already in Use

If port 8000/3000/9000 is already in use:

```bash
# Find what's using the port
lsof -i :8000
lsof -i :3000
lsof -i :9000

# Kill the process
kill -9 <PID>
```

### ChromaDB Issues

If you see ChromaDB errors, reset the collection:

```bash
curl -X POST http://localhost:8000/admin/reset-collection
```

Then re-upload your documents.

## Full Reset (Clean Start)

```bash
# Stop everything
docker-compose down -v  # Deletes MinIO data
rm -rf backend/chroma_db  # Deletes ChromaDB data
rm -rf backend/venv  # Deletes Python environment
rm -rf frontend/node_modules  # Deletes Node modules

# Start fresh from Step 1
```

## Development Tips

### Run Everything in One Command (using tmux)

```bash
# Install tmux if not installed
brew install tmux

# Run all services
tmux new-session -d -s dev 'docker-compose up' \; \
  split-window -v -p 50 'cd backend && source venv/bin/activate && uvicorn main:app --reload' \; \
  split-window -h -p 50 'cd frontend && npm run dev' \; \
  attach

# Detach: Ctrl+B then D
# Reattach: tmux attach -t dev
# Kill session: tmux kill-session -t dev
```

### Check All Services Status

```bash
# Backend health
curl http://localhost:8000/health

# MinIO health
curl http://localhost:9000/minio/health/live

# Frontend (should show HTML)
curl http://localhost:3000
```

## Common Mac-Specific Issues

### 1. "xcrun: error" when installing deps
```bash
xcode-select --install
```

### 2. Python version mismatch
```bash
# Use pyenv to manage Python versions
brew install pyenv
pyenv install 3.11
pyenv local 3.11
```

### 3. Node version issues
```bash
# Use nvm
brew install nvm
nvm install 20
nvm use 20
```

## Environment Variables

If you need to customize settings, create a `.env` file in the backend directory:

```bash
# backend/.env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
CHROMA_PERSIST_DIR=./chroma_db
```

## Ready to Go! 🚀

After setup, you should have:
- ✅ MinIO running on http://localhost:9000
- ✅ Backend API on http://localhost:8000
- ✅ Frontend on http://localhost:3000

Upload some documents and start searching! 🎉
