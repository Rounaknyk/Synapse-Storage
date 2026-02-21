from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
from config import settings
from datetime import datetime
import uuid

class QdrantSearchService:
    def __init__(self):
        try:
            # Use prefer_grpc=False for better cloud reliability
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=120,
                prefer_grpc=False  # Use HTTP API for more reliable cloud connections
            )
            self.collection_name = settings.QDRANT_COLLECTION_NAME
            self._initialized = False  # Track if collection was initialized
            print(f"✓ Qdrant connected to {settings.QDRANT_URL}")
        except Exception as e:
            print(f"❌ Error connecting to Qdrant: {e}")
            raise
    
    def initialize_collection(self):
        """Initialize or get existing Qdrant collection with retry logic"""
        if self._initialized:
            return  # Already initialized
            
        max_retries = 2  # Reduced retries for faster startup
        for attempt in range(max_retries):
            try:
                # Check if collection exists
                collections = self.client.get_collections().collections
                collection_names = [col.name for col in collections]
                
                if self.collection_name not in collection_names:
                    # Create collection with cosine distance
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=settings.EMBEDDING_DIMENSION,  # 384 for all-MiniLM-L6-v2
                            distance=Distance.COSINE
                        )
                    )
                    
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="user_id",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    print(f"✓ Created Qdrant collection '{self.collection_name}' with user_id index")
                else:
                    # Ensure index exists on older clusters
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="user_id",
                            field_schema=PayloadSchemaType.KEYWORD
                        )
                    except Exception:
                        pass
                    print(f"✓ Qdrant collection '{self.collection_name}' ready")
                
                self._initialized = True
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Qdrant connection attempt {attempt + 1} failed, retrying...")
                    import time
                    time.sleep(1)  # Reduced backoff
                else:
                    print(f"❌ Error initializing Qdrant collection after {max_retries} attempts: {e}")
                    raise
    
    def reset_collection(self):
        """Delete and recreate collection"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Deleted collection '{self.collection_name}'")
            self.initialize_collection()
            return True
        except Exception as e:
            print(f"❌ Error resetting collection: {e}")
            return False
    
    def add_document(self, doc_id: str, embedding: list, metadata: dict):
        """Add document embedding to Qdrant"""
        try:
            point = PointStruct(
                id=str(uuid.uuid4()),  # Qdrant needs unique ID
                vector=embedding,
                payload={
                    "doc_id": doc_id,
                    **metadata
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"❌ Error adding document to Qdrant: {e}")
            return False
    
    def search_similar(self, query_embedding: list, top_k: int = 3, user_id: str = None):
        """Perform similarity search"""
        try:
            # Lazy initialization if not done during startup
            if not self._initialized:
                self.initialize_collection()
                
            query_filter = None
            if user_id:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
                
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                query_filter=query_filter,
                limit=top_k
            ).points
            
            # Format results
            formatted_results = []
            for result in results:
                payload = result.payload
                # Qdrant score is already 0-1 for cosine similarity
                similarity = result.score
                
                formatted_results.append({
                    "id": payload.get("doc_id"), # Used to match Qdrant records with Firestore documents
                    "file_name": payload.get("file_name"),
                    "bucket_name": payload.get("bucket_name"),
                    "document_type": payload.get("document_type"),
                    "upload_time": payload.get("upload_time"),
                    "similarity_score": round(similarity, 4),
                    "preview": payload.get("preview", "")
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Error searching documents in Qdrant: {e}")
            return []
    
    def delete_document(self, bucket_name: str, file_name: str, user_id: str = None):
        """Delete document(s) from Qdrant by bucket and file name"""
        try:
            must_conditions = [
                FieldCondition(
                    key="bucket_name",
                    match=MatchValue(value=bucket_name)
                ),
                FieldCondition(
                    key="file_name",
                    match=MatchValue(value=file_name)
                )
            ]
            
            if user_id:
                must_conditions.append(
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                )
                
            # Search for documents matching the criteria
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=must_conditions),
                limit=100
            )
            
            points_to_delete = [point.id for point in scroll_result[0]]
            
            if points_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
                print(f"Deleted {len(points_to_delete)} point(s) for {file_name}")
                return True
            else:
                print(f"No documents found for {file_name} in {bucket_name}")
                return False
        except Exception as e:
            print(f"❌ Error deleting document from Qdrant: {e}")
            return False
    
    def delete_documents(self, files: list[dict], user_id: str = None):
        """Delete multiple documents from Qdrant"""
        results = []
        for file_info in files:
            bucket_name = file_info.get('bucket_name')
            file_name = file_info.get('file_name')
            success = self.delete_document(bucket_name, file_name, user_id)
            results.append({
                'bucket_name': bucket_name,
                'file_name': file_name,
                'success': success
            })
        return results
    
    def get_all_documents(self, user_id: str = None):
        """Get all documents metadata from Qdrant"""
        try:
            scroll_filter = None
            if user_id:
                scroll_filter = Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
                
            # Scroll through all points
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=scroll_filter,
                limit=10000,  # Adjust based on your needs
                with_payload=True,
                with_vectors=False
            )
            
            documents = []
            for point in scroll_result[0]:
                payload = point.payload
                documents.append({
                    "file_name": payload.get("file_name"),
                    "bucket_name": payload.get("bucket_name"),
                    "document_type": payload.get("document_type"),
                    "upload_time": payload.get("upload_time"),
                    "preview": payload.get("preview", "")
                })
            
            return documents
        except Exception as e:
            print(f"❌ Error getting documents from Qdrant: {e}")
            return []

# Singleton instance
qdrant_search_service = QdrantSearchService()
