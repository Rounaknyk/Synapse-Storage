import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_FINANCE_BUCKET = os.getenv("AWS_S3_FINANCE_BUCKET", "synapse-finance-prod")
    AWS_S3_LEGAL_BUCKET = os.getenv("AWS_S3_LEGAL_BUCKET", "synapse-legal-prod")
    AWS_S3_GENERAL_BUCKET = os.getenv("AWS_S3_GENERAL_BUCKET", "synapse-general-prod")
    
    # Bucket mapping (category → actual bucket name)
    BUCKETS = {
        "finance": AWS_S3_FINANCE_BUCKET,
        "legal": AWS_S3_LEGAL_BUCKET,
        "general": AWS_S3_GENERAL_BUCKET
    }
    
    # Qdrant Configuration
    QDRANT_URL = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    
    # Embedding Model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2
    
    # Classification Keywords
    CLASSIFICATION_KEYWORDS = {
        "finance": ["invoice", "tax", "revenue", "balance", "payment", "transaction", "financial"],
        "legal": ["agreement", "contract", "clause", "terms", "legal", "liability", "party"]
    }

settings = Settings()
