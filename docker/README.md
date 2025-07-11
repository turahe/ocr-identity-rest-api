# Docker Setup - OCR Identity REST API

This directory contains optimized Docker Compose configurations for the OCR Identity REST API with support for multiple environments and database configurations.

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

## 📁 File Structure

```
docker/
├── docker-compose.yml          # Main configuration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.staging.yml  # Staging overrides
├── docker-compose.prod.yml     # Production overrides
├── docker-compose.multi-db.yml # Multi-database setup
├── start-dev.sh               # Development startup script
├── start-staging.sh           # Staging startup script
├── start-prod.sh              # Production startup script
└── README.md                  # This file
```

## 🚀 Quick Start

### Development Environment

```bash
# Navigate to docker directory
cd docker

# Start development environment
./start-dev.sh
```

### Staging Environment

```bash
# Start staging environment
./start-staging.sh
```

### Production Environment

```bash
# Start production environment
./start-prod.sh
```

### Multi-Database Setup

```bash
# Start with multiple databases
docker-compose -f docker-compose.yml -f docker-compose.multi-db.yml up -d
```

## 🔧 Environment-Specific Configurations

### Development
- **Ports**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis), 9000/9001 (MinIO), 8025 (Mailpit)
- **Resources**: Optimized for development with reduced memory usage
- **Features**: Hot reload, debug mode, development tools
- **Volumes**: Code mounted for live development

### Staging
- **Ports**: 8001 (API), 5433 (PostgreSQL), 6380 (Redis), 9002/9003 (MinIO), 8026 (Mailpit)
- **Resources**: Moderate resource allocation
- **Features**: Optimized for testing, separate from development
- **Volumes**: Code mounted for testing

### Production
- **Ports**: 8002 (API), 5434 (PostgreSQL), 6381 (Redis), 9004/9005 (MinIO)
- **Resources**: High resource allocation for performance
- **Features**: Production optimizations, no debug mode
- **Volumes**: Optimized for production deployment

## 📊 Service Ports by Environment

| Service | Development | Staging | Production |
|---------|-------------|---------|------------|
| **API** | 8000 | 8001 | 8002 |
| **PostgreSQL** | 5432 | 5433 | 5434 |
| **Redis** | 6379 | 6380 | 6381 |
| **MinIO API** | 9000 | 9002 | 9004 |
| **MinIO Console** | 9001 | 9003 | 9005 |
| **Mailpit SMTP** | 1025 | 1026 | - |
| **Mailpit UI** | 8025 | 8026 | - |
| **Debug Port** | 5678 | - | - |

## 🗄️ Multi-Database Configuration

The multi-database setup includes:

- **Default Database**: Main application data
- **Analytics Database**: Performance metrics and analytics
- **Logging Database**: Application logs and audit trails
- **Archive Database**: Historical data and backups

### Multi-Database Ports

| Database | Port | Purpose |
|----------|------|---------|
| Default | 5432 | Main application data |
| Analytics | 5433 | Performance metrics |
| Logging | 5434 | Application logs |
| Archive | 5435 | Historical data |

## 🔧 Resource Management

### Development Resources
```yaml
app:
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.25'
```

### Staging Resources
```yaml
app:
  deploy:
    resources:
      limits:
        memory: 1.5G
        cpus: '1.5'
      reservations:
        memory: 768M
        cpus: '0.5'
```

### Production Resources
```yaml
app:
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: '4.0'
      reservations:
        memory: 2G
        cpus: '1.0'
```

## 🐳 Docker Compose Commands

### Basic Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Show status
docker-compose ps

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

### Environment-Specific Commands

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Multi-database
docker-compose -f docker-compose.yml -f docker-compose.multi-db.yml up -d
```

### Service Management

```bash
# Start specific service
docker-compose up -d app

# Stop specific service
docker-compose stop celery_worker_ocr

# View logs for specific service
docker-compose logs -f app

# Execute command in container
docker-compose exec app poetry run python main.py
```

## 🔍 Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping` command
- **MinIO**: HTTP health endpoint
- **Application**: HTTP health endpoint
- **Mailpit**: HTTP health endpoint

## 📈 Performance Optimizations

### Redis Configuration
```bash
redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-} --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### PostgreSQL Configuration
- Optimized for different environments
- Separate data volumes
- Health checks with timeouts

### MinIO Configuration
- S3-compatible object storage
- Console for management
- Health monitoring

## 🔒 Security Features

### Network Isolation
- Custom bridge network
- Isolated subnet (172.20.0.0/16)
- Service-to-service communication

### Resource Limits
- Memory and CPU limits per service
- Environment-specific resource allocation
- Prevention of resource exhaustion

### Health Monitoring
- Automatic health checks
- Service dependency management
- Graceful startup/shutdown

## 🛠️ Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service_name

# Check resource usage
docker stats

# Restart service
docker-compose restart service_name
```

#### Database Connection Issues
```bash
# Check database health
docker-compose exec postgres pg_isready -U postgres

# Check database logs
docker-compose logs postgres
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
# or use environment-specific overrides
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Use different ports in environment-specific files
```

### Debug Commands

```bash
# Enter container
docker-compose exec app bash

# Check service status
docker-compose ps

# View all logs
docker-compose logs

# Check network
docker network ls
docker network inspect docker_ocr_network
```

## 📋 Environment Variables

### Required Variables
```bash
# Database
DB_NAME=ocr_identity_db
DB_USERNAME=postgres
DB_PASSWORD=postgres

# Redis
REDIS_PASSWORD=your_redis_password

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Application
SECRET_KEY=your-secret-key-change-in-production
```

### Optional Variables
```bash
# Sentry
SENTRY_DSN=https://your-sentry-dsn-here@sentry.io/project-id
SENTRY_RELEASE=2.0.0
SENTRY_SERVER_NAME=ocr-identity-api
SENTRY_ENVIRONMENT=development

# Multi-database
DB_ANALYTICS_NAME=ocr_analytics_db
DB_LOGGING_NAME=ocr_logging_db
DB_ARCHIVE_NAME=ocr_archive_db
```

## 🚀 Deployment

### Development Deployment
```bash
cd docker
./start-dev.sh
```

### Staging Deployment
```bash
cd docker
./start-staging.sh
```

### Production Deployment
```bash
cd docker
./start-prod.sh
```

### Multi-Database Deployment
```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.multi-db.yml up -d
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [MinIO Documentation](https://min.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

When contributing to the Docker setup:

1. Test changes in development environment first
2. Update documentation for new features
3. Ensure backward compatibility
4. Add appropriate health checks
5. Optimize resource usage
6. Update startup scripts if needed

## 📄 License

This Docker setup is part of the OCR Identity REST API project and follows the same license terms. 