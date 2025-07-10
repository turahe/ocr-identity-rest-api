#!/bin/bash

# OCR Identity REST API - Poetry Installation Script
# This script installs Poetry and sets up the project dependencies

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

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
}

# Check Python version
check_python_version() {
    print_status "Checking Python version..."
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.11"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        print_success "Python version $PYTHON_VERSION meets requirements (>= $REQUIRED_VERSION)"
    else
        print_error "Python version $PYTHON_VERSION is too old. Please install Python $REQUIRED_VERSION or higher."
        exit 1
    fi
}

# Install Poetry
install_poetry() {
    print_status "Installing Poetry..."
    
    if command -v poetry &> /dev/null; then
        POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
        print_success "Poetry $POETRY_VERSION is already installed"
    else
        print_status "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        
        # Add Poetry to PATH if not already there
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            export PATH="$HOME/.local/bin:$PATH"
            print_warning "Added Poetry to PATH. Please restart your terminal or run 'source ~/.bashrc'"
        fi
        
        print_success "Poetry installed successfully"
    fi
}

# Configure Poetry
configure_poetry() {
    print_status "Configuring Poetry..."
    
    # Configure Poetry to create virtual environments in project directory
    poetry config virtualenvs.in-project true
    
    # Configure Poetry to not ask for credentials
    poetry config http-basic.pypi __token__ ""
    
    print_success "Poetry configured successfully"
}

# Install project dependencies
install_dependencies() {
    print_status "Installing project dependencies..."
    
    if [ -f "pyproject.toml" ]; then
        poetry install
        print_success "Dependencies installed successfully"
    else
        print_error "pyproject.toml not found. Are you in the correct directory?"
        exit 1
    fi
}

# Create environment file
create_env_file() {
    print_status "Setting up environment file..."
    
    if [ ! -f ".env" ]; then
        if [ -f "config.example.env" ]; then
            cp config.example.env .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your configuration"
        else
            print_warning "No config.example.env found. Please create .env file manually"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Setup development environment
setup_dev_environment() {
    print_status "Setting up development environment..."
    
    # Install development dependencies
    poetry install --with=dev
    
    # Create necessary directories
    mkdir -p storage/images logs
    
    print_success "Development environment setup completed"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Poetry
    if poetry --version &> /dev/null; then
        print_success "Poetry is working correctly"
    else
        print_error "Poetry is not working correctly"
        exit 1
    fi
    
    # Test Python in Poetry environment
    if poetry run python -c "import sys; print('Python in Poetry environment:', sys.version)" &> /dev/null; then
        print_success "Python in Poetry environment is working"
    else
        print_error "Python in Poetry environment is not working"
        exit 1
    fi
    
    # Test key dependencies
    DEPENDENCIES=("fastapi" "sqlalchemy" "celery" "boto3")
    for dep in "${DEPENDENCIES[@]}"; do
        if poetry run python -c "import $dep; print('$dep imported successfully')" &> /dev/null; then
            print_success "$dep is available"
        else
            print_warning "$dep is not available (this might be normal for optional dependencies)"
        fi
    done
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Poetry installation completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Start Docker services: docker-compose up -d"
    echo "3. Run database migrations: poetry run alembic upgrade head"
    echo "4. Setup MinIO: poetry run python scripts/setup_minio.py"
    echo "5. Start the application: poetry run uvicorn main:app --reload"
    echo ""
    echo "📚 Useful commands:"
    echo "  poetry shell          - Activate Poetry virtual environment"
    echo "  poetry run pytest     - Run tests"
    echo "  poetry run black .    - Format code"
    echo "  make help            - Show all available commands"
    echo ""
    echo "🌐 Access points:"
    echo "  API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  MinIO Console: http://localhost:9001"
    echo "  Mailpit: http://localhost:8025"
    echo ""
}

# Main installation function
main() {
    echo "🚀 OCR Identity REST API - Poetry Installation"
    echo "=============================================="
    echo ""
    
    check_python
    check_python_version
    install_poetry
    configure_poetry
    install_dependencies
    create_env_file
    setup_dev_environment
    test_installation
    show_next_steps
}

# Run main function
main "$@" 