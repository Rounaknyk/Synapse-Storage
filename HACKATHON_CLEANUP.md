# 🧹 Files to Delete Before Submitting Hackathon Repo

## ⚠️ CRITICAL - DELETE THESE (Security Risk):

```bash
# Delete .env file (contains API keys and credentials)
rm backend/.env

# Create .env.example instead
cat > backend/.env.example << 'EOF'
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=eu-north-1
AWS_S3_FINANCE_BUCKET=your-finance-bucket
AWS_S3_LEGAL_BUCKET=your-legal-bucket
AWS_S3_GENERAL_BUCKET=your-general-bucket

# Qdrant Configuration
QDRANT_URL=https://your-qdrant-url.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=documents

# Groq API (for RAG)
GROQ_API_KEY=your_groq_api_key_here
EOF
```

## 🗑️ DELETE - Cache & Generated Files:

```bash
# Python cache files
rm -rf backend/__pycache__
rm -rf backend/services/__pycache__
rm -rf backend/utils/__pycache__

# Virtual environments
rm -rf backend/venv
rm -rf .venv

# Database files (will be regenerated)
rm -rf backend/chroma_db

# Node modules if any
rm -rf frontend/node_modules
rm -rf node_modules
```

## 🗑️ DELETE - Unrelated/Extra Files:

```bash
# Delete unrelated chrome extension
rm -rf chrome-extension

# Delete temporary test files
rm test_finance_doc.txt
rm test_legal_doc.txt

# Delete redundant documentation (keep only essential)
rm FIXES_APPLIED.md
rm LATEST_FIXES.md
rm MIGRATION_STATUS.md
rm MIGRATION_AWS_QDRANT.md
rm FRIEND_QUICKSTART.md
rm MAC_SETUP.md
rm BOTPRESS_INTEGRATION_PLAN.md
rm SPLINE_INTEGRATION_PLAN.md

# Clean up package-lock.json at root (frontend has its own)
rm package-lock.json
rm backend/package-lock.json
```

## ✅ KEEP THESE FILES:

```
✅ README.md (main documentation)
✅ backend/
  ✅ main.py
  ✅ config.py
  ✅ requirements.txt
  ✅ start.sh
  ✅ services/
  ✅ utils/
  ✅ sample_docs/
  ✅ .gitignore
  ✅ README.md
  ✅ QUICKSTART.md
  ✅ DEMO_SCRIPT.md
  ✅ test_*.py
  ✅ Postman_Collection.json
✅ frontend/
✅ docker-compose.yml
✅ API_TESTING_GUIDE.md
✅ DEPLOYMENT_GUIDE.md
✅ FRONTEND_MASTER_PROMPT.md
✅ HOW_IT_WORKS.md
✅ PROJECT_STATUS.md
✅ TECHNICAL_EXPLAINED.md
✅ PRESENTATION_SCRIPT.md (new)
```

## 🚀 One-Command Cleanup:

```bash
# Run this from project root
cd "/Users/rohitbinoj/bits hack"

# Backup .env first
cp backend/.env backend/.env.backup

# Delete sensitive & unnecessary files
rm backend/.env && \
rm -rf backend/__pycache__ backend/services/__pycache__ backend/utils/__pycache__ && \
rm -rf backend/venv .venv && \
rm -rf backend/chroma_db && \
rm -rf chrome-extension && \
rm -f test_finance_doc.txt test_legal_doc.txt && \
rm -f package-lock.json backend/package-lock.json && \
rm -f FIXES_APPLIED.md LATEST_FIXES.md MIGRATION_STATUS.md MIGRATION_AWS_QDRANT.md && \
rm -f FRIEND_QUICKSTART.md MAC_SETUP.md BOTPRESS_INTEGRATION_PLAN.md SPLINE_INTEGRATION_PLAN.md && \
echo "✅ Cleanup complete!"
```

## 📝 Update .gitignore:

Make sure your `.gitignore` includes:
```
# Environment variables
.env
*.env
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.venv/

# Database
chroma_db/
*.sqlite3

# Node
node_modules/
package-lock.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## ⚡ Before Submission Checklist:

- [ ] Deleted `.env` file
- [ ] Created `.env.example` with placeholder values
- [ ] Deleted all `__pycache__` folders
- [ ] Deleted `venv/` and `.venv/`
- [ ] Deleted `chroma_db/`
- [ ] Deleted unrelated files
- [ ] Updated `.gitignore`
- [ ] Tested that setup works from scratch
- [ ] Updated README.md with clear setup instructions
- [ ] Created PRESENTATION_SCRIPT.md

## 🔒 Security Note:

**NEVER commit your `.env` file!** It contains:
- AWS credentials
- Qdrant API keys
- Groq API keys

If you accidentally committed it:
```bash
# Remove from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch backend/.env' \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

---

**After cleanup, your repo will be:**
- ✅ Clean and professional
- ✅ Secure (no leaked credentials)
- ✅ Lightweight (no cache/build files)
- ✅ Ready for judges to clone and run
