# Multi-stage Dockerfile for OCR Identity REST API
# Development, Staging, and Production environments

# =============================================================================
# BASE STAGE - Common dependencies and setup
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # OCR dependencies
    tesseract-ocr \
    tesseract-ocr-eng \
    # Image processing
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Database client
    postgresql-client \
    # Utilities
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# =============================================================================
# DEVELOPMENT STAGE
# =============================================================================
FROM base as development

# Install dependencies with dev group
RUN poetry install --only=main,dev --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/images logs

# Expose ports
EXPOSE 8000 5678

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# STAGING STAGE
# =============================================================================
FROM base as staging

# Install dependencies (no dev group)
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/images logs

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Staging command
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# PRODUCTION STAGE
# =============================================================================
FROM base as production

# Install dependencies (only main group)
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/images logs

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with Gunicorn
CMD ["poetry", "run", "gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]

# =============================================================================
# CELERY WORKER STAGE
# =============================================================================
FROM base as celery-worker

# Install dependencies with dev group for development
RUN poetry install --only=main,dev --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Create non-root user for production
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check for Celery
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD poetry run celery -A app.core.celery_app inspect ping || exit 1

# Default command (can be overridden)
CMD ["poetry", "run", "python", "scripts/start_celery_worker.py", "--worker", "--queue", "default"]

# =============================================================================
# CELERY BEAT STAGE
# =============================================================================
FROM base as celery-beat

# Install dependencies (only main group)
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check for Celery Beat
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD poetry run celery -A app.core.celery_app inspect ping || exit 1

# Beat command
CMD ["poetry", "run", "python", "scripts/start_celery_worker.py", "--beat"]