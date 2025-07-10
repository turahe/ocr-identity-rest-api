# OCR Identity REST API v2.0.0

A modern, scalable REST API for OCR identity document processing with S3 storage, database metadata management, and background task processing using Celery.

## 🚀 Features

### Core Functionality
- **OCR Processing**: Extract text from identity documents (passports, ID cards, driver licenses)
- **spaCy NER**: Advanced Named Entity Recognition for accurate information extraction
- **S3 Storage**: Secure file storage with MinIO (S3-compatible)
- **Database Metadata**: PostgreSQL with comprehensive media management
- **Background Processing**: Celery workers for async OCR and media processing
- **Polymorphic Media**: Flexible media relationships across models
- **REST API**: FastAPI with automatic documentation

### Architecture
- **Microservices**: Docker containers for each service
- **Queue-based Processing**: Redis-backed Celery for background tasks
- **Object Storage**: S3-compatible storage with MinIO
- **Database**: PostgreSQL 17 with Alembic migrations
- **Caching**: Redis for session and task management
- **Email Testing**: Mailpit for development email testing
- **Dependency Management**: Poetry for modern Python packaging

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Celery Workers │    │   PostgreSQL    │
│   (Port 8000)   │    │  (OCR/Media)    │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MinIO (S3)    │    │     Redis       │    │    Mailpit      │
│  (Port 9000)    │    │   (Port 6379)   │    │   (Port 8025)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Poetry (for dependency management)
- Git

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ocr-identity-rest-api
```

### 2. Install Poetry (if not installed)
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

### 3. Environment Configuration
```bash
# Copy environment template
cp config.example.env .env

# Edit environment variables
nano .env
```

### 4. Install Dependencies
```bash
# Install all dependencies (including dev)
poetry install

# Or install only production dependencies
poetry install --only=main
```

### 5. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 6. Initialize Database and Models
```bash
# Run migrations
poetry run alembic upgrade head

# Create MinIO bucket
poetry run python scripts/setup_minio.py

# Download spaCy models
poetry run python scripts/download_spacy_models.py
```

### 7. Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
- **Mailpit**: http://localhost:8025

## 🔧 Configuration

### Environment Variables

#### Database
```env
DB_HOST=postgres
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_NAME=ocr_identity_db
```

#### Redis
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
```

#### S3/MinIO
```env
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
S3_BUCKET_NAME=ocr-identity-bucket
S3_ENDPOINT_URL=http://minio:9000
S3_USE_SSL=false
S3_VERIFY_SSL=false
```

#### Application
```env
SECRET_KEY=your-secret-key-change-in-production
DEBUG=false
ENVIRONMENT=development
```

## 📡 API Endpoints

### File Upload & Processing

#### Upload Image (Async)
```http
POST /upload-image/
Content-Type: multipart/form-data

file: [image file]
user_id: [optional]
```

**Response:**
```json
{
  "status": "uploading",
  "task_id": "abc123-def456",
  "filename": "passport.jpg",
  "content_type": "image/jpeg",
  "message": "File upload started. Use task_id to check status."
}
```

#### Upload Image (Sync)
```http
POST /upload-image-sync/
Content-Type: multipart/form-data

file: [image file]
user_id: [optional]
```

**Response:**
```json
{
  "status": "success",
  "media_id": "uuid-here",
  "s3_key": "uploads/abc123.jpg",
  "s3_url": "http://minio:9000/bucket/uploads/abc123.jpg",
  "file_hash": "abc123...",
  "file_size": 1024000,
  "ocr_task_id": "def456-ghi789",
  "message": "File uploaded and OCR processing started"
}
```

### Task Management

#### Get Task Status
```http
GET /task/{task_id}
```

**Response:**
```json
{
  "task_id": "abc123-def456",
  "state": "SUCCESS",
  "result": {
    "status": "success",
    "media_id": "uuid-here",
    "ocr_job_id": "job-uuid",
    "extracted_text": "PASSPORT...",
    "processing_time_ms": 1500
  }
}
```

### Media Management

#### Get Media Information
```http
GET /media/{media_id}
```

#### Get OCR Results
```http
GET /media/{media_id}/ocr
```

#### Delete Media
```http
DELETE /media/{media_id}
```

### Health Check
```http
GET /health
```

## 🗄️ Database Schema

### Media Table
```sql
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    hash VARCHAR(255),
    file_name VARCHAR(255) NOT NULL,
    disk VARCHAR(255) NOT NULL,  -- 's3', 'local'
    mime_type VARCHAR(255) NOT NULL,
    size INTEGER NOT NULL,
    record_left BIGINT,
    record_right BIGINT,
    record_dept BIGINT,
    record_ordering BIGINT,
    parent_id UUID REFERENCES media(id),
    custom_attribute VARCHAR(255),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_by UUID REFERENCES users(id),
    deleted_at BIGINT,
    created_at BIGINT,
    updated_at BIGINT
);
```

### Mediable Table (Polymorphic Relationships)
```sql
CREATE TABLE mediables (
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,
    mediable_id UUID NOT NULL,
    mediable_type VARCHAR(255) NOT NULL,
    group VARCHAR(255) NOT NULL,
    PRIMARY KEY (media_id, mediable_id)
);
```

### OCR Jobs Table
```sql
CREATE TABLE ocr_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES identity_documents(id) ON DELETE CASCADE,
    job_status VARCHAR(50) DEFAULT 'pending',
    input_file_path VARCHAR(500),
    output_data JSONB,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at BIGINT,
    updated_at BIGINT
);
```

## 🔄 Background Processing

### Celery Workers

#### OCR Worker
```bash
# Start OCR worker
poetry run python scripts/start_celery_worker.py --worker --queue ocr --concurrency 2
```

#### Media Worker
```bash
# Start media worker
poetry run python scripts/start_celery_worker.py --worker --queue media --concurrency 4
```

#### Beat Scheduler
```bash
# Start beat scheduler
poetry run python scripts/start_celery_worker.py --beat
```

### Task Types

#### OCR Tasks
- `process_ocr_image`: Process single image OCR
- `process_bulk_ocr`: Process multiple images
- `cleanup_failed_ocr_jobs`: Clean up failed jobs

#### Media Tasks
- `upload_media_to_s3`: Upload file to S3
- `process_media_batch`: Process multiple files
- `cleanup_orphaned_media`: Clean up orphaned records
- `generate_media_thumbnails`: Generate image thumbnails

## 🐳 Docker Services

### Core Services
- **app**: FastAPI application
- **postgres**: PostgreSQL 17 database
- **redis**: Redis cache and message broker
- **minio**: S3-compatible object storage
- **mailpit**: Email testing service

### Celery Services
- **celery_worker_ocr**: OCR processing worker
- **celery_worker_media**: Media processing worker
- **celery_beat**: Task scheduler

## 🛠️ Development

### Local Development
```bash
# Install development dependencies
poetry install

# Run migrations
poetry run alembic upgrade head

# Start services
docker-compose up -d postgres redis minio

# Run application
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Using Makefile
```bash
# Show all available commands
make help

# Quick development setup
make dev-setup

# Quick start with Docker
make quick-start

# Run tests
make test

# Code quality checks
make check
```

### Poetry Commands
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Run commands in Poetry environment
poetry run python main.py
poetry run pytest
poetry run black app/

# Activate Poetry shell
poetry shell
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test categories
poetry run pytest tests/test_media_models.py
poetry run pytest tests/test_ocr_tasks.py
poetry run pytest tests/test_integration.py
```

### Code Quality
```bash
# Format code
poetry run black app/ tests/ scripts/
poetry run isort app/ tests/ scripts/

# Lint code
poetry run flake8 app/ tests/ scripts/

# Type checking
poetry run mypy app/ scripts/
```

## 📊 Monitoring

### Task Monitoring
```bash
# Check Celery worker status
poetry run celery -A app.core.celery_app inspect active

# Monitor task queues
poetry run celery -A app.core.celery_app inspect stats
```

### Database Monitoring
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d ocr_identity_db

# Check media records
SELECT COUNT(*) FROM media;

# Check OCR jobs
SELECT job_status, COUNT(*) FROM ocr_jobs GROUP BY job_status;
```

### S3/MinIO Monitoring
- Access MinIO Console: http://localhost:9001
- Default credentials: minioadmin/minioadmin
- Check bucket contents and access logs

## 🔒 Security

### File Upload Security
- File size limits (configurable)
- File type validation
- Hash-based deduplication
- Secure S3 access with presigned URLs

### Database Security
- Connection pooling
- Prepared statements
- Soft delete for data retention
- Audit logging

### API Security
- Input validation
- Error handling
- Rate limiting (configurable)
- CORS configuration

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-secret-key>

# Database
DB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# S3 (AWS or other provider)
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
S3_BUCKET_NAME=<your-bucket>
```

### Scaling
```bash
# Scale workers
docker-compose up -d --scale celery_worker_ocr=3 --scale celery_worker_media=2

# Scale application
docker-compose up -d --scale app=3
```

### Monitoring
- Set up logging aggregation
- Configure health checks
- Monitor resource usage
- Set up alerting

## 📝 Changelog

### v2.0.0
- **S3 Storage**: Replaced local file storage with S3/MinIO
- **Database Metadata**: Added comprehensive media management
- **Background Processing**: Implemented Celery for async tasks
- **Polymorphic Media**: Added flexible media relationships
- **API Enhancement**: New endpoints for task and media management
- **Docker Optimization**: Multi-service architecture with Celery workers
- **Poetry Migration**: Modern dependency management with Poetry

### v1.0.0
- Basic OCR functionality
- Local file storage
- Simple REST API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `/docs`

---

**Note**: This is a production-ready OCR identity document processing API with modern architecture, scalable design, and comprehensive testing. The system is designed to handle high-volume document processing with background task management and secure file storage.