# 🚀 Deployment Guide - Synapse Storage Gateway

## Overview
This guide covers deploying your Semantic Storage Gateway to production, including MinIO object storage, backend API, and frontend.

---

## 🎯 Quick Answer: MinIO Deployment

**No, MinIO does NOT only work locally!** Here are your deployment options:

### Option 1: MinIO Cloud (Easiest - Recommended for Hackathon)
### Option 2: Self-Hosted MinIO (Free - Docker/Cloud VM)
### Option 3: AWS S3 Compatible (Drop-in replacement)

---

## 📦 Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│             PRODUCTION STACK                     │
├─────────────────────────────────────────────────┤
│ Frontend (Vercel/Netlify)                       │
│    ↓                                             │
│ Backend (Railway/Render/Fly.io)                 │
│    ↓                                             │
│ MinIO (MinIO Cloud/Self-hosted/AWS S3)          │
│ ChromaDB (Persistent Volume)                    │
│ SentenceTransformers (Hugging Face)             │
└─────────────────────────────────────────────────┘
```

---

## 🔥 Option 1: MinIO Cloud (Fastest - 15 minutes)

### Why Choose This:
- ✅ **Zero infrastructure management**
- ✅ **Free tier available**
- ✅ **Automatic scaling**
- ✅ **Perfect for hackathons/demos**

### Setup Steps:

1. **Sign up for MinIO Cloud**
   ```
   Visit: https://min.io/signup
   - Create account
   - Choose free tier (10 GB free)
   ```

2. **Create Access Keys**
   ```
   Console → Access Keys → Create Access Key
   
   Copy:
   - Access Key ID: AKIAIOSFODNN7EXAMPLE
   - Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

3. **Get Your Endpoint**
   ```
   Format: https://play.min.io:9000
   Or your custom: https://your-org.minio.cloud:9000
   ```

4. **Update Backend Config**
   
   **File:** `backend/.env`
   ```bash
   # MinIO Cloud Configuration
   MINIO_ENDPOINT=your-org.minio.cloud:9000
   MINIO_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
   MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   MINIO_SECURE=true
   ```

5. **Update Code (if needed)**
   
   **File:** `backend/config.py`
   ```python
   # MinIO Configuration
   MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
   MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
   MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
   MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
   ```

6. **Test Connection**
   ```bash
   cd backend
   python3 -c "
   from services.storage import storage_service
   print('✅ Connected to MinIO Cloud!')
   "
   ```

**Done!** Your app now uses MinIO Cloud. 🎉

---

## 🐳 Option 2: Self-Hosted MinIO (Docker)

### Why Choose This:
- ✅ **Completely free**
- ✅ **Full control**
- ✅ **Works on any cloud provider**
- ✅ **Production-grade**

### A. Deploy MinIO on Railway (Recommended)

1. **Create `docker-compose.yml` for MinIO**
   ```yaml
   version: '3.8'
   
   services:
     minio:
       image: minio/minio:latest
       container_name: minio
       ports:
         - "9000:9000"
         - "9001:9001"
       environment:
         MINIO_ROOT_USER: minioadmin
         MINIO_ROOT_PASSWORD: minioadmin123
       command: server /data --console-address ":9001"
       volumes:
         - minio_data:/data
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
         interval: 30s
         timeout: 20s
         retries: 3
   
   volumes:
     minio_data:
   ```

2. **Deploy to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Create new project
   railway init
   
   # Deploy MinIO
   railway up
   
   # Get URL
   railway domain
   # Example output: minio-production.up.railway.app
   ```

3. **Update Backend Config**
   ```bash
   MINIO_ENDPOINT=minio-production.up.railway.app:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin123
   MINIO_SECURE=true
   ```

### B. Deploy MinIO on Render

1. **Create `Dockerfile` for MinIO**
   ```dockerfile
   FROM minio/minio:latest
   
   EXPOSE 9000 9001
   
   ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]
   CMD ["server", "/data", "--console-address", ":9001"]
   ```

2. **Deploy on Render**
   ```
   1. Go to render.com
   2. New → Web Service
   3. Connect GitHub repo
   4. Environment: Docker
   5. Add environment variables:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
   6. Add disk: /data (persistent storage)
   7. Deploy
   ```

3. **Get URL**
   ```
   Example: https://minio-xyz123.onrender.com
   ```

### C. Deploy MinIO on AWS EC2 (Self-Managed)

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run MinIO
sudo docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin123" \
  -v /mnt/data:/data \
  --name minio \
  --restart unless-stopped \
  minio/minio server /data --console-address ":9001"

# Access MinIO
# API: http://your-ec2-ip:9000
# Console: http://your-ec2-ip:9001
```

---

## ☁️ Option 3: AWS S3 (Drop-in Replacement)

MinIO is S3-compatible, so you can switch to AWS S3:

1. **Create S3 Bucket**
   ```
   AWS Console → S3 → Create Bucket
   - Name: synapse-storage-prod
   - Region: us-east-1
   - Disable "Block all public access" (for presigned URLs)
   ```

2. **Get AWS Credentials**
   ```
   AWS Console → IAM → Users → Create User
   - Attach policy: AmazonS3FullAccess
   - Create access key
   ```

3. **Update Backend Config**
   ```bash
   MINIO_ENDPOINT=s3.amazonaws.com
   MINIO_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
   MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   MINIO_SECURE=true
   AWS_REGION=us-east-1
   ```

4. **Update Storage Service** (minimal changes needed)
   
   **File:** `backend/services/storage.py`
   ```python
   # Add region configuration
   from minio import Minio
   
   self.client = Minio(
       settings.MINIO_ENDPOINT,
       access_key=settings.MINIO_ACCESS_KEY,
       secret_key=settings.MINIO_SECRET_KEY,
       secure=settings.MINIO_SECURE,
       region=os.getenv("AWS_REGION", "us-east-1")  # Add this
   )
   ```

**Note:** S3 has different bucket naming (no underscores), so update `config.py`:
```python
BUCKETS = ["finance", "legal", "general"]  # Remove finance_bucket format
```

---

## 🚀 Full Application Deployment

### 1. Deploy Backend (Railway/Render/Fly.io)

#### Option A: Railway (Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Add environment variables
railway variables set MINIO_ENDPOINT=your-minio-endpoint
railway variables set MINIO_ACCESS_KEY=your-access-key
railway variables set MINIO_SECRET_KEY=your-secret-key
railway variables set GROQ_API_KEY=your-groq-key

# Deploy
railway up

# Get URL
railway domain
# Example: https://synapse-backend.up.railway.app
```

#### Option B: Render

1. **Create `render.yaml`**
   ```yaml
   services:
     - type: web
       name: synapse-backend
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: MINIO_ENDPOINT
           value: your-minio-endpoint
         - key: MINIO_ACCESS_KEY
           value: your-access-key
         - key: MINIO_SECRET_KEY
           sync: false  # Secret
       disk:
         name: chromadb
         mountPath: /app/chroma_db
         sizeGB: 1
   ```

2. **Deploy**
   ```
   1. Go to render.com
   2. New → Web Service
   3. Connect GitHub repo (backend folder)
   4. Deploy
   ```

#### Option C: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
cd backend
fly launch

# Set secrets
fly secrets set MINIO_ENDPOINT=your-endpoint
fly secrets set MINIO_ACCESS_KEY=your-key
fly secrets set MINIO_SECRET_KEY=your-secret
fly secrets set GROQ_API_KEY=your-groq-key

# Deploy
fly deploy

# Get URL
fly status
# Example: https://synapse-backend.fly.dev
```

---

### 2. Deploy Frontend (Vercel/Netlify)

#### Option A: Vercel (Recommended for Next.js)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://synapse-backend.up.railway.app

# Production deploy
vercel --prod
```

**Or use Vercel Dashboard:**
```
1. Go to vercel.com
2. Import GitHub repo
3. Framework: Next.js
4. Root directory: frontend
5. Environment variables:
   - NEXT_PUBLIC_API_URL: https://your-backend-url
6. Deploy
```

#### Option B: Netlify

1. **Create `netlify.toml`**
   ```toml
   [build]
     base = "frontend"
     command = "npm run build"
     publish = "out"
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   
   [build.environment]
     NEXT_PUBLIC_API_URL = "https://your-backend-url"
   ```

2. **Deploy**
   ```bash
   # Install Netlify CLI
   npm install -g netlify-cli
   
   # Login
   netlify login
   
   # Deploy
   cd frontend
   netlify deploy --prod
   ```

---

### 3. Update Frontend API URL

**File:** `frontend/src/lib/api.ts`
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**File:** `frontend/.env.production`
```bash
NEXT_PUBLIC_API_URL=https://synapse-backend.up.railway.app
```

---

## 🔒 Security Checklist

### Before Going Live:

1. **Change Default Credentials**
   ```bash
   # Generate strong passwords
   openssl rand -base64 32
   
   # Update .env
   MINIO_ACCESS_KEY=<strong-access-key>
   MINIO_SECRET_KEY=<strong-secret-key>
   ```

2. **Enable HTTPS**
   - ✅ Railway/Render/Vercel provide free HTTPS
   - ✅ Use Let's Encrypt for custom domains

3. **CORS Configuration**
   
   **File:** `backend/main.py`
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://synapse-storage.vercel.app",  # Your production URL
           "http://localhost:3000"  # Keep for dev
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Environment Variables**
   - ❌ Never commit `.env` files
   - ✅ Use platform secret managers
   - ✅ Rotate keys regularly

5. **Rate Limiting** (Optional but recommended)
   ```bash
   pip install slowapi
   ```
   
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/upload")
   @limiter.limit("10/minute")
   async def upload_file(...):
       ...
   ```

---

## 💰 Cost Breakdown (for 1000 users/month)

### Free Tier Option (Perfect for Hackathon):
- **Frontend (Vercel):** FREE
- **Backend (Railway):** FREE ($5 credit)
- **MinIO (Self-hosted on Railway):** FREE
- **Total:** $0/month

### Production Option:
- **Frontend (Vercel Pro):** $20/month
- **Backend (Railway):** $5-10/month
- **MinIO Cloud:** $10/month (50GB)
- **Total:** $35-40/month

### Enterprise Option:
- **Frontend (Vercel):** $20/month
- **Backend (AWS ECS):** $30/month
- **AWS S3:** $5/month (100GB)
- **Total:** $55/month

---

## 📊 Recommended Setup for Hackathon Demo

```
Frontend: Vercel (free, instant deploy)
Backend: Railway (free $5 credit, easy setup)
MinIO: Railway Docker (free, same platform)
Domain: Vercel auto-domain (.vercel.app)
Total Cost: $0
Setup Time: 30 minutes
```

---

## 🧪 Testing Production Setup

1. **Test MinIO Connection**
   ```bash
   curl -I https://your-minio-endpoint:9000/minio/health/live
   # Should return: 200 OK
   ```

2. **Test Backend API**
   ```bash
   curl https://your-backend-url/documents
   # Should return: {"total_documents": 0, "documents": []}
   ```

3. **Test Frontend**
   ```
   Visit: https://your-app.vercel.app
   - Upload a file
   - Search for it
   - Download it
   ```

4. **Test End-to-End**
   ```bash
   # Upload via API
   curl -X POST https://your-backend-url/upload \
     -F "file=@test.pdf"
   
   # Verify in MinIO Console
   # Visit: https://your-minio-endpoint:9001
   ```

---

## 🚨 Troubleshooting

### Issue: "Connection refused" to MinIO
**Solution:**
- Check firewall rules (open ports 9000, 9001)
- Verify MINIO_ENDPOINT in backend .env
- Test: `telnet your-minio-host 9000`

### Issue: "CORS error" in frontend
**Solution:**
- Add your frontend URL to CORS origins in backend
- Check browser console for exact error
- Verify backend is using HTTPS if frontend is

### Issue: "File upload fails"
**Solution:**
- Check MinIO bucket exists
- Verify MinIO credentials are correct
- Check backend logs for specific error
- Test MinIO directly with `mc` CLI

### Issue: "Search returns no results"
**Solution:**
- Verify ChromaDB has data: `/documents` endpoint
- Check if embedding model loaded successfully
- Restart backend to reload ChromaDB

---

## 📚 Additional Resources

- **MinIO Docs:** https://min.io/docs/minio/linux/index.html
- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs

---

## ✅ Quick Deployment Checklist

- [ ] Choose MinIO deployment option
- [ ] Set up MinIO (cloud/self-hosted/S3)
- [ ] Get MinIO credentials
- [ ] Update backend .env with MinIO config
- [ ] Deploy backend to Railway/Render
- [ ] Test backend API endpoints
- [ ] Update frontend API URL
- [ ] Deploy frontend to Vercel
- [ ] Test end-to-end upload/search/download
- [ ] Set up custom domain (optional)
- [ ] Enable monitoring/analytics
- [ ] **Demo ready!** 🎉

---

**Estimated Total Time:** 
- Basic setup: 30-45 minutes
- Production setup: 2-3 hours
- With custom domain: +30 minutes

**You're not limited to localhost anymore!** 🚀
