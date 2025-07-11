#!/bin/bash

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
until curl -f http://localhost:9000/minio/health/live; do
    echo "MinIO is not ready yet, waiting..."
    sleep 5
done

echo "MinIO is ready!"

# Install MinIO client (mc)
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configure MinIO client
./mc alias set myminio http://localhost:9000 ${MINIO_ROOT_USER:-minioadmin} ${MINIO_ROOT_PASSWORD:-minioadmin}

# Create default bucket
echo "Creating default bucket: ${S3_BUCKET_NAME:-ocr-identity-bucket}"
./mc mb myminio/${S3_BUCKET_NAME:-ocr-identity-bucket}

# Set bucket policy for public read (optional, adjust as needed)
# ./mc policy set download myminio/${S3_BUCKET_NAME:-ocr-identity-bucket}

echo "MinIO setup completed!"
echo "Bucket created: ${S3_BUCKET_NAME:-ocr-identity-bucket}"
echo "Access MinIO Console at: http://localhost:9001"
echo "Username: ${MINIO_ROOT_USER:-minioadmin}"
echo "Password: ${MINIO_ROOT_PASSWORD:-minioadmin}" 