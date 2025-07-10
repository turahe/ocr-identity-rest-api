# OCR Identity REST API Makefile
# Usage: make <target>

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
APP_NAME := ocr-identity-api
PYTHON_VERSION := 3.12

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)OCR Identity REST API - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# Development Commands
# =============================================================================

.PHONY: install
install: ## Install Python dependencies
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install black isort flake8 mypy pytest pytest-asyncio pytest-cov
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

.PHONY: dev
dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	./start-dev.sh

.PHONY: staging
staging: ## Start staging environment
	@echo "$(BLUE)Starting staging environment...$(NC)"
	./start-staging.sh

.PHONY: prod
prod: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	./start-prod.sh

.PHONY: run
run: ## Run the application locally
	@echo "$(BLUE)Running application...$(NC)"
	$(PYTHON) main.py

.PHONY: run-reload
run-reload: ## Run with auto-reload
	@echo "$(BLUE)Running with auto-reload...$(NC)"
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# =============================================================================
# Docker Commands
# =============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	$(DOCKER) build -t $(APP_NAME) .

.PHONY: docker-build-dev
docker-build-dev: ## Build development Docker image
	@echo "$(BLUE)Building development Docker image...$(NC)"
	$(DOCKER) build --target development -t $(APP_NAME)-dev .

.PHONY: docker-build-staging
docker-build-staging: ## Build staging Docker image
	@echo "$(BLUE)Building staging Docker image...$(NC)"
	$(DOCKER) build --target staging -t $(APP_NAME)-staging .

.PHONY: docker-build-prod
docker-build-prod: ## Build production Docker image
	@echo "$(BLUE)Building production Docker image...$(NC)"
	$(DOCKER) build --target production -t $(APP_NAME)-prod .

.PHONY: docker-up
docker-up: ## Start all Docker services
	@echo "$(BLUE)Starting Docker services...$(NC)"
	$(DOCKER_COMPOSE) up -d

.PHONY: docker-down
docker-down: ## Stop all Docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	$(DOCKER_COMPOSE) down

.PHONY: docker-logs
docker-logs: ## Show Docker logs
	@echo "$(BLUE)Showing Docker logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f

.PHONY: docker-clean
docker-clean: ## Clean Docker containers and images
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER) system prune -f

# =============================================================================
# Database Commands
# =============================================================================

.PHONY: db-init
db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	$(PYTHON) scripts/migrate.py init

.PHONY: db-migrate
db-migrate: ## Create new migration
	@echo "$(BLUE)Creating new migration...$(NC)"
	@read -p "Enter migration name: " name; \
	$(PYTHON) scripts/migrate.py create "$$name"

.PHONY: db-upgrade
db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(NC)"
	$(PYTHON) scripts/migrate.py upgrade

.PHONY: db-downgrade
db-downgrade: ## Rollback database migrations
	@echo "$(BLUE)Rolling back database migrations...$(NC)"
	$(PYTHON) scripts/migrate.py downgrade

.PHONY: db-current
db-current: ## Show current migration
	@echo "$(BLUE)Current migration:$(NC)"
	$(PYTHON) scripts/migrate.py current

.PHONY: db-history
db-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	$(PYTHON) scripts/migrate.py history

.PHONY: db-reset
db-reset: ## Reset database (drop and recreate)
	@echo "$(YELLOW)⚠️  This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)Resetting database...$(NC)"; \
		$(PYTHON) scripts/migrate.py downgrade base; \
		$(PYTHON) scripts/migrate.py upgrade; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

# =============================================================================
# Testing Commands
# =============================================================================

.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	python scripts/run_tests.py

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	python scripts/run_tests.py --unit

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	python scripts/run_tests.py --integration

.PHONY: test-cov
test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	python scripts/run_tests.py --coverage

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	python scripts/run_tests.py --watch

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests with verbose output...$(NC)"
	python scripts/run_tests.py --verbose

.PHONY: test-fast
test-fast: ## Run tests and stop on first failure
	@echo "$(BLUE)Running tests (stop on first failure)...$(NC)"
	python scripts/run_tests.py --fast

.PHONY: lint
lint: ## Run linting
	@echo "$(BLUE)Running linting...$(NC)"
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

.PHONY: lint-fix
lint-fix: ## Fix linting issues
	@echo "$(BLUE)Fixing linting issues...$(NC)"
	black app/ tests/
	isort app/ tests/

.PHONY: type-check
type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	mypy app/

# =============================================================================
# Code Quality Commands
# =============================================================================

.PHONY: format
format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	black app/ tests/
	isort app/ tests/

.PHONY: check
check: ## Run all checks (lint, type, test)
	@echo "$(BLUE)Running all checks...$(NC)"
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

.PHONY: pre-commit
pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	$(MAKE) format
	$(MAKE) check

# =============================================================================
# Utility Commands
# =============================================================================

.PHONY: clean
clean: ## Clean Python cache and temporary files
	@echo "$(BLUE)Cleaning cache and temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/
	@echo "$(GREEN)✓ Clean complete$(NC)"

.PHONY: requirements
requirements: ## Update requirements.txt
	@echo "$(BLUE)Updating requirements.txt...$(NC)"
	$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ Requirements updated$(NC)"

.PHONY: shell
shell: ## Start Python shell
	@echo "$(BLUE)Starting Python shell...$(NC)"
	$(PYTHON) -i

.PHONY: logs
logs: ## Show application logs
	@echo "$(BLUE)Showing application logs...$(NC)"
	tail -f logs/app.log

.PHONY: status
status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@echo "$(GREEN)✓ Docker services:$(NC)"
	$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(GREEN)✓ Database migration status:$(NC)"
	$(PYTHON) scripts/migrate.py current

# =============================================================================
# Documentation Commands
# =============================================================================

.PHONY: docs
docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(NC)"
	$(PYTHON) -c "import uvicorn; from main import app; print('API docs available at: http://localhost:8000/docs')"

.PHONY: open-docs
open-docs: ## Open API documentation in browser
	@echo "$(BLUE)Opening API documentation...$(NC)"
	xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null || echo "Please open http://localhost:8000/docs in your browser"

# =============================================================================
# Deployment Commands
# =============================================================================

.PHONY: deploy-dev
deploy-dev: ## Deploy to development environment
	@echo "$(BLUE)Deploying to development...$(NC)"
	$(MAKE) docker-build-dev
	$(MAKE) docker-up

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	$(MAKE) docker-build-staging
	$(DOCKER_COMPOSE) -f docker-compose.staging.yml up -d

.PHONY: deploy-prod
deploy-prod: ## Deploy to production environment
	@echo "$(YELLOW)⚠️  Deploying to production...$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)Deploying to production...$(NC)"; \
		$(MAKE) docker-build-prod; \
		$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d; \
		echo "$(GREEN)✓ Production deployment complete$(NC)"; \
	else \
		echo "$(YELLOW)Production deployment cancelled$(NC)"; \
	fi

# =============================================================================
# Backup and Restore Commands
# =============================================================================

.PHONY: backup
backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec -T postgres pg_dump -U postgres ocr_identity_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup created$(NC)"

.PHONY: restore
restore: ## Restore database from backup
	@echo "$(YELLOW)⚠️  This will overwrite current database!$(NC)"
	@read -p "Enter backup file path: " backup_file; \
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)Restoring database...$(NC)"; \
		$(DOCKER_COMPOSE) exec -T postgres psql -U postgres ocr_identity_db < "$$backup_file"; \
		echo "$(GREEN)✓ Database restored$(NC)"; \
	else \
		echo "$(YELLOW)Database restore cancelled$(NC)"; \
	fi

# =============================================================================
# Monitoring Commands
# =============================================================================

.PHONY: monitor
monitor: ## Monitor system resources
	@echo "$(BLUE)Monitoring system resources...$(NC)"
	@echo "$(GREEN)CPU and Memory:$(NC)"
	top -bn1 | grep "Cpu(s)" | awk '{print $$2}' | awk -F'%' '{print $$1}'
	@echo "$(GREEN)Docker containers:$(NC)"
	$(DOCKER) stats --no-stream

.PHONY: health
health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo "$(GREEN)API Health:$(NC)"
	curl -f http://localhost:8000/health || echo "$(RED)API is down$(NC)"
	@echo "$(GREEN)Database Health:$(NC)"
	$(DOCKER_COMPOSE) exec -T postgres pg_isready -U postgres || echo "$(RED)Database is down$(NC)"
	@echo "$(GREEN)Redis Health:$(NC)"
	$(DOCKER_COMPOSE) exec -T redis redis-cli ping || echo "$(RED)Redis is down$(NC)"

# =============================================================================
# Development Setup
# =============================================================================

.PHONY: setup
setup: ## Complete development setup
	@echo "$(BLUE)Setting up development environment...$(NC)"
	$(MAKE) install-dev
	$(MAKE) docker-up
	@echo "$(BLUE)Waiting for services to start...$(NC)"
	sleep 30
	$(MAKE) db-upgrade
	@echo "$(GREEN)✓ Development setup complete$(NC)"
	@echo "$(BLUE)Access points:$(NC)"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  MinIO Console: http://localhost:9001"
	@echo "  Mailpit UI: http://localhost:8025"

.PHONY: setup-fresh
setup-fresh: ## Fresh development setup (clean everything first)
	@echo "$(BLUE)Performing fresh development setup...$(NC)"
	$(MAKE) clean
	$(MAKE) docker-clean
	$(MAKE) setup

# =============================================================================
# Quick Commands
# =============================================================================

.PHONY: quick-start
quick-start: ## Quick start for development
	@echo "$(BLUE)Quick starting development environment...$(NC)"
	$(MAKE) setup
	$(MAKE) run-reload

.PHONY: restart
restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	$(MAKE) docker-down
	$(MAKE) docker-up
	@echo "$(GREEN)✓ Services restarted$(NC)"

.PHONY: rebuild
rebuild: ## Rebuild and restart services
	@echo "$(BLUE)Rebuilding and restarting services...$(NC)"
	$(MAKE) docker-down
	$(MAKE) docker-build
	$(MAKE) docker-up
	@echo "$(GREEN)✓ Services rebuilt and restarted$(NC)" 