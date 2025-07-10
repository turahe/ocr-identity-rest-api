#!/usr/bin/env python3
"""
MinIO setup script for bucket creation and configuration
"""
import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import get_s3_config


def setup_minio_bucket():
    """Setup MinIO bucket and configuration"""
    try:
        config = get_s3_config()
        
        # Create S3 client
        session = boto3.Session(
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region_name
        )
        
        s3_client = session.client(
            's3',
            endpoint_url=config.endpoint_url,
            use_ssl=config.use_ssl,
            verify=config.verify_ssl
        )
        
        bucket_name = config.bucket_name
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                print(f"📦 Creating bucket '{bucket_name}'...")
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' created successfully")
            else:
                raise e
        
        # Set bucket policy for public read access (optional)
        try:
            bucket_policy = {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Sid': 'PublicReadGetObject',
                        'Effect': 'Allow',
                        'Principal': '*',
                        'Action': 's3:GetObject',
                        'Resource': f'arn:aws:s3:::{bucket_name}/*'
                    }
                ]
            }
            
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print(f"✅ Bucket policy set for '{bucket_name}'")
        except Exception as e:
            print(f"⚠️  Could not set bucket policy: {e}")
        
        # Create folder structure
        folders = [
            'uploads/',
            'thumbnails/',
            'documents/',
            'temp/'
        ]
        
        for folder in folders:
            try:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=folder,
                    Body=''
                )
                print(f"✅ Created folder '{folder}'")
            except Exception as e:
                print(f"⚠️  Could not create folder '{folder}': {e}")
        
        print(f"\n🎉 MinIO setup completed successfully!")
        print(f"📁 Bucket: {bucket_name}")
        print(f"🌐 Endpoint: {config.endpoint_url}")
        print(f"🔑 Access Key: {config.aws_access_key_id}")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please check your configuration.")
        return False
    except Exception as e:
        print(f"❌ MinIO setup failed: {e}")
        return False


def test_s3_connection():
    """Test S3 connection and permissions"""
    try:
        config = get_s3_config()
        
        session = boto3.Session(
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region_name
        )
        
        s3_client = session.client(
            's3',
            endpoint_url=config.endpoint_url,
            use_ssl=config.use_ssl,
            verify=config.verify_ssl
        )
        
        # Test upload
        test_content = b"test file content"
        test_key = "test/connection-test.txt"
        
        s3_client.put_object(
            Bucket=config.bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType="text/plain"
        )
        
        # Test download
        response = s3_client.get_object(
            Bucket=config.bucket_name,
            Key=test_key
        )
        
        downloaded_content = response['Body'].read()
        if downloaded_content == test_content:
            print("✅ S3 connection test successful")
            
            # Clean up test file
            s3_client.delete_object(
                Bucket=config.bucket_name,
                Key=test_key
            )
            print("✅ Test file cleaned up")
            return True
        else:
            print("❌ S3 connection test failed - content mismatch")
            return False
            
    except Exception as e:
        print(f"❌ S3 connection test failed: {e}")
        return False


def main():
    """Main setup function"""
    import json
    
    print("🚀 Setting up MinIO configuration...")
    
    # Setup bucket
    if setup_minio_bucket():
        print("\n🧪 Testing S3 connection...")
        if test_s3_connection():
            print("\n🎉 MinIO setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start your application")
            print("2. Upload files via API")
            print("3. Check MinIO console at http://localhost:9001")
        else:
            print("\n❌ S3 connection test failed")
            sys.exit(1)
    else:
        print("\n❌ MinIO setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 