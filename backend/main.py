from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import uuid

# Import services
from services.embedding import embedding_service
from services.s3_storage import s3_storage_service as storage_service
from services.qdrant_search import qdrant_search_service as search_service
from services.classifier import classifier_service
from services.gemini_service import gemini_service
from utils.text_extractor import text_extractor

# Initialize FastAPI app
app = FastAPI(
    title="Semantic Storage Gateway",
    description="AI-powered document storage and search system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    min_similarity: float = 0.0  # Filter results below this threshold (0.0 to 1.0)

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_name: str
    document_type: str
    bucket_name: str

class SearchResult(BaseModel):
    file_name: str
    bucket_name: str
    document_type: str
    upload_time: str
    similarity_score: float
    preview: str = ""  # Document text preview

class DownloadResponse(BaseModel):
    file_name: str
    bucket_name: str
    download_url: str

class DeleteRequest(BaseModel):
    bucket_name: str
    file_name: str

class BatchDeleteRequest(BaseModel):
    files: list[DeleteRequest]

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("\n" + "="*50)
    print("🚀 Starting Semantic Storage Gateway")
    print("="*50 + "\n")
    
    # Initialize MinIO buckets
    print("📦 Initializing MinIO buckets...")
    storage_service.initialize_buckets()
    
    # Skip Qdrant initialization at startup (will initialize on first use)
    print("\n🔍 Qdrant will initialize on first use...")
    
    print("\n" + "="*50)
    print("✅ System ready!")
    print("="*50 + "\n")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Semantic Storage Gateway API",
        "status": "running",
        "version": "1.0.0"
    }

# Upload endpoint
@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document (PDF, TXT, MD)
    - Extracts text
    - Generates embedding
    - Classifies document type
    - Stores in MinIO
    - Indexes in ChromaDB
    """
    try:
        # Validate file extension
        ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.pptx', '.ppt'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text
        print(f"📄 Extracting text from {file.filename}...")
        extracted_text = text_extractor.extract_text(file_content, file_extension)
        
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from file"
            )
        
        # Classify document
        print(f"🏷️  Classifying document...")
        document_type = classifier_service.classify_document(extracted_text)
        bucket_name = document_type
        
        # Generate embedding
        print(f"🧠 Generating embedding...")
        embedding = embedding_service.generate_embedding(extracted_text)
        
        # Upload to MinIO
        print(f"☁️  Uploading to MinIO bucket: {bucket_name}...")
        upload_success = storage_service.upload_file(
            file_content=file_content,
            file_name=file.filename,
            bucket_name=bucket_name,
            content_type=file.content_type or "application/octet-stream"
        )
        
        if not upload_success:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        
        # Generate preview snippet (first 200 chars) and RAG content (first 1500 chars)
        clean_text = ' '.join(extracted_text.split())  # collapse whitespace
        preview_snippet = clean_text[:200].rsplit(' ', 1)[0] + '...' if len(clean_text) > 200 else clean_text
        rag_content = clean_text[:1500]  # full context for RAG generation
        
        # Store in ChromaDB
        print(f"💾 Indexing in ChromaDB...")
        doc_id = f"{bucket_name}_{file.filename}_{uuid.uuid4().hex[:8]}"
        metadata = {
            "file_name": file.filename,
            "bucket_name": bucket_name,
            "document_type": document_type,
            "upload_time": datetime.now().isoformat(),
            "preview": preview_snippet,
            "content": rag_content,
        }
        
        index_success = search_service.add_document(doc_id, embedding, metadata)
        
        if not index_success:
            raise HTTPException(
                status_code=500,
                detail="Failed to index document"
            )
        
        print(f"✅ Successfully processed {file.filename}\n")
        
        return UploadResponse(
            success=True,
            message="File uploaded and indexed successfully",
            file_name=file.filename,
            document_type=document_type,
            bucket_name=bucket_name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Batch upload endpoint
@app.post("/upload-batch")
async def upload_batch(files: list[UploadFile] = File(...)):
    """
    Upload multiple documents at once
    - Processes each file independently
    - Returns results for all files (including failures)
    """
    results = []
    errors = []
    
    for file in files:
        try:
            # Validate file extension
            ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.pptx', '.ppt'}
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                errors.append({
                    "file_name": file.filename,
                    "error": "Unsupported file type"
                })
                continue
            
            # Read file content
            file_content = await file.read()
            
            # Extract text
            print(f"📄 [{file.filename}] Extracting text...")
            extracted_text = text_extractor.extract_text(file_content, file_extension)
            
            if not extracted_text:
                errors.append({
                    "file_name": file.filename,
                    "error": "Could not extract text"
                })
                continue
            
            # Classify document
            print(f"🏷️  [{file.filename}] Classifying...")
            document_type = classifier_service.classify_document(extracted_text)
            bucket_name = document_type
            
            # Generate embedding
            print(f"🧠 [{file.filename}] Generating embedding...")
            embedding = embedding_service.generate_embedding(extracted_text)
            
            # Upload to MinIO
            print(f"☁️  [{file.filename}] Uploading to {bucket_name}...")
            upload_success = storage_service.upload_file(
                file_content=file_content,
                file_name=file.filename,
                bucket_name=bucket_name
            )
            
            if not upload_success:
                errors.append({
                    "file_name": file.filename,
                    "error": "Failed to upload to storage"
                })
                continue
            
            # Generate preview snippet
            clean_text = ' '.join(extracted_text.split())
            preview_snippet = clean_text[:200].rsplit(' ', 1)[0] + '...' if len(clean_text) > 200 else clean_text
            
            # Index in ChromaDB
            print(f"🔍 [{file.filename}] Indexing...")
            doc_id = f"{bucket_name}_{file.filename}_{uuid.uuid4().hex[:8]}"
            metadata = {
                "file_name": file.filename,
                "bucket_name": bucket_name,
                "document_type": document_type,
                "upload_time": datetime.now().isoformat(),
                "preview": preview_snippet
            }
            
            index_success = search_service.add_document(doc_id, embedding, metadata)
            
            if not index_success:
                errors.append({
                    "file_name": file.filename,
                    "error": "Failed to index document"
                })
                continue
            
            print(f"✅ [{file.filename}] Success!")
            results.append({
                "success": True,
                "file_name": file.filename,
                "document_type": document_type,
                "bucket_name": bucket_name
            })
        
        except Exception as e:
            print(f"❌ [{file.filename}] Error: {e}")
            errors.append({
                "file_name": file.filename,
                "error": str(e)
            })
    
    return {
        "total_files": len(files),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

# Search endpoint
@app.post("/search", response_model=list[SearchResult])
async def search_documents(request: SearchRequest):
    """
    Search for documents using natural language query
    - Converts query to embedding
    - Performs similarity search
    - Returns top K results filtered by minimum similarity
    """
    try:
        print(f"🔍 Searching for: '{request.query}'...")
        
        # Generate query embedding
        query_embedding = embedding_service.generate_query_embedding(request.query)
        
        # Search in ChromaDB
        results = search_service.search_similar(query_embedding, top_k=request.top_k)
        
        # Filter by minimum similarity threshold
        if request.min_similarity > 0:
            results = [r for r in results if r['similarity_score'] >= request.min_similarity]
            print(f"📊 Filtered to {len(results)} results above {request.min_similarity} similarity")
        
        print(f"✅ Found {len(results)} results\n")
        
        return results
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

# RAG Search endpoint — Retrieve → Augment → Generate
class SmartSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.0

class SmartSearchResponse(BaseModel):
    query: str
    rag_answer: str          # Gemini-generated answer grounded in retrieved docs
    sources: list            # The retrieved documents used as context

@app.post("/search/smart", response_model=SmartSearchResponse)
async def smart_search(request: SmartSearchRequest):
    """
    Full RAG pipeline:
      1. RETRIEVE  — embed query → vector search → top-k document chunks
      2. AUGMENT   — attach retrieved text as context
      3. GENERATE  — Gemini reads context and writes a grounded answer
    """
    try:
        print(f"\n🔍 RAG search: '{request.query}'")

        # ── Step 1: RETRIEVE ──────────────────────────────────────
        query_embedding = embedding_service.generate_query_embedding(request.query)
        results = search_service.search_similar(query_embedding, top_k=request.top_k)

        if request.min_similarity > 0:
            results = [r for r in results if r["similarity_score"] >= request.min_similarity]

        print(f"📥 Retrieved {len(results)} document(s) for RAG context")

        # ── Step 2: AUGMENT — fetch FULL document text from MinIO ────
        context_chunks = []
        for r in results:
            file_name = r["file_name"]
            bucket_name = r["bucket_name"]
            document_type = r["document_type"]

            # Download raw bytes from MinIO
            file_bytes = storage_service.download_file(bucket_name, file_name)
            if file_bytes:
                ext = os.path.splitext(file_name)[1].lower()
                full_text = text_extractor.extract_text(file_bytes, ext)
                # Collapse whitespace but keep full content
                full_text = ' '.join(full_text.split())
                print(f"  📄 {file_name}: {len(full_text)} chars extracted for RAG")
            else:
                # Fallback to stored content if MinIO download fails
                full_text = r.get("content", r.get("preview", ""))
                print(f"  ⚠️  {file_name}: MinIO download failed, using stored excerpt")

            if full_text:
                context_chunks.append({
                    "file_name": file_name,
                    "document_type": document_type,
                    "content": full_text,
                })

        # ── Step 3: GENERATE ──────────────────────────────────────
        rag_answer = gemini_service.generate_rag_answer(request.query, context_chunks)


        print(f"✅ RAG complete — {len(results)} sources, answer: {len(rag_answer)} chars\n")

        return SmartSearchResponse(
            query=request.query,
            rag_answer=rag_answer,
            sources=results,
        )

    except Exception as e:
        print(f"❌ RAG search error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG search failed: {str(e)}")

# Download endpoint
@app.get("/download/{bucket_name}/{file_name}", response_model=DownloadResponse)
async def download_file(bucket_name: str, file_name: str):
    """
    Generate presigned URL for file download
    """
    try:
        print(f"🔗 Generating download URL for {file_name} from {bucket_name}...")
        
        # Generate presigned URL
        download_url = storage_service.generate_presigned_url(bucket_name, file_name)
        
        if not download_url:
            raise HTTPException(
                status_code=404,
                detail="File not found or unable to generate download URL"
            )
        
        print(f"✅ Download URL generated\n")
        
        return DownloadResponse(
            file_name=file_name,
            bucket_name=bucket_name,
            download_url=download_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Download error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(e)}"
        )

# List all documents (bonus endpoint for debugging)
@app.get("/documents")
async def list_documents():
    """
    List all indexed documents
    """
    try:
        documents = search_service.get_all_documents()
        return {
            "total_documents": len(documents),
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )

# Delete single document endpoint
@app.delete("/documents/{bucket_name}/{file_name}")
async def delete_document(bucket_name: str, file_name: str):
    """
    Delete a document from both MinIO storage and ChromaDB index
    """
    try:
        print(f"🗑️  Deleting {file_name} from {bucket_name}...")
        
        # Delete from ChromaDB
        search_success = search_service.delete_document(bucket_name, file_name)
        
        # Delete from MinIO
        storage_success = storage_service.delete_file(bucket_name, file_name)
        
        if search_success or storage_success:
            return {
                "success": True,
                "message": f"Successfully deleted {file_name}",
                "file_name": file_name,
                "bucket_name": bucket_name,
                "deleted_from_search": search_success,
                "deleted_from_storage": storage_success
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Document not found in storage or search index"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )

# Batch delete endpoint
@app.post("/documents/delete-batch")
async def delete_documents_batch(request: BatchDeleteRequest):
    """
    Delete multiple documents from both S3 storage and Qdrant index
    """
    try:
        print(f"🗑️  Batch deleting {len(request.files)} documents...")
        
        # Convert to list of dicts for service methods
        files_list = [
            {"bucket_name": f.bucket_name, "file_name": f.file_name}
            for f in request.files
        ]
        
        # Delete from ChromaDB
        search_results = search_service.delete_documents(files_list)
        
        # Delete from MinIO
        storage_results = storage_service.delete_files(files_list)
        
        # Combine results
        combined_results = []
        for i, file_info in enumerate(files_list):
            combined_results.append({
                "file_name": file_info["file_name"],
                "bucket_name": file_info["bucket_name"],
                "deleted_from_search": search_results[i]["success"],
                "deleted_from_storage": storage_results[i]["success"],
                "success": search_results[i]["success"] or storage_results[i]["success"]
            })
        
        successful = sum(1 for r in combined_results if r["success"])
        
        print(f"✅ Batch delete complete: {successful}/{len(request.files)} successful")
        
        return {
            "total_files": len(request.files),
            "successful": successful,
            "failed": len(request.files) - successful,
            "results": combined_results
        }
    
    except Exception as e:
        print(f"❌ Batch delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete documents: {str(e)}"
        )

# Reset collection endpoint (for development)
@app.post("/admin/reset-collection")
async def reset_collection():
    """
    Reset the ChromaDB collection (WARNING: Deletes all indexed documents)
    """
    try:
        success = search_service.reset_collection()
        if success:
            return {
                "success": True,
                "message": "Collection reset successfully. Please re-upload your documents."
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to reset collection"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting collection: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
