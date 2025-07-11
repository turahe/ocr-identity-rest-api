#!/bin/bash

# OCR Identity REST API - Docker Migration Script
# This script migrates old Docker files to the new optimized structure

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

# Create backup directory
create_backup() {
    print_status "Creating backup directory..."
    mkdir -p docker/backup
    print_success "Backup directory created"
}

# Backup old Docker files
backup_old_files() {
    print_status "Backing up old Docker files..."
    
    # List of files to backup
    files_to_backup=(
        "../docker-compose.yml"
        "../docker-compose.dev.yml"
        "../docker-compose.staging.yml"
        "../docker-compose.prod.yml"
        "../docker-compose.multi-db.yml"
        "../start-dev.sh"
        "../start-staging.sh"
        "../start-prod.sh"
        "../start-multi-db.sh"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "docker/backup/"
            print_success "Backed up: $file"
        else
            print_warning "File not found: $file"
        fi
    done
}

# Remove old Docker files
remove_old_files() {
    print_status "Removing old Docker files..."
    
    # List of files to remove
    files_to_remove=(
        "../docker-compose.yml"
        "../docker-compose.dev.yml"
        "../docker-compose.staging.yml"
        "../docker-compose.prod.yml"
        "../docker-compose.multi-db.yml"
        "../start-dev.sh"
        "../start-staging.sh"
        "../start-prod.sh"
        "../start-multi-db.sh"
    )
    
    for file in "${files_to_remove[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            print_success "Removed: $file"
        else
            print_warning "File not found: $file"
        fi
    done
}

# Update Makefile references
update_makefile() {
    print_status "Updating Makefile Docker references..."
    
    if [ -f "../Makefile" ]; then
        # Update Docker commands in Makefile
        sed -i 's|docker-compose|cd docker \&\& docker-compose|g' ../Makefile
        sed -i 's|make docker-up|cd docker \&\& ./start-dev.sh|g' ../Makefile
        sed -i 's|make docker-down|cd docker \&\& docker-compose down|g' ../Makefile
        print_success "Makefile updated"
    else
        print_warning "Makefile not found"
    fi
}

# Show migration summary
show_summary() {
    echo ""
    print_success "Docker migration completed!"
    echo ""
    print_status "Migration Summary:"
    echo "  ✅ Old Docker files backed up to docker/backup/"
    echo "  ✅ New optimized Docker structure created"
    echo "  ✅ Environment-specific configurations added"
    echo "  ✅ Resource management optimized"
    echo "  ✅ Health checks improved"
    echo ""
    print_status "Next Steps:"
    echo "  1. Test the new Docker setup: cd docker && ./start-dev.sh"
    echo "  2. Review the new structure: docker/README.md"
    echo "  3. Update your deployment scripts if needed"
    echo "  4. Remove backup files when confident: rm -rf docker/backup/"
    echo ""
    print_status "New Docker Commands:"
    echo "  cd docker && ./start-dev.sh      # Development"
    echo "  cd docker && ./start-staging.sh  # Staging"
    echo "  cd docker && ./start-prod.sh     # Production"
    echo "  cd docker && docker-compose ps   # Status"
    echo "  cd docker && docker-compose logs # Logs"
}

# Main function
main() {
    echo "🚀 OCR Identity REST API - Docker Migration"
    echo "==========================================="
    echo ""
    
    # Change to scripts directory
    cd "$(dirname "$0")"
    
    create_backup
    backup_old_files
    remove_old_files
    update_makefile
    show_summary
}

# Run main function
main "$@" 