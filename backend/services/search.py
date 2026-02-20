import chromadb
from config import settings
from datetime import datetime

class SearchService:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
            self.collection = None
            print(f"ChromaDB initialized at {settings.CHROMA_PERSIST_DIR}")
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            # Fallback to default initialization
            self.client = chromadb.PersistentClient()
            self.collection = None
    
    def initialize_collection(self):
        """Initialize or get existing ChromaDB collection"""
        try:
            # Use cosine similarity for better semantic search
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Document embeddings for semantic search", "hnsw:space": "cosine"}
            )
            print(f"✓ ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' ready")
        except Exception as e:
            print(f"Error initializing collection: {e}")
            # Fallback without metadata
            try:
                self.collection = self.client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME
                )
                print(f"✓ ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' ready (fallback)")
            except Exception as e2:
                print(f"Error in fallback: {e2}")
    
    def reset_collection(self):
        """Delete and recreate collection with optimal settings"""
        try:
            # Delete existing collection
            self.client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
            print(f"Deleted existing collection '{settings.CHROMA_COLLECTION_NAME}'")
            # Recreate with cosine similarity
            self.initialize_collection()
            return True
        except Exception as e:
            print(f"Error resetting collection: {e}")
            return False
    
    def add_document(self, doc_id: str, embedding: list, metadata: dict):
        """Add document embedding to ChromaDB"""
        try:
            self.collection.add(
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"Error adding document to ChromaDB: {e}")
            return False
    
    def search_similar(self, query_embedding: list, top_k: int = 3):
        """Perform similarity search"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['metadatas'] and len(results['metadatas'][0]) > 0:
                for i, metadata in enumerate(results['metadatas'][0]):
                    # Get distance from ChromaDB
                    distance = results['distances'][0][i] if results['distances'] else 0
                    
                    # Convert distance to similarity score (0-1, where 1 is most similar)
                    # For cosine distance: distance is already (1 - cosine_similarity), so similarity = 1 - distance
                    # For L2 distance: use 1 / (1 + distance)
                    # ChromaDB with cosine space returns cosine distance
                    try:
                        # If distance is between 0 and 2, it's likely cosine distance
                        if 0 <= distance <= 2:
                            similarity = 1 - (distance / 2)  # Normalize to 0-1
                        else:
                            # Fallback to L2 calculation
                            similarity = 1 / (1 + abs(distance))
                    except:
                        similarity = 1 / (1 + abs(distance))
                    
                    formatted_results.append({
                        "file_name": metadata.get("file_name"),
                        "bucket_name": metadata.get("bucket_name"),
                        "document_type": metadata.get("document_type"),
                        "upload_time": metadata.get("upload_time"),
                        "similarity_score": round(max(0, min(1, similarity)), 4),  # Clamp between 0-1
                        "preview": metadata.get("preview", "")  # Document preview
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def delete_document(self, bucket_name: str, file_name: str):
        """Delete document(s) from ChromaDB by bucket and file name"""
        try:
            # Get all documents
            all_docs = self.collection.get()
            
            # Find document IDs that match bucket_name and file_name
            ids_to_delete = []
            for i, metadata in enumerate(all_docs['metadatas']):
                if metadata.get('bucket_name') == bucket_name and metadata.get('file_name') == file_name:
                    ids_to_delete.append(all_docs['ids'][i])
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                print(f"Deleted {len(ids_to_delete)} document(s) for {file_name}")
                return True
            else:
                print(f"No documents found for {file_name} in {bucket_name}")
                return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def delete_documents(self, files: list[dict]):
        """Delete multiple documents from ChromaDB
        
        Args:
            files: List of dicts with 'bucket_name' and 'file_name' keys
        
        Returns:
            List of results with success status for each file
        """
        results = []
        for file_info in files:
            bucket_name = file_info.get('bucket_name')
            file_name = file_info.get('file_name')
            success = self.delete_document(bucket_name, file_name)
            results.append({
                'bucket_name': bucket_name,
                'file_name': file_name,
                'success': success
            })
        return results

# Singleton instance
search_service = SearchService()
