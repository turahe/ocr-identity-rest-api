#!/bin/bash

# Development Environment Startup Script

echo "🚀 Starting OCR Identity REST API in Development Mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists, create from dev config if not
if [ ! -f .env ]; then
    echo "📝 Creating .env file from development configuration..."
    cp config.dev.env .env
    echo "✅ .env file created from development configuration."
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

# Start development services
echo "🐳 Starting development services..."
docker-compose -f docker-compose.dev.yml --profile dev up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.dev.yml exec -T app alembic upgrade head

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 OCR Identity REST API (Development) is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "   • Mailpit UI: http://localhost:8025"
echo ""
echo "🔧 Default Credentials:"
echo "   • Database: postgres/postgres"
echo "   • MinIO: minioadmin/minioadmin"
echo ""
echo "🐛 Debug Features:"
echo "   • Hot reload enabled"
echo "   • Debug port: 5678"
echo "   • Debug mode: enabled"
echo ""
echo "📝 Commands:"
echo "   • View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "   • Stop services: docker-compose -f docker-compose.dev.yml down"
echo "   • Restart app: docker-compose -f docker-compose.dev.yml restart app"
echo ""
echo "✨ Development environment is ready!" 