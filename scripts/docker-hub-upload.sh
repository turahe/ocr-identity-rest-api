#!/bin/bash

# Docker Hub Upload Script for OCR Identity REST API
# Usage: ./scripts/docker-hub-upload.sh [version] [username]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_VERSION="latest"
DEFAULT_USERNAME="your-dockerhub-username"
DEFAULT_IMAGE_NAME="ocr-identity-api"

# Configuration
VERSION=${1:-$DEFAULT_VERSION}
DOCKER_USERNAME=${2:-$DEFAULT_USERNAME}
IMAGE_NAME=${DEFAULT_IMAGE_NAME}
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    log_info "Checking Docker installation..."
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running or not installed"
        exit 1
    fi
    log_success "Docker is running"
}

# Check if Dockerfile exists
check_dockerfile() {
    log_info "Checking Dockerfile..."
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile not found in current directory"
        exit 1
    fi
    log_success "Dockerfile found"
}

# Login to Docker Hub
docker_login() {
    log_info "Logging in to Docker Hub..."
    
    if [ -z "$DOCKER_USERNAME" ] || [ "$DOCKER_USERNAME" = "$DEFAULT_USERNAME" ]; then
        log_warning "Please set your Docker Hub username"
        read -p "Enter your Docker Hub username: " DOCKER_USERNAME
        FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"
    fi
    
    if [ -z "$DOCKER_PASSWORD" ]; then
        log_warning "DOCKER_PASSWORD environment variable not set"
        read -s -p "Enter your Docker Hub password: " DOCKER_PASSWORD
        echo
    fi
    
    if echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin; then
        log_success "Successfully logged in to Docker Hub"
    else
        log_error "Failed to login to Docker Hub"
        exit 1
    fi
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    log_info "Image: ${FULL_IMAGE_NAME}:${VERSION}"
    
    # Build with different targets
    log_info "Building production image..."
    if docker build --target production -t "${FULL_IMAGE_NAME}:${VERSION}" .; then
        log_success "Production image built successfully"
    else
        log_error "Failed to build production image"
        exit 1
    fi
    
    # Also build development image
    log_info "Building development image..."
    if docker build --target development -t "${FULL_IMAGE_NAME}:${VERSION}-dev" .; then
        log_success "Development image built successfully"
    else
        log_error "Failed to build development image"
        exit 1
    fi
}

# Tag images
tag_images() {
    log_info "Tagging images..."
    
    # Tag production image
    docker tag "${FULL_IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}:latest"
    log_success "Tagged production image as latest"
    
    # Tag development image
    docker tag "${FULL_IMAGE_NAME}:${VERSION}-dev" "${FULL_IMAGE_NAME}:latest-dev"
    log_success "Tagged development image as latest-dev"
    
    # If version is not latest, also tag with version
    if [ "$VERSION" != "latest" ]; then
        docker tag "${FULL_IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_NAME}:v${VERSION}"
        docker tag "${FULL_IMAGE_NAME}:${VERSION}-dev" "${FULL_IMAGE_NAME}:v${VERSION}-dev"
        log_success "Tagged images with version v${VERSION}"
    fi
}

# Push images to Docker Hub
push_images() {
    log_info "Pushing images to Docker Hub..."
    
    # Push production images
    log_info "Pushing production image..."
    if docker push "${FULL_IMAGE_NAME}:${VERSION}"; then
        log_success "Production image pushed successfully"
    else
        log_error "Failed to push production image"
        exit 1
    fi
    
    if docker push "${FULL_IMAGE_NAME}:latest"; then
        log_success "Latest production image pushed successfully"
    else
        log_error "Failed to push latest production image"
        exit 1
    fi
    
    # Push development images
    log_info "Pushing development image..."
    if docker push "${FULL_IMAGE_NAME}:${VERSION}-dev"; then
        log_success "Development image pushed successfully"
    else
        log_error "Failed to push development image"
        exit 1
    fi
    
    if docker push "${FULL_IMAGE_NAME}:latest-dev"; then
        log_success "Latest development image pushed successfully"
    else
        log_error "Failed to push latest development image"
        exit 1
    fi
    
    # Push versioned images if not latest
    if [ "$VERSION" != "latest" ]; then
        log_info "Pushing versioned images..."
        docker push "${FULL_IMAGE_NAME}:v${VERSION}"
        docker push "${FULL_IMAGE_NAME}:v${VERSION}-dev"
        log_success "Versioned images pushed successfully"
    fi
}

# Show image information
show_image_info() {
    log_info "Image information:"
    echo "  Repository: ${FULL_IMAGE_NAME}"
    echo "  Version: ${VERSION}"
    echo "  Tags:"
    echo "    - ${FULL_IMAGE_NAME}:${VERSION}"
    echo "    - ${FULL_IMAGE_NAME}:latest"
    echo "    - ${FULL_IMAGE_NAME}:${VERSION}-dev"
    echo "    - ${FULL_IMAGE_NAME}:latest-dev"
    if [ "$VERSION" != "latest" ]; then
        echo "    - ${FULL_IMAGE_NAME}:v${VERSION}"
        echo "    - ${FULL_IMAGE_NAME}:v${VERSION}-dev"
    fi
}

# Clean up local images (optional)
cleanup_images() {
    read -p "Do you want to remove local images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Removing local images..."
        docker rmi "${FULL_IMAGE_NAME}:${VERSION}" 2>/dev/null || true
        docker rmi "${FULL_IMAGE_NAME}:latest" 2>/dev/null || true
        docker rmi "${FULL_IMAGE_NAME}:${VERSION}-dev" 2>/dev/null || true
        docker rmi "${FULL_IMAGE_NAME}:latest-dev" 2>/dev/null || true
        if [ "$VERSION" != "latest" ]; then
            docker rmi "${FULL_IMAGE_NAME}:v${VERSION}" 2>/dev/null || true
            docker rmi "${FULL_IMAGE_NAME}:v${VERSION}-dev" 2>/dev/null || true
        fi
        log_success "Local images removed"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [version] [username]"
    echo ""
    echo "Arguments:"
    echo "  version   - Version tag for the image (default: latest)"
    echo "  username  - Docker Hub username (default: your-dockerhub-username)"
    echo ""
    echo "Environment variables:"
    echo "  DOCKER_PASSWORD - Docker Hub password (optional, will prompt if not set)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build and push latest version"
    echo "  $0 2.0.0             # Build and push version 2.0.0"
    echo "  $0 2.0.0 myusername  # Build and push version 2.0.0 for myusername"
    echo ""
    echo "The script will create the following tags:"
    echo "  - username/ocr-identity-api:version"
    echo "  - username/ocr-identity-api:latest"
    echo "  - username/ocr-identity-api:version-dev"
    echo "  - username/ocr-identity-api:latest-dev"
    echo "  - username/ocr-identity-api:vversion (if version != latest)"
    echo "  - username/ocr-identity-api:vversion-dev (if version != latest)"
}

# Main function
main() {
    echo "🐳 Docker Hub Upload Script for OCR Identity REST API"
    echo "=================================================="
    echo ""
    
    # Show usage if help is requested
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    # Show configuration
    log_info "Configuration:"
    echo "  Version: ${VERSION}"
    echo "  Username: ${DOCKER_USERNAME}"
    echo "  Image: ${FULL_IMAGE_NAME}"
    echo ""
    
    # Check prerequisites
    check_docker
    check_dockerfile
    
    # Login to Docker Hub
    docker_login
    
    # Build images
    build_image
    
    # Tag images
    tag_images
    
    # Push images
    push_images
    
    # Show results
    echo ""
    log_success "🎉 All images uploaded successfully!"
    show_image_info
    
    # Cleanup option
    echo ""
    cleanup_images
    
    echo ""
    log_success "Upload completed! You can now pull the images with:"
    echo "  docker pull ${FULL_IMAGE_NAME}:${VERSION}"
    echo "  docker pull ${FULL_IMAGE_NAME}:latest"
}

# Run main function
main "$@" 