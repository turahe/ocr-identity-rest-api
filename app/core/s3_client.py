import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, BinaryIO, Dict, Any
import io
from .config import get_s3_config


class S3Manager:
    """AWS S3 connection manager"""
    
    def __init__(self):
        self.config = get_s3_config()
        self.client: Optional[boto3.client] = None
        self.resource: Optional[boto3.resource] = None
    
    def create_client(self) -> boto3.client:
        """Create and return an S3 client"""
        if self.client is None:
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.region_name,
                endpoint_url=self.config.endpoint_url,
                use_ssl=self.config.use_ssl,
                verify=self.config.verify_ssl
            )
        return self.client
    
    def create_resource(self) -> boto3.resource:
        """Create and return an S3 resource"""
        if self.resource is None:
            self.resource = boto3.resource(
                's3',
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.region_name,
                endpoint_url=self.config.endpoint_url,
                use_ssl=self.config.use_ssl,
                verify=self.config.verify_ssl
            )
        return self.resource
    
    def get_client(self) -> boto3.client:
        """Get the S3 client"""
        if self.client is None:
            self.create_client()
        return self.client
    
    def get_resource(self) -> boto3.resource:
        """Get the S3 resource"""
        if self.resource is None:
            self.create_resource()
        return self.resource
    
    def upload_file(self, file_path: str, s3_key: str, content_type: Optional[str] = None) -> bool:
        """Upload a file to S3"""
        try:
            client = self.get_client()
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            client.upload_file(
                file_path,
                self.config.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            print(f"Error uploading file to S3: {e}")
            return False
    
    def upload_fileobj(self, file_obj: BinaryIO, s3_key: str, content_type: Optional[str] = None) -> bool:
        """Upload a file object to S3"""
        try:
            client = self.get_client()
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            client.upload_fileobj(
                file_obj,
                self.config.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            print(f"Error uploading file object to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """Download a file from S3"""
        try:
            client = self.get_client()
            client.download_file(
                self.config.bucket_name,
                s3_key,
                local_path
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            print(f"Error downloading file from S3: {e}")
            return False
    
    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for file access"""
        try:
            client = self.get_client()
            url = client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.config.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return url
        except (ClientError, NoCredentialsError) as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        try:
            client = self.get_client()
            client.delete_object(
                Bucket=self.config.bucket_name,
                Key=s3_key
            )
            return True
        except (ClientError, NoCredentialsError) as e:
            print(f"Error deleting file from S3: {e}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3"""
        try:
            client = self.get_client()
            client.head_object(
                Bucket=self.config.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> list:
        """List files in S3 bucket with optional prefix"""
        try:
            client = self.get_client()
            response = client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except (ClientError, NoCredentialsError) as e:
            print(f"Error listing files from S3: {e}")
            return []


# Global S3 manager instance
s3_manager = S3Manager()


def get_s3() -> S3Manager:
    """Get the S3 manager instance"""
    return s3_manager 