#!/bin/bash

# OCR Identity REST API - Development Startup Script
# Optimized Docker Compose setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! docker-compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create environment file if it doesn't exist
create_env_file() {
    print_status "Setting up environment file..."
    
    if [ ! -f "../.env" ]; then
        if [ -f "../config.example.env" ]; then
            cp ../config.example.env ../.env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your configuration"
        else
            print_warning "No config.example.env found. Please create .env file manually"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Build images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    print_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "PostgreSQL failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Redis failed to start within 30 seconds"
        exit 1
    fi
    
    # Wait for MinIO
    print_status "Waiting for MinIO..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
            print_success "MinIO is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "MinIO failed to start within 30 seconds"
        exit 1
    fi
    
    # Wait for application
    print_status "Waiting for application..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Application is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Application failed to start within 60 seconds"
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if docker-compose exec -T app poetry run alembic upgrade head; then
        print_success "Database migrations completed"
    else
        print_error "Database migrations failed"
        exit 1
    fi
}

# Setup MinIO bucket
setup_minio() {
    print_status "Setting up MinIO bucket..."
    
    if docker-compose exec -T app poetry run python scripts/setup_minio.py; then
        print_success "MinIO bucket setup completed"
    else
        print_warning "MinIO bucket setup failed (this might be normal if already configured)"
    fi
}

# Show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  MinIO Console: http://localhost:9001"
    echo "  Mailpit: http://localhost:8025"
    echo ""
    print_status "Useful commands:"
    echo "  docker-compose logs -f    # View logs"
    echo "  docker-compose down       # Stop services"
    echo "  docker-compose restart    # Restart services"
    echo "  docker-compose ps         # Show status"
}

# Main function
main() {
    echo "🚀 OCR Identity REST API - Development Startup"
    echo "=============================================="
    echo ""
    
    # Change to docker directory
    cd "$(dirname "$0")"
    
    check_docker
    check_docker_compose
    create_env_file
    start_services
    wait_for_services
    run_migrations
    setup_minio
    show_status
    
    echo ""
    print_success "Development environment is ready!"
    echo ""
}

# Run main function
main "$@" 