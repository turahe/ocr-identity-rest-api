"""
S3 service for file uploads and management
"""
import boto3
import hashlib
import os
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import get_s3_config


class S3Service:
    """Service for S3 operations"""
    
    def __init__(self):
        self.config = get_s3_config()
        self.client = self._create_client()
        self.bucket_name = self.config.bucket_name
    
    def _create_client(self):
        """Create S3 client with configuration"""
        session = boto3.Session(
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            region_name=self.config.region_name
        )
        
        return session.client(
            's3',
            endpoint_url=self.config.endpoint_url,
            use_ssl=self.config.use_ssl,
            verify=self.config.verify_ssl
        )
    
    def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> Dict[str, Any]:
        """
        Upload file to S3
        
        Args:
            file_content: File content as bytes
            file_name: Name of the file
            content_type: MIME type of the file
            
        Returns:
            Dict containing upload result with key, url, and metadata
        """
        try:
            # Generate file hash for unique naming
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Create S3 key with hash-based naming
            file_extension = os.path.splitext(file_name)[1]
            s3_key = f"uploads/{file_hash}{file_extension}"
            
            # Upload to S3
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'original_filename': file_name,
                    'file_hash': file_hash,
                    'content_type': content_type,
                    'file_size': str(len(file_content))
                }
            )
            
            # Generate URL
            if self.config.endpoint_url:
                # For MinIO or other S3-compatible services
                url = f"{self.config.endpoint_url}/{self.bucket_name}/{s3_key}"
            else:
                # For AWS S3
                url = f"https://{self.bucket_name}.s3.{self.config.region_name}.amazonaws.com/{s3_key}"
            
            return {
                'key': s3_key,
                'url': url,
                'hash': file_hash,
                'size': len(file_content),
                'original_filename': file_name,
                'content_type': content_type
            }
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def download_file(self, s3_key: str) -> bytes:
        """
        Download file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"S3 download failed: {str(e)}")
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            raise Exception(f"S3 delete failed: {str(e)}")
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
    
    def get_file_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            File metadata or None if not found
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }
        except ClientError:
            return None
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for file access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError:
            return None


# Create global S3 service instance
s3_service = S3Service() 