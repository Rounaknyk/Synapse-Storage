import firebase_admin
from firebase_admin import firestore
from datetime import datetime

class FirestoreService:
    def __init__(self):
        # We explicitly grab the app to ensure credentials flow through correctly to gRPC
        try:
            app = firebase_admin.get_app()
            self.db = firestore.client(app=app)
            print("✓ Firestore connected")
        except Exception as e:
            print(f"⚠️  Firestore connection issue: {e}")
            self.db = None
            
    def add_document_metadata(self, doc_id: str, user_id: str, file_name: str, bucket_name: str, document_type: str, preview: str):
        """Save document metadata to Firestore"""
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection('documents').document(doc_id)
            doc_ref.set({
                "user_id": user_id,
                "file_name": file_name,
                "bucket_name": bucket_name,
                "document_type": document_type,
                "preview": preview,
                "upload_time": datetime.now().isoformat(),
                "qdrant_id": doc_id # Store the reference ID to the vector DB
            })
            return True
        except Exception as e:
            print(f"❌ Error adding document to Firestore: {e}")
            return False

    def get_user_documents(self, user_id: str):
        """Retrieve all documents uploaded by a specific user"""
        if not self.db:
            return []
            
        try:
            docs = self.db.collection('documents').where('user_id', '==', user_id).order_by('upload_time', direction=firestore.Query.DESCENDING).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
                
            return results
        except Exception as e:
            print(f"❌ Error retrieving documents from Firestore: {e}")
            # If the index is missing, firestore will throw an error with a URL to create it
            return []
            
    def get_documents_by_ids(self, doc_ids: list[str]):
        """Retrieve full metadata for specific document IDs (used after Qdrant search)"""
        if not self.db or not doc_ids:
            return []
            
        try:
            results = []
            # Since top_k is small (usually 3-5), fetching them individually is extremely fast
            # and avoids the python FieldPath.document_id() complexities.
            for doc_id in doc_ids:
                doc = self.db.collection('documents').document(doc_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    results.append(data)
                        
            return results
        except Exception as e:
            print(f"❌ Error retrieving specific documents from Firestore: {e}")
            return []

    def delete_document(self, user_id: str, bucket_name: str, file_name: str):
        """Delete a document record from Firestore"""
        if not self.db:
            return False
            
        try:
            # Find the document ID first
            docs = self.db.collection('documents')\
                .where('user_id', '==', user_id)\
                .where('bucket_name', '==', bucket_name)\
                .where('file_name', '==', file_name)\
                .stream()
                
            deleted = False
            for doc in docs:
                doc.reference.delete()
                deleted = True
                
            return deleted
        except Exception as e:
            print(f"❌ Error deleting document from Firestore: {e}")
            return False
            
    def delete_documents(self, files: list[dict], user_id: str):
        """Delete multiple document records from Firestore"""
        results = []
        for file_info in files:
            bucket_name = file_info.get('bucket_name')
            file_name = file_info.get('file_name')
            success = self.delete_document(user_id, bucket_name, file_name)
            results.append({
                'bucket_name': bucket_name,
                'file_name': file_name,
                'success': success
            })
        return results

# Singleton instance
firestore_service = FirestoreService()
