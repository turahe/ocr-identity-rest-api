#!/bin/bash

# Staging Environment Startup Script

echo "🚀 Starting OCR Identity REST API in Staging Mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists, create from staging config if not
if [ ! -f .env ]; then
    echo "📝 Creating .env file from staging configuration..."
    cp config.staging.env .env
    echo "✅ .env file created from staging configuration."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p storage/images
mkdir -p init-scripts
mkdir -p logs

# Make init script executable
if [ -f init-scripts/02-minio-setup.sh ]; then
    chmod +x init-scripts/02-minio-setup.sh
fi

# Start staging services
echo "🐳 Starting staging services..."
docker-compose -f docker-compose.staging.yml --profile staging up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.staging.yml exec -T app alembic upgrade head

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.staging.yml ps

echo ""
echo "🎉 OCR Identity REST API (Staging) is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   • API Documentation: http://localhost:8001/docs"
echo "   • MinIO Console: http://localhost:9003 (minioadmin/minioadmin)"
echo "   • Mailpit UI: http://localhost:8026"
echo ""
echo "🔧 Default Credentials:"
echo "   • Database: postgres/postgres"
echo "   • MinIO: minioadmin/minioadmin"
echo ""
echo "🔍 Staging Features:"
echo "   • Optimized for testing"
echo "   • Separate database and storage"
echo "   • Different ports to avoid conflicts"
echo ""
echo "📝 Commands:"
echo "   • View logs: docker-compose -f docker-compose.staging.yml logs -f"
echo "   • Stop services: docker-compose -f docker-compose.staging.yml down"
echo "   • Restart app: docker-compose -f docker-compose.staging.yml restart app"
echo ""
echo "✨ Staging environment is ready!" 