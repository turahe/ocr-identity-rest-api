#!/bin/bash

# Production Environment Startup Script

echo "🚀 Starting OCR Identity REST API in Production Mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create .env file from production configuration:"
    echo "   cp config.prod.env .env"
    echo "   # Then edit .env with your production settings"
    exit 1
fi

# Check for required production environment variables
if grep -q "your-secure" .env || grep -q "your-super-secure" .env; then
    echo "⚠️  WARNING: Default passwords detected in .env file!"
    echo "   Please update the following in your .env file:"
    echo "   - SECRET_KEY"
    echo "   - DB_PASSWORD"
    echo "   - REDIS_PASSWORD"
    echo "   - MINIO_ROOT_PASSWORD"
    echo "   - EMAIL_PASSWORD"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p storage/images
mkdir -p init-scripts
mkdir -p logs
mkdir -p nginx/ssl

# Make init script executable
if [ -f init-scripts/02-minio-setup.sh ]; then
    chmod +x init-scripts/02-minio-setup.sh
fi

# Start production services
echo "🐳 Starting production services..."
docker-compose -f docker-compose.prod.yml --profile prod up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 20

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T app alembic upgrade head

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🎉 OCR Identity REST API (Production) is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   • API Documentation: http://localhost:8002/docs"
echo "   • MinIO Console: http://localhost:9005"
echo ""
echo "🔧 Production Features:"
echo "   • Multiple app replicas for high availability"
echo "   • Resource limits configured"
echo "   • Health checks enabled"
echo "   • Production-optimized settings"
echo ""
echo "📝 Commands:"
echo "   • View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   • Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   • Scale app: docker-compose -f docker-compose.prod.yml up --scale app=3"
echo ""
echo "🔒 Security Reminders:"
echo "   • Change all default passwords"
echo "   • Use strong SECRET_KEY"
echo "   • Configure SSL/TLS"
echo "   • Set up proper firewall rules"
echo ""
echo "✨ Production environment is ready!" 