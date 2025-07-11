# OCR Identity REST API - Makefile
# Poetry-based dependency management

.PHONY: help install install-dev install-prod install-docs clean test test-coverage lint format type-check docker-up docker-down docker-logs docker-clean db-upgrade db-current db-reset setup-minio start-app start-worker start-beat health status monitor

# Default target
help:
	@echo "OCR Identity REST API - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "📦 Installation:"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  install-docs   - Install documentation dependencies"
	@echo "  clean          - Clean Poetry cache and build files"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-watch     - Run tests in watch mode"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  lint           - Run linting (flake8)"
	@echo "  format         - Format code (black + isort)"
	@echo "  type-check     - Run type checking (mypy)"
	@echo "  check          - Run all quality checks"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-up      - Start all Docker services"
	@echo "  docker-down    - Stop all Docker services"
	@echo "  docker-logs    - Show Docker logs"
	@echo "  docker-clean   - Clean Docker containers and volumes"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  db-upgrade     - Run database migrations"
	@echo "  db-current     - Show current migration"
	@echo "  db-reset       - Reset database (DANGER!)"
	@echo ""
	@echo "⚙️  Setup:"
	@echo "  setup-minio    - Setup MinIO bucket and configuration"
	@echo ""
	@echo "🚀 Application:"
	@echo "  start-app      - Start FastAPI application"
	@echo "  start-worker   - Start Celery worker"
	@echo "  start-beat     - Start Celery beat scheduler"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  health         - Check service health"
	@echo "  status         - Show service status"
	@echo "  monitor        - Monitor system resources"

# =============================================================================
# Installation
# =============================================================================

install:
	@echo "📦 Installing production dependencies..."
	poetry install --only=main --no-dev

install-dev:
	@echo "📦 Installing development dependencies..."
	poetry install --with=dev

install-docs:
	@echo "📦 Installing documentation dependencies..."
	poetry install --with=docs

clean:
	@echo "🧹 Cleaning Poetry cache and build files..."
	poetry cache clear . --all
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# =============================================================================
# Testing
# =============================================================================

test:
	@echo "🧪 Running tests..."
	poetry run pytest

test-coverage:
	@echo "🧪 Running tests with coverage..."
	poetry run pytest --cov=app --cov-report=html --cov-report=term

test-watch:
	@echo "🧪 Running tests in watch mode..."
	poetry run pytest-watch

# =============================================================================
# Code Quality
# =============================================================================

lint:
	@echo "🔍 Running linting..."
	poetry run flake8 app/ tests/ scripts/ main.py

format:
	@echo "🎨 Formatting code..."
	poetry run black app/ tests/ scripts/ main.py
	poetry run isort app/ tests/ scripts/ main.py

type-check:
	@echo "🔍 Running type checking..."
	poetry run mypy app/ scripts/ main.py

check: lint format type-check test
	@echo "✅ All quality checks passed!"

# =============================================================================
# Docker Commands
# =============================================================================

docker-up:
	@echo "🐳 Starting Docker services..."
	cd docker && docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker services..."
	cd docker && docker-compose down

docker-logs:
	@echo "📋 Showing Docker logs..."
	cd docker && docker-compose logs -f

docker-clean:
	@echo "🧹 Cleaning Docker containers and volumes..."
	cd docker && docker-compose down -v --remove-orphans
	docker system prune -f

# =============================================================================
# Database Commands
# =============================================================================

db-upgrade:
	@echo "🗄️  Running database migrations..."
	poetry run alembic upgrade head

db-current:
	@echo "🗄️  Showing current migration..."
	poetry run alembic current

db-reset:
	@echo "⚠️  WARNING: This will reset the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "🗄️  Resetting database..."; \
		poetry run alembic downgrade base; \
		poetry run alembic upgrade head; \
	else \
		echo "❌ Database reset cancelled."; \
	fi

# =============================================================================
# Setup Commands
# =============================================================================

setup-minio:
	@echo "⚙️  Setting up MinIO bucket and configuration..."
	poetry run python scripts/setup_minio.py

setup-spacy:
	@echo "📦 Setting up spaCy models..."
	poetry run python scripts/download_spacy_models.py

fix-spacy:
	@echo "🔧 Fixing spaCy installation issues..."
	poetry run python scripts/fix_spacy_installation.py

# =============================================================================
# Application Commands
# =============================================================================

start-app:
	@echo "🚀 Starting FastAPI application..."
	poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

start-worker:
	@echo "🚀 Starting Celery worker..."
	poetry run python scripts/start_celery_worker.py --worker --queue default

start-beat:
	@echo "🚀 Starting Celery beat scheduler..."
	poetry run python scripts/start_celery_worker.py --beat

# =============================================================================
# Monitoring Commands
# =============================================================================

health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Health check failed"

status:
	@echo "📊 Service status:"
	@cd docker && docker-compose ps

monitor:
	@echo "📊 Monitoring system resources..."
	@echo "Docker containers:"
	@docker stats --no-stream
	@echo ""
	@echo "Disk usage:"
	@df -h
	@echo ""
	@echo "Memory usage:"
	@free -h

# =============================================================================
# Development Workflow
# =============================================================================

dev-setup: install-dev setup-minio
	@echo "✅ Development setup completed!"

quick-start: docker-up
	@echo "⏳ Waiting for services to start..."
	@sleep 10
	@make db-upgrade
	@make setup-minio
	@make setup-spacy
	@echo "🚀 Quick start completed! Access the API at http://localhost:8000"

# =============================================================================
# Production Commands
# =============================================================================

prod-build:
	@echo "🏗️  Building production image..."
	docker build --target production -t ocr-identity-api:prod .

prod-run:
	@echo "🚀 Running production container..."
	docker run -d --name ocr-identity-api-prod \
		-p 8000:8000 \
		--env-file .env \
		ocr-identity-api:prod

# =============================================================================
# Utility Commands
# =============================================================================

shell:
	@echo "🐚 Starting Poetry shell..."
	poetry shell

add-dependency:
	@echo "📦 Adding new dependency..."
	@read -p "Enter package name: " package; \
	poetry add $$package

add-dev-dependency:
	@echo "📦 Adding new development dependency..."
	@read -p "Enter package name: " package; \
	poetry add --group dev $$package

update-dependencies:
	@echo "📦 Updating dependencies..."
	poetry update

lock:
	@echo "🔒 Updating Poetry lock file..."
	poetry lock

export-requirements:
	@echo "📋 Exporting requirements.txt..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# =============================================================================
# Documentation
# =============================================================================

docs-serve:
	@echo "📚 Serving documentation..."
	poetry run mkdocs serve

docs-build:
	@echo "📚 Building documentation..."
	poetry run mkdocs build

# =============================================================================
# Testing Utilities
# =============================================================================

# Note: test-upload command removed as test_upload.py was deleted

test-celery:
	@echo "🧪 Testing Celery tasks..."
	poetry run celery -A app.core.celery_app inspect active

test-s3:
	@echo "🧪 Testing S3 connection..."
	poetry run python -c "from app.services.s3_service import s3_service; print('S3 service initialized successfully')"

# =============================================================================
# Backup and Restore
# =============================================================================

backup-db:
	@echo "💾 Creating database backup..."
	cd docker && docker-compose exec postgres pg_dump -U postgres ocr_identity_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:
	@echo "📥 Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	cd docker && docker-compose exec -T postgres psql -U postgres ocr_identity_db < $$backup_file 