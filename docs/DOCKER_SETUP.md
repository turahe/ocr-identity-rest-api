# Multi-Stage Docker Setup

This project includes a comprehensive multi-stage Docker setup supporting development, staging, and production environments.

## 🏗️ Architecture Overview

### Docker Stages
- **Base**: Common dependencies and setup
- **Development**: Hot reload, debugging, development tools
- **Staging**: Testing environment with optimized settings
- **Production**: Production-ready with Gunicorn, resource limits

### Environment-Specific Configurations
- **Development**: `docker-compose.dev.yml` + `config.dev.env`
- **Staging**: `docker-compose.staging.yml` + `config.staging.env`
- **Production**: `docker-compose.prod.yml` + `config.prod.env`

## 🚀 Quick Start

### Development Environment
```bash
./start-dev.sh
```

### Staging Environment
```bash
./start-staging.sh
```

### Production Environment
```bash
cp config.prod.env .env
# Edit .env with your production settings
./start-prod.sh
```

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

## 🔧 Dockerfile Stages

### Base Stage
```dockerfile
FROM python:3.11-slim as base
```
- Common Python dependencies
- System packages (gcc, libpq-dev, curl)
- Non-root user setup
- Base environment variables

### Development Stage
```dockerfile
FROM base as development
```
- Development tools (pytest, black, flake8, mypy)
- Debugging support (debugpy)
- Hot reload enabled
- Volume mounting for live code changes

### Staging Stage
```dockerfile
FROM base as staging
```
- Optimized for testing
- Multiple workers (2)
- Info-level logging
- Separate database and storage

### Production Stage
```dockerfile
FROM base as production
```
- Gunicorn with Uvicorn workers
- Multiple replicas (2+)
- Resource limits configured
- Warning-level logging
- Health checks

## 📁 Configuration Files

### Environment Configurations
- `config.dev.env` - Development settings
- `config.staging.env` - Staging settings  
- `config.prod.env` - Production settings
- `config.example.env` - Template configuration

### Docker Compose Files
- `docker-compose.dev.yml` - Development services
- `docker-compose.staging.yml` - Staging services
- `docker-compose.prod.yml` - Production services

### Startup Scripts
- `start-dev.sh` - Development startup
- `start-staging.sh` - Staging startup
- `start-prod.sh` - Production startup

## 🛠️ Manual Commands

### Development
```bash
# Build development image
docker build --target development -t ocr-identity:dev .

# Start development services
docker-compose -f docker-compose.dev.yml --profile dev up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f app

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Staging
```bash
# Build staging image
docker build --target staging -t ocr-identity:staging .

# Start staging services
docker-compose -f docker-compose.staging.yml --profile staging up -d

# View logs
docker-compose -f docker-compose.staging.yml logs -f app

# Stop services
docker-compose -f docker-compose.staging.yml down
```

### Production
```bash
# Build production image
docker build --target production -t ocr-identity:prod .

# Start production services
docker-compose -f docker-compose.prod.yml --profile prod up -d

# Scale application
docker-compose -f docker-compose.prod.yml up --scale app=3

# View logs
docker-compose -f docker-compose.prod.yml logs -f app

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## 🔍 Environment Differences

### Development
- **Hot Reload**: Enabled for live code changes
- **Debug Mode**: Full debugging support
- **Debug Port**: 5678 for remote debugging
- **Logging**: Debug level
- **Database**: Echo SQL queries
- **Workers**: Single worker with reload

### Staging
- **Hot Reload**: Disabled
- **Debug Mode**: Disabled
- **Logging**: Info level
- **Database**: No SQL echo
- **Workers**: 2 workers
- **Separate Ports**: Different ports to avoid conflicts

### Production
- **Hot Reload**: Disabled
- **Debug Mode**: Disabled
- **Logging**: Warning level
- **Database**: Optimized connection pool
- **Workers**: 4+ workers with Gunicorn
- **Resource Limits**: CPU and memory limits
- **Health Checks**: Comprehensive health monitoring
- **Replicas**: Multiple app instances

## 🔒 Security Considerations

### Development
- Default passwords (safe for local development)
- Debug mode enabled
- Verbose logging
- No SSL/TLS

### Staging
- Default passwords (change for shared environments)
- Debug mode disabled
- Moderate logging
- No SSL/TLS

### Production
- **REQUIRED**: Change all default passwords
- **REQUIRED**: Use strong SECRET_KEY
- **REQUIRED**: Configure SSL/TLS
- **REQUIRED**: Set up firewall rules
- **RECOMMENDED**: Use external database
- **RECOMMENDED**: Use external Redis
- **RECOMMENDED**: Use external S3/MinIO

## 📈 Performance Optimizations

### Development
- Minimal resource usage
- Fast build times
- Development tools included

### Staging
- Moderate resource usage
- Testing optimizations
- Separate data volumes

### Production
- **Resource Limits**: CPU and memory limits
- **Connection Pooling**: Optimized database connections
- **Caching**: Redis for session and data caching
- **Load Balancing**: Multiple app replicas
- **Health Checks**: Comprehensive monitoring
- **Logging**: Structured logging with appropriate levels

## 🐛 Debugging

### Development Debugging
```bash
# Attach debugger
docker exec -it ocr_app_dev python -m debugpy --listen 0.0.0.0:5678 --wait-for-client main.py

# View real-time logs
docker-compose -f docker-compose.dev.yml logs -f app

# Access container shell
docker exec -it ocr_app_dev /bin/bash
```

### Staging Testing
```bash
# Run tests
docker exec -it ocr_app_staging pytest

# Check health
curl http://localhost:8001/health

# Monitor performance
docker stats ocr_app_staging
```

### Production Monitoring
```bash
# Check service health
docker-compose -f docker-compose.prod.yml ps

# View resource usage
docker stats

# Check logs
docker-compose -f docker-compose.prod.yml logs -f app

# Scale services
docker-compose -f docker-compose.prod.yml up --scale app=3
```

## 🔄 CI/CD Integration

### Build Commands
```bash
# Development build
docker build --target development -t ocr-identity:dev .

# Staging build
docker build --target staging -t ocr-identity:staging .

# Production build
docker build --target production -t ocr-identity:prod .
```

### Environment Variables
```bash
# Development
export ENVIRONMENT=development
export DEBUG=true

# Staging
export ENVIRONMENT=staging
export DEBUG=false

# Production
export ENVIRONMENT=production
export DEBUG=false
```

## 📝 Best Practices

### Development
1. Use hot reload for rapid development
2. Enable debug mode for troubleshooting
3. Use local volumes for code changes
4. Monitor resource usage

### Staging
1. Test with production-like settings
2. Use separate databases and storage
3. Validate configuration changes
4. Test scaling and performance

### Production
1. **ALWAYS** change default passwords
2. Use strong secrets and keys
3. Configure SSL/TLS
4. Set up monitoring and alerting
5. Regular security updates
6. Backup strategies
7. Disaster recovery plans

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Use different ports
export APP_PORT=8001
```

#### Database Connection Issues
```bash
# Check database health
docker-compose logs postgres

# Test connection
docker exec -it ocr_postgres_dev psql -U postgres -d ocr_identity_db
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Adjust resource limits in docker-compose files
```

#### Build Issues
```bash
# Clean build
docker-compose build --no-cache

# Rebuild specific stage
docker build --target development -t ocr-identity:dev .
```

## 📚 Additional Resources

- [Docker Multi-Stage Builds](https://docs.docker.com/develop/dev-best-practices/multistage-build/)
- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html) 