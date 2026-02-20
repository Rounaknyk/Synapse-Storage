from sentence_transformers import SentenceTransformer
from config import settings

class EmbeddingService:
    def __init__(self):
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> list:
        """Generate embedding vector from text"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def generate_query_embedding(self, query: str) -> list:
        """Generate embedding for search query"""
        return self.generate_embedding(query)

# Singleton instance
embedding_service = EmbeddingService()
