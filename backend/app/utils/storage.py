import os
import uuid
from datetime import datetime
from typing import Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class StorageManager:
    def __init__(self):
        self.backend = settings.storage_backend.lower()
        if self.backend == "local":
            self._ensure_local_dirs()
    
    def _ensure_local_dirs(self):
        """Create necessary local storage directories"""
        base_dir = settings.storage_local_dir
        subdirs = ['photos', 'reports', 'temp']
        
        for subdir in subdirs:
            path = os.path.join(base_dir, subdir)
            os.makedirs(path, exist_ok=True)
    
    def save_photo(self, image_bytes: bytes, bin_id: Optional[str] = None) -> str:
        """Save photo and return storage reference"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            
            if bin_id:
                filename = f"{bin_id}_{timestamp}_{unique_id}.jpg"
            else:
                filename = f"snapshot_{timestamp}_{unique_id}.jpg"
            
            if self.backend == "local":
                return self._save_local_photo(image_bytes, filename)
            elif self.backend == "s3":
                return self._save_s3_photo(image_bytes, filename)
            else:
                raise ValueError(f"Unsupported storage backend: {self.backend}")
        
        except Exception as e:
            logger.error(f"Error saving photo: {e}")
            raise
    
    def _save_local_photo(self, image_bytes: bytes, filename: str) -> str:
        """Save photo to local storage"""
        today = datetime.now().strftime("%Y-%m-%d")
        photo_dir = os.path.join(settings.storage_local_dir, "photos", today)
        os.makedirs(photo_dir, exist_ok=True)
        
        file_path = os.path.join(photo_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        # Return relative path for storage reference
        return f"local://photos/{today}/{filename}"
    
    def _save_s3_photo(self, image_bytes: bytes, filename: str) -> str:
        """Save photo to S3 storage"""
        try:
            import boto3
            from botocore.config import Config
            
            # Configure S3 client
            config = Config(
                region_name='auto',
                retries={'max_attempts': 3}
            )
            
            s3_client = boto3.client(
                's3',
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                config=config
            )
            
            # Upload to S3
            today = datetime.now().strftime("%Y-%m-%d")
            key = f"photos/{today}/{filename}"
            
            s3_client.put_object(
                Bucket=settings.s3_bucket,
                Key=key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            
            return f"s3://{settings.s3_bucket}/{key}"
        
        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            # Fallback to local storage
            return self._save_local_photo(image_bytes, filename)
    
    def save_report(self, content: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        """Save report file and return storage reference"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            if self.backend == "local":
                report_dir = os.path.join(settings.storage_local_dir, "reports", today)
                os.makedirs(report_dir, exist_ok=True)
                
                file_path = os.path.join(report_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(content)
                
                return f"local://reports/{today}/{filename}"
            
            elif self.backend == "s3":
                import boto3
                from botocore.config import Config
                
                config = Config(region_name='auto', retries={'max_attempts': 3})
                s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.s3_endpoint,
                    aws_access_key_id=settings.s3_access_key,
                    aws_secret_access_key=settings.s3_secret_key,
                    config=config
                )
                
                key = f"reports/{today}/{filename}"
                s3_client.put_object(
                    Bucket=settings.s3_bucket,
                    Key=key,
                    Body=content,
                    ContentType=content_type
                )
                
                return f"s3://{settings.s3_bucket}/{key}"
        
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise
    
    def get_file_url(self, storage_ref: str) -> str:
        """Get accessible URL for storage reference"""
        try:
            if storage_ref.startswith("local://"):
                # For local files, return relative path for serving
                path = storage_ref.replace("local://", "")
                return f"/storage/{path}"
            
            elif storage_ref.startswith("s3://"):
                # For S3, generate presigned URL
                import boto3
                from botocore.config import Config
                
                bucket_and_key = storage_ref.replace("s3://", "")
                bucket, key = bucket_and_key.split("/", 1)
                
                config = Config(region_name='auto')
                s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.s3_endpoint,
                    aws_access_key_id=settings.s3_access_key,
                    aws_secret_access_key=settings.s3_secret_key,
                    config=config
                )
                
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': key},
                    ExpiresIn=3600  # 1 hour
                )
                
                return url
            
            else:
                return storage_ref
        
        except Exception as e:
            logger.error(f"Error generating file URL: {e}")
            return storage_ref
    
    def get_file_path(self, storage_ref: str) -> Optional[str]:
        """Get local file path for storage reference (local backend only)"""
        if not storage_ref.startswith("local://"):
            return None
        
        relative_path = storage_ref.replace("local://", "")
        return os.path.join(settings.storage_local_dir, relative_path)


# Global storage manager instance
storage_manager = StorageManager()