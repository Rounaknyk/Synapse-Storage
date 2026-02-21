import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from config import settings
from datetime import timedelta
import io

class S3StorageService:
    def __init__(self):
        # Force boto3 to use regional endpoints for presigned URLs
        s3_config = Config(
            region_name=settings.AWS_REGION,
            s3={'addressing_style': 'virtual'},
            signature_version='s3v4'
        )
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=s3_config
        )
        print(f"✓ Connected to AWS S3 in region {settings.AWS_REGION}")
    
    def initialize_buckets(self):
        """Verify S3 buckets exist"""
        for category, bucket_name in settings.BUCKETS.items():
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                print(f"✓ Bucket verified: {bucket_name}")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    print(f"❌ Bucket not found: {bucket_name}")
                    print(f"   Please create it in AWS Console")
                else:
                    print(f"⚠️  Error checking bucket {bucket_name}: {e}")
    
    def upload_file(self, file_content: bytes, file_name: str, bucket_name: str, content_type: str = "application/octet-stream"):
        """Upload file to S3 bucket"""
        try:
            # Get actual bucket name from mapping
            actual_bucket = settings.BUCKETS.get(bucket_name, bucket_name)
            
            self.s3_client.put_object(
                Bucket=actual_bucket,
                Key=file_name,
                Body=file_content,
                ContentType=content_type
            )
            return True
        except ClientError as e:
            print(f"❌ Error uploading file to S3: {e}")
            return False
    
    def generate_presigned_url(self, bucket_name: str, file_name: str, expiry_hours: int = 1, inline: bool = False):
        """Generate presigned URL for file download or inline viewing"""
        try:
            import mimetypes
            
            # Get actual bucket name from mapping
            actual_bucket = settings.BUCKETS.get(bucket_name, bucket_name)
            
            # Debug logging
            print(f"🔍 Presigned URL Debug:")
            print(f"   Region: {settings.AWS_REGION}")
            print(f"   Bucket: {actual_bucket}")
            print(f"   Key: {file_name}")
            print(f"   Inline: {inline}")
            
            # Setup response overrides for inline viewing
            params = {
                'Bucket': actual_bucket,
                'Key': file_name
            }
            
            if inline:
                params['ResponseContentDisposition'] = f'inline; filename="{file_name}"'
                content_type, _ = mimetypes.guess_type(file_name)
                if content_type:
                    params['ResponseContentType'] = content_type
            
            # Generate presigned URL - will automatically use regional endpoint due to Config
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=int(timedelta(hours=expiry_hours).total_seconds())
            )
            
            print(f"   Generated URL: {url[:100]}...")
            return url
        except ClientError as e:
            print(f"❌ Error generating presigned URL: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error generating presigned URL: {e}")
            return None
    
    def delete_file(self, bucket_name: str, file_name: str):
        """Delete a file from S3 bucket"""
        try:
            actual_bucket = settings.BUCKETS.get(bucket_name, bucket_name)
            
            self.s3_client.delete_object(
                Bucket=actual_bucket,
                Key=file_name
            )
            return True
        except ClientError as e:
            print(f"❌ Error deleting file from S3: {e}")
            return False
    
    def delete_files(self, files: list[dict]):
        """Delete multiple files from S3 buckets"""
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
        """Download raw file bytes from S3 — used for full-text RAG context"""
        try:
            actual_bucket = settings.BUCKETS.get(bucket_name, bucket_name)
            
            response = self.s3_client.get_object(
                Bucket=actual_bucket,
                Key=file_name
            )
            data = response['Body'].read()
            return data
        except ClientError as e:
            print(f"❌ Error downloading file {file_name}: {e}")
            return None

# Singleton instance
s3_storage_service = S3StorageService()
