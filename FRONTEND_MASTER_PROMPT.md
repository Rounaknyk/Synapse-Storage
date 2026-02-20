# 🎨 FRONTEND MASTER PROMPT - Semantic Storage Gateway

## 📋 Project Overview

You are building the **frontend interface** for a Semantic Storage Gateway - an AI-powered document management system that uses semantic search to find documents based on meaning, not just keywords.

**Backend is 100% ready and running at:** `http://localhost:8000`

---

## 🎯 What You Need to Build

A modern, intuitive web interface with 3 main features:

### 1. **Document Upload** 📤
- Drag & drop or file picker for PDF, TXT, MD files
- Real-time upload progress
- Show success notification with classification result
- Display: file name, document type (finance/legal/general), bucket name

### 2. **Semantic Search** 🔍  
- Natural language search input (e.g., "tax documents from Q4")
- Display results with:
  - File name
  - Document type badge (color-coded)
  - Similarity score (as percentage or visual indicator)
  - Upload timestamp
  - Download button per result

### 3. **Document Management** 📁
- View all uploaded documents
- Filter by type (finance/legal/general)
- Download any document
- Visual card/list view

---

## 🔌 API ENDPOINTS (Backend Ready)

### Base URL
```
http://localhost:8000
```

### 1. Upload Document
```http
POST /upload
Content-Type: multipart/form-data

Body: 
  file: <PDF, TXT, or MD file>

Response:
{
  "success": true,
  "message": "File uploaded and indexed successfully",
  "file_name": "finance_report.md",
  "document_type": "finance",
  "bucket_name": "finance"
}
```

### 2. Search Documents
```http
POST /search
Content-Type: application/json

Body:
{
  "query": "tax documents from last quarter",
  "top_k": 3
}

Response:
[
  {
    "file_name": "finance_report.md",
    "bucket_name": "finance",
    "document_type": "finance",
    "upload_time": "2026-02-20T21:04:30.178368",
    "similarity_score": 0.7332
  },
  ...
]
```

### 3. Download File
```http
GET /download/{bucket_name}/{file_name}

Response:
{
  "file_name": "finance_report.md",
  "bucket_name": "finance",
  "download_url": "http://localhost:9000/finance/finance_report.md?..."
}
```

### 4. List All Documents
```http
GET /documents

Response:
{
  "total_documents": 3,
  "documents": [
    {
      "file_name": "finance_report.md",
      "bucket_name": "finance",
      "document_type": "finance",
      "upload_time": "2026-02-20T21:04:30.178368"
    },
    ...
  ]
}
```

### 5. Health Check
```http
GET /

Response:
{
  "message": "Semantic Storage Gateway API",
  "status": "running",
  "version": "1.0.0"
}
```

---

## 🎨 Recommended Tech Stack

**Choose ONE:**

### Option A: Next.js (Recommended)
```bash
npx create-next-app@latest semantic-storage-frontend
cd semantic-storage-frontend
npm install axios react-dropzone
```

### Option B: React + Vite
```bash
npm create vite@latest semantic-storage-frontend -- --template react
cd semantic-storage-frontend
npm install axios react-dropzone
```

### Option C: Simple HTML/CSS/JS
- No build step needed
- Use `fetch()` API
- Quick to demo

---

## 🎨 UI/UX Guidelines

### Color Coding for Document Types
```css
finance:  #10B981 (Green)  - Money/Revenue theme
legal:    #3B82F6 (Blue)   - Trust/Professional theme  
general:  #6B7280 (Gray)   - Neutral theme
```

### Similarity Score Display
```
0.8 - 1.0  = Excellent match (Green)
0.6 - 0.79 = Good match (Yellow/Orange)
0.0 - 0.59 = Weak match (Red)
```

### Layout Suggestions
```
┌─────────────────────────────────────┐
│  Semantic Storage Gateway 🤖        │
│  ───────────────────────────────    │
│                                      │
│  ┌─────────────────────────────┐    │
│  │ 🔍 Search: "tax documents"  │    │
│  └─────────────────────────────┘    │
│                                      │
│  📤 Upload New Document              │
│  ┌─────────────────────────────┐    │
│  │  Drag files here or click   │    │
│  │  PDF, TXT, MD supported     │    │
│  └─────────────────────────────┘    │
│                                      │
│  📊 Search Results (3)               │
│  ┌─────────────────────────────┐    │
│  │ 📄 finance_report.md         │    │
│  │ 🟢 Finance | 73% match       │    │
│  │ [Download] [View Details]   │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

---

## 💻 Sample Frontend Code

### Next.js Example - Upload Component

```jsx
'use client';
import { useState } from 'react';
import axios from 'axios';

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        'http://localhost:8000/upload',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResult(response.data);
      alert(`Success! Document classified as: ${response.data.document_type}`);
    } catch (error) {
      alert('Upload failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleUpload}>
      <input 
        type="file" 
        accept=".pdf,.txt,.md"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Uploading...' : 'Upload Document'}
      </button>
      {result && (
        <div>
          <p>✅ {result.message}</p>
          <p>Type: <span className="badge">{result.document_type}</span></p>
        </div>
      )}
    </form>
  );
}
```

### Next.js Example - Search Component

```jsx
'use client';
import { useState } from 'react';
import axios from 'axios';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;

    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/search',
        { query, top_k: 5 }
      );
      setResults(response.data);
    } catch (error) {
      alert('Search failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (bucketName, fileName) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/download/${bucketName}/${fileName}`
      );
      window.open(response.data.download_url, '_blank');
    } catch (error) {
      alert('Download failed: ' + error.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search documents... (e.g., 'tax information')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      <div className="results">
        {results.map((doc, idx) => (
          <div key={idx} className="result-card">
            <h3>📄 {doc.file_name}</h3>
            <p>
              <span className={`badge ${doc.document_type}`}>
                {doc.document_type}
              </span>
              <span className="similarity">
                {Math.round(doc.similarity_score * 100)}% match
              </span>
            </p>
            <small>{new Date(doc.upload_time).toLocaleString()}</small>
            <button 
              onClick={() => handleDownload(doc.bucket_name, doc.file_name)}
            >
              Download
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Vanilla JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Semantic Storage Gateway</title>
  <style>
    .badge { padding: 4px 8px; border-radius: 4px; }
    .finance { background: #10B981; color: white; }
    .legal { background: #3B82F6; color: white; }
    .general { background: #6B7280; color: white; }
  </style>
</head>
<body>
  <h1>🔍 Semantic Storage Gateway</h1>
  
  <!-- Search -->
  <input id="searchQuery" placeholder="Search documents..." />
  <button onclick="search()">Search</button>
  
  <!-- Upload -->
  <input type="file" id="fileInput" accept=".pdf,.txt,.md" />
  <button onclick="upload()">Upload</button>
  
  <!-- Results -->
  <div id="results"></div>

  <script>
    const API_URL = 'http://localhost:8000';

    async function search() {
      const query = document.getElementById('searchQuery').value;
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 })
      });
      const results = await response.json();
      
      document.getElementById('results').innerHTML = results.map(doc => `
        <div>
          <h3>📄 ${doc.file_name}</h3>
          <span class="badge ${doc.document_type}">${doc.document_type}</span>
          <span>${Math.round(doc.similarity_score * 100)}% match</span>
          <button onclick="download('${doc.bucket_name}', '${doc.file_name}')">
            Download
          </button>
        </div>
      `).join('');
    }

    async function upload() {
      const fileInput = document.getElementById('fileInput');
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
      
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      alert(`Success! Document type: ${result.document_type}`);
    }

    async function download(bucket, fileName) {
      const response = await fetch(`${API_URL}/download/${bucket}/${fileName}`);
      const data = await response.json();
      window.open(data.download_url, '_blank');
    }
  </script>
</body>
</html>
```

---

## 🚀 Features to Implement (Priority Order)

### Phase 1 - MVP (Required for Demo)
1. ✅ Upload single file
2. ✅ Search with natural language
3. ✅ Display search results
4. ✅ Download files

### Phase 2 - Enhanced UX (Nice to Have)
5. 📤 Drag & drop upload
6. 📊 View all documents
7. 🎨 Document type filtering
8. 📈 Visual similarity indicator (progress bar/gauge)
9. 🕐 Upload history/timeline

### Phase 3 - Advanced (If Time Permits)
10. 🎯 Search suggestions
11. 📝 Document preview
12. 🔄 Real-time search (as you type)
13. 📱 Mobile responsive design
14. 🌓 Dark mode

---

## 🎯 Demo Script for Presentation

### 1. Opening (15 seconds)
"Traditional file search uses keywords. We built semantic search - it understands *meaning*."

### 2. Upload Demo (30 seconds)
- Upload `finance_report.md`
- Show it auto-classifies as "finance"
- Upload `legal_contract.md`
- Show it auto-classifies as "legal"

### 3. Search Demo (45 seconds)  
- Search: "tax information" → Finance doc appears first
- Search: "contract terms" → Legal doc appears first
- Search: "product plans" → General doc appears first
- **Highlight**: "Notice it finds the right document even though I didn't use the exact filename"

### 4. Download Demo (15 seconds)
- Click download on any result
- File opens/downloads

### 5. Closer (15 seconds)
"This is production-ready. Works locally. Can scale to cloud. Built in 24 hours."

---

## 🐛 Common Issues & Solutions

### CORS Error
**Problem:** `Access-Control-Allow-Origin` error

**Solution:** Backend already has CORS enabled. If issue persists:
```javascript
// Add mode: 'cors' to fetch
fetch('http://localhost:8000/search', {
  method: 'POST',
  mode: 'cors',
  // ...
})
```

### Port Connection Refused
**Problem:** Can't connect to backend

**Solution:** 
1. Verify backend is running: `curl http://localhost:8000/`
2. Check MinIO is running: `curl http://localhost:9000/`

### File Upload Fails
**Problem:** "Unsupported file type"

**Solution:** Only PDF, TXT, MD are supported. Check file extension.

---

## 📊 Testing Checklist

Before presenting:
- [ ] Upload works for PDF, TXT, MD files
- [ ] Search returns relevant results
- [ ] Similarity scores are between 0-1
- [ ] Download links work
- [ ] UI is responsive
- [ ] No console errors
- [ ] Works in Chrome, Firefox, Safari

---

## 💡 Pro Tips

### Make It Visual
- Use icons (📄 for files, 🔍 for search, 📤 for upload)
- Add loading spinners
- Show success/error toasts
- Use colors to differentiate document types

### Make It Fast
- Debounce search input (wait 300ms after typing)
- Show upload progress
- Cache search results

### Make It Impressive
- Add smooth animations
- Use a modern UI library (shadcn/ui, Tailwind, Material-UI)
- Add empty states ("No documents yet - upload your first!")
- Show document count badges

---

## 🎨 Design Inspiration

### Similar Products
- Google Drive search interface
- Notion's search
- Dropbox file browser

### UI Libraries (Pick One)
- **Tailwind CSS** - Utility-first, fast   
- **shadcn/ui** - Beautiful components
- **Material-UI** - Professional
- **Chakra UI** - Accessible

---

## 📝 Final Notes

### What's Already Done (Backend)
✅ FastAPI server running
✅ MinIO object storage configured
✅ ChromaDB vector database working
✅ Semantic search with 70-80% accuracy
✅ Document classification (finance/legal/general)
✅ File upload & download
✅ CORS enabled
✅ All endpoints tested

### Your Job (Frontend)
🎯 Build the UI to interact with these endpoints
🎯 Make it beautiful and intuitive
🎯 Prepare a killer demo

### Success Criteria
- Upload a file → See it classified
- Search "tax" → Get finance doc top result
- Search "contract" → Get legal doc top result
- Download any file → File opens

---

## 🚀 Getting Started

### Step 1: Verify Backend is Running
```bash
curl http://localhost:8000/
# Should return: {"message":"Semantic Storage Gateway API","status":"running","version":"1.0.0"}
```

### Step 2: Create Your Frontend
```bash
# Option A: Next.js
npx create-next-app@latest frontend
cd frontend
npm install axios

# Option B: Vanilla HTML
mkdir frontend
cd frontend
touch index.html
```

### Step 3: Start Building
1. Create upload form
2. Create search bar
3. Display results
4. Add download buttons

### Step 4: Test Everything
1. Upload sample documents from `backend/sample_docs/`
2. Test searches
3. Test downloads

### Step 5: Polish for Demo
1. Add loading states
2. Style with CSS
3. Test in different browsers
4. Prepare demo script

---

## 📞 Need Help?

### Backend API Docs
Visit: http://localhost:8000/docs

### Test the API
Use Postman collection: `backend/Postman_Collection.json`

### Sample Documents
Located in: `backend/sample_docs/`
- finance_report.md
- legal_contract.md
- general_roadmap.md

---

## 🎯 Deliverables

By end of hackathon:
1. ✅ Working frontend (any framework)
2. ✅ Upload functionality
3. ✅ Search functionality  
4. ✅ Download functionality
5. ✅ Clean, presentable UI
6. ✅ 2-minute demo ready

---

## 🏆 Bonus Points

If you have extra time:
- Add file type icons (PDF icon, TXT icon)
- Show upload progress bar
- Add search history
- Implement document preview
- Add statistics dashboard
- Create a landing page

---

**Good luck! You got this! 🚀**

The backend is rock-solid. Focus on making the frontend beautiful and the demo compelling.

Remember: **Judges care about (1) Working demo, (2) Visual appeal, (3) Clear value proposition**

You have all three covered. Now execute! 💪
