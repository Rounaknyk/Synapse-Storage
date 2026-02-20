from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import uuid

# Import services
from services.embedding import embedding_service
from services.storage import storage_service
from services.search import search_service
from services.classifier import classifier_service
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

class DownloadResponse(BaseModel):
    file_name: str
    bucket_name: str
    download_url: str

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
    
    # Initialize ChromaDB collection
    print("\n🔍 Initializing ChromaDB collection...")
    search_service.initialize_collection()
    
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
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.txt', '.md']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Only PDF, TXT, and MD files are allowed."
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
        
        # Store in ChromaDB
        print(f"💾 Indexing in ChromaDB...")
        doc_id = f"{bucket_name}_{file.filename}_{uuid.uuid4().hex[:8]}"
        metadata = {
            "file_name": file.filename,
            "bucket_name": bucket_name,
            "document_type": document_type,
            "upload_time": datetime.now().isoformat()
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
        collection = search_service.collection
        if collection:
            data = collection.get()
            return {
                "total_documents": len(data['ids']) if data['ids'] else 0,
                "documents": data['metadatas'] if data['metadatas'] else []
            }
        return {"total_documents": 0, "documents": []}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
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
