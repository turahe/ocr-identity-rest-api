#!/bin/bash

# OCR Identity REST API Startup Script

echo "🚀 Starting OCR Identity REST API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp config.example.env .env
    echo "✅ .env file created. You can edit it later if needed."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p storage/images
mkdir -p init-scripts

# Make init script executable
if [ -f init-scripts/02-minio-setup.sh ]; then
    chmod +x init-scripts/02-minio-setup.sh
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 OCR Identity REST API is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • MinIO Console: http://localhost:9001 (admin/minioadmin)"
echo "   • Mailpit UI: http://localhost:8025"
echo ""
echo "🔧 Default Credentials:"
echo "   • Database: postgres/postgres"
echo "   • MinIO: minioadmin/minioadmin"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop services: docker-compose down"
echo ""
echo "✨ Setup complete! Your OCR Identity REST API is ready to use." 