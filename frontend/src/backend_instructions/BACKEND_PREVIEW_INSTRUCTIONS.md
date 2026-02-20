# 🔧 Backend Instructions — Smart Document Preview

**Feature:** Return a `preview` text snippet inside every search result so the frontend can show users *why* a document matched their query.

---

## 1 · What the Frontend Expects

The `/search` endpoint must add a `preview` field to every result object:

```json
[
  {
    "file_name": "Q4_finances.pdf",
    "bucket_name": "finance",
    "document_type": "finance",
    "upload_time": "2026-02-20T21:04:30.178368",
    "similarity_score": 0.7332,
    "preview": "...Revenue: $100k, Tax: $20k, EBITDA: $34k..."
  }
]
```

**Rules:**
- Max **200 characters** of extracted text
- Wrap with `...` on both sides (e.g. `...snippet text...`)
- If no text is stored, return `""` (empty string) — **never omit the field**
- Should be the most *relevant* portion of the document, not just the first 200 chars (see options below)

---

## 2 · Where to Store the Text Snippet

The extracted document text is already available at upload time (`extracted_text` in `main.py → upload_file`).  
You need to **store a snippet in ChromaDB metadata** so it can be retrieved during search — no extra DB call needed.

### Step A — Store snippet at upload time (`main.py`)

In the `upload_file` endpoint, after `extracted_text` is obtained, compute and add the snippet to `metadata`:

```python
# After: extracted_text = text_extractor.extract_text(...)

# Compute preview snippet (first 200 chars of meaningful content)
clean_text = ' '.join(extracted_text.split())  # collapse whitespace
preview_snippet = clean_text[:200].rsplit(' ', 1)[0] + '...' if len(clean_text) > 200 else clean_text

# Then add to metadata dict:
metadata = {
    "file_name": file.filename,
    "bucket_name": bucket_name,
    "document_type": document_type,
    "upload_time": datetime.now().isoformat(),
    "preview": preview_snippet,   # ← ADD THIS LINE
}
```

> **Note:** ChromaDB metadata values must be `str | int | float | bool`. The preview string is fine.

---

### Step B — Return snippet in search results (`services/search.py`)

In `search_similar()` (or wherever results are assembled from ChromaDB), add `preview` from the stored metadata:

```python
# Inside your results loop, wherever you build each result dict:
result = {
    "file_name": metadata.get("file_name", ""),
    "bucket_name": metadata.get("bucket_name", ""),
    "document_type": metadata.get("document_type", "general"),
    "upload_time": metadata.get("upload_time", ""),
    "similarity_score": round(score, 4),
    "preview": metadata.get("preview", ""),   # ← ADD THIS LINE
}
```

---

### Step C — Update the Pydantic model (`main.py`)

Add `preview` to the `SearchResult` model so FastAPI includes it in the response schema:

```python
class SearchResult(BaseModel):
    file_name: str
    bucket_name: str
    document_type: str
    upload_time: str
    similarity_score: float
    preview: str = ""   # ← ADD THIS LINE (default empty string)
```

---

## 3 · Optional Enhancement — Query-Relevant Snippet

Instead of always returning the *first* 200 chars, return the sentence/chunk that is **closest to the search query**. This makes the preview more meaningful ("Look, it found the exact section!").

```python
import re

def extract_relevant_preview(text: str, query: str, max_len: int = 200) -> str:
    """Return the sentence most relevant to the query."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    query_words = set(query.lower().split())
    
    best_sentence = ""
    best_score = -1
    for sentence in sentences:
        score = sum(1 for w in query_words if w in sentence.lower())
        if score > best_score:
            best_score = score
            best_sentence = sentence
    
    snippet = best_sentence.strip()
    if len(snippet) > max_len:
        snippet = snippet[:max_len].rsplit(' ', 1)[0]
    return f"...{snippet}..." if snippet else ""
```

Call it at upload time instead of the simple slice:
```python
preview_snippet = extract_relevant_preview(extracted_text, "")  # store full best sentence
# OR store full text and compute at search time using the query
```

---

## 4 · Testing

After making the changes, test with:

```bash
# Upload a doc
curl -X POST http://localhost:8000/upload -F "file=@backend/sample_docs/finance_report.md"

# Search and verify preview field exists
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "tax", "top_k": 3}'
```

Expected: each result object has a non-empty `"preview"` field.

---

## 5 · Checklist

- [ ] `metadata` dict in `upload_file` includes `"preview"` key
- [ ] `SearchResult` Pydantic model has `preview: str = ""`
- [ ] `search_similar()` maps `metadata["preview"]` → result dict
- [ ] Old documents (uploaded before this change) return `preview: ""` gracefully
- [ ] Preview is max ~200 chars, wrapped with `...`
