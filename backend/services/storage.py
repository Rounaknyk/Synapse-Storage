from minio import Minio
from minio.error import S3Error
from config import settings
from datetime import timedelta
import io

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        print(f"Connected to MinIO at {settings.MINIO_ENDPOINT}")
    
    def initialize_buckets(self):
        """Create buckets if they don't exist"""
        for bucket_name in settings.BUCKETS:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    print(f"✓ Created bucket: {bucket_name}")
                else:
                    print(f"✓ Bucket already exists: {bucket_name}")
            except S3Error as e:
                print(f"Error creating bucket {bucket_name}: {e}")
    
    def upload_file(self, file_content: bytes, file_name: str, bucket_name: str, content_type: str = "application/octet-stream"):
        """Upload file to MinIO bucket"""
        try:
            file_stream = io.BytesIO(file_content)
            self.client.put_object(
                bucket_name,
                file_name,
                file_stream,
                length=len(file_content),
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return False
    
    def generate_presigned_url(self, bucket_name: str, file_name: str, expiry_hours: int = 1):
        """Generate presigned URL for file download"""
        try:
            url = self.client.presigned_get_object(
                bucket_name,
                file_name,
                expires=timedelta(hours=expiry_hours)
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, bucket_name: str, file_name: str):
        """Delete a file from MinIO bucket"""
        try:
            self.client.remove_object(bucket_name, file_name)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False
    
    def delete_files(self, files: list[dict]):
        """Delete multiple files from MinIO buckets
        
        Args:
            files: List of dicts with 'bucket_name' and 'file_name' keys
        
        Returns:
            List of results with success status for each file
        """
        results = []
        for file_info in files:
            bucket_name = file_info.get('bucket_name')
            file_name = file_info.get('file_name')
            success = self.delete_file(bucket_name, file_name)
            results.append({
                'bucket_name': bucket_name,
                'file_name': file_name,
                'success': success
            })
        return results

    def download_file(self, bucket_name: str, file_name: str) -> bytes | None:
        """Download raw file bytes from MinIO — used for full-text RAG context"""
        try:
            response = self.client.get_object(bucket_name, file_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error downloading file {file_name}: {e}")
            return None

# Singleton instance
storage_service = StorageService()
