import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MinIO Configuration
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # Buckets
    BUCKETS = ["finance", "legal", "general"]
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = "./chroma_db"
    CHROMA_COLLECTION_NAME = "documents"
    
    # Embedding Model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Classification Keywords
    CLASSIFICATION_KEYWORDS = {
        "finance": ["invoice", "tax", "revenue", "balance", "payment", "transaction", "financial"],
        "legal": ["agreement", "contract", "clause", "terms", "legal", "liability", "party"]
    }

settings = Settings()
