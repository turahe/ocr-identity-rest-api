# Multi-Database Support

This document describes the multi-database feature that allows the OCR Identity REST API to connect to and manage multiple databases simultaneously.

## Overview

The multi-database feature provides:

- **Database Routing**: Automatically route models to different databases based on configuration
- **Health Monitoring**: Monitor the health and status of all configured databases
- **Statistics**: Get detailed statistics for each database
- **Query Execution**: Execute queries on specific databases
- **Backup Information**: Get backup information for all databases

## Architecture

### Database Types

1. **Default Database** (`default`): Main application database
   - Models: User, People, Media, IdentityDocument, AuditLog, OCRJob, Mediable

2. **Analytics Database** (`analytics`): For analytics and reporting
   - Models: AnalyticsEvent, UserActivity, SystemMetrics

3. **Logging Database** (`logging`): For application logs
   - Models: ApplicationLog, ErrorLog, AccessLog

4. **Archive Database** (`archive`): For archived data
   - Models: ArchivedMedia, ArchivedPeople, ArchivedUser

### Configuration Structure

```python
class MultiDatabaseConfig:
    default: DatabaseConfig      # Main application database
    analytics: DatabaseConfig   # Analytics database (optional)
    logging: DatabaseConfig     # Logging database (optional)
    archive: DatabaseConfig     # Archive database (optional)
    routing: Dict[str, str]    # Model to database routing
```

## Setup

### 1. Environment Configuration

Copy the multi-database configuration template:

```bash
cp config.multi_db.example.env .env
```

Edit the `.env` file to configure your databases:

```env
# Main Database
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_NAME=ocr_identity_db

# Analytics Database
MULTI_DB_ANALYTICS_HOST=localhost
MULTI_DB_ANALYTICS_PORT=5433
MULTI_DB_ANALYTICS_USERNAME=postgres
MULTI_DB_ANALYTICS_PASSWORD=postgres
MULTI_DB_ANALYTICS_DATABASE=ocr_analytics_db

# Logging Database
MULTI_DB_LOGGING_HOST=localhost
MULTI_DB_LOGGING_PORT=5434
MULTI_DB_LOGGING_USERNAME=postgres
MULTI_DB_LOGGING_PASSWORD=postgres
MULTI_DB_LOGGING_DATABASE=ocr_logging_db

# Archive Database
MULTI_DB_ARCHIVE_HOST=localhost
MULTI_DB_ARCHIVE_PORT=5435
MULTI_DB_ARCHIVE_USERNAME=postgres
MULTI_DB_ARCHIVE_PASSWORD=postgres
MULTI_DB_ARCHIVE_DATABASE=ocr_archive_db
```

### 2. Docker Setup

Use the multi-database Docker Compose file:

```bash
# Start all services with multi-database support
./start-multi-db.sh

# Or manually
docker-compose -f docker-compose.multi-db.yml --profile multi-db up -d
```

### 3. Manual Setup

If you prefer to set up databases manually:

```bash
# Create databases
createdb ocr_identity_db
createdb ocr_analytics_db
createdb ocr_logging_db
createdb ocr_archive_db

# Run migrations
poetry run alembic upgrade head
```

## Usage

### Database Routing

Models are automatically routed to databases based on their type:

```python
from app.core.database_session import get_db_for_model
from app.models.user import User

# Get session for User model (routes to default database)
async def get_user_session():
    async for db in get_db_for_model(User):
        return db
```

### Manual Database Selection

```python
from app.core.database_session import get_db

# Get session for specific database
async def get_analytics_session():
    async for db in get_db("analytics"):
        return db
```

### Database Utilities

```python
from app.core.multi_database_utils import get_multi_database_utils

utils = get_multi_database_utils()

# Health check all databases
health_status = utils.health_check_all_databases()

# Get database statistics
stats = utils.get_all_database_stats()

# Get configured databases
databases = utils.get_configured_databases()
```

## API Endpoints

### Database Management

All endpoints require authentication (JWT or API Key).

#### Health Check All Databases

```http
GET /database/health
```

Response:
```json
{
  "default": {
    "database": "default",
    "status": "healthy",
    "test_query": 1,
    "database_name": "ocr_identity_db",
    "version": "PostgreSQL 17.0"
  },
  "analytics": {
    "database": "analytics",
    "status": "healthy",
    "test_query": 1,
    "database_name": "ocr_analytics_db",
    "version": "PostgreSQL 17.0"
  }
}
```

#### Get Database Statistics

```http
GET /database/stats
```

Response:
```json
{
  "default": {
    "database": "default",
    "table_count": 8,
    "database_size": "2.1 MB",
    "status": "available"
  },
  "analytics": {
    "database": "analytics",
    "table_count": 3,
    "database_size": "1.2 MB",
    "status": "available"
  }
}
```

#### Get Configured Databases

```http
GET /database/configured
```

Response:
```json
{
  "databases": ["default", "analytics", "logging", "archive"]
}
```

#### Get Models by Database

```http
GET /database/models
```

Response:
```json
{
  "default": ["User", "People", "Media", "IdentityDocument"],
  "analytics": ["AnalyticsEvent", "UserActivity", "SystemMetrics"],
  "logging": ["ApplicationLog", "ErrorLog", "AccessLog"],
  "archive": ["ArchivedMedia", "ArchivedPeople", "ArchivedUser"]
}
```

#### Health Check Specific Database

```http
GET /database/{database_name}/health
```

#### Get Statistics for Specific Database

```http
GET /database/{database_name}/stats
```

#### Get Models for Specific Database

```http
GET /database/{database_name}/models
```

Response:
```json
{
  "database": "analytics",
  "models": ["AnalyticsEvent", "UserActivity", "SystemMetrics"]
}
```

#### Execute Query on Database

```http
POST /database/{database_name}/execute
Content-Type: application/json

{
  "query": "SELECT COUNT(*) FROM users",
  "params": {}
}
```

Response:
```json
{
  "database": "default",
  "query": "SELECT COUNT(*) FROM users",
  "params": {},
  "result": [[5]]
}
```

#### Get Backup Information

```http
GET /database/backup/info
```

Response:
```json
{
  "default": {
    "host": "localhost",
    "port": 5432,
    "database": "ocr_identity_db",
    "username": "postgres",
    "url": "postgresql://postgres:postgres@localhost:5432/ocr_identity_db"
  },
  "analytics": {
    "host": "localhost",
    "port": 5433,
    "database": "ocr_analytics_db",
    "username": "postgres",
    "url": "postgresql://postgres:postgres@localhost:5433/ocr_analytics_db"
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_*` | Main database configuration | - |
| `MULTI_DB_ANALYTICS_*` | Analytics database configuration | - |
| `MULTI_DB_LOGGING_*` | Logging database configuration | - |
| `MULTI_DB_ARCHIVE_*` | Archive database configuration | - |
| `MULTI_DB_ROUTING` | Model to database routing | `{}` |

### Database Configuration Options

Each database supports these configuration options:

- `HOST`: Database host
- `PORT`: Database port
- `USERNAME`: Database username
- `PASSWORD`: Database password
- `DATABASE`: Database name
- `POOL_SIZE`: Connection pool size
- `MAX_OVERFLOW`: Maximum overflow connections
- `ECHO`: SQL query echo (for debugging)

## Development

### Adding New Models

1. Create your model class
2. Add it to the routing configuration in `app/core/database_router.py`
3. Update the database router's `_init_default_routing` method

```python
# In app/core/database_router.py
def _init_default_routing(self):
    # Add your model to the appropriate database
    analytics_models = [
        'AnalyticsEvent', 'UserActivity', 'SystemMetrics',
        'YourNewModel'  # Add here
    ]
```

### Custom Database Routing

You can set custom database routing for models:

```python
from app.core.database_router import get_database_router

router = get_database_router()
router.add_model_to_database(YourModel, "analytics")
```

### Database Utilities

The `MultiDatabaseUtils` class provides utilities for:

- Health checking databases
- Getting database statistics
- Executing queries on specific databases
- Managing database connections
- Getting backup information

## Monitoring

### Health Checks

Regular health checks are performed to ensure database connectivity:

```python
from app.core.multi_database_utils import health_check_all

# Check all databases
status = health_check_all()
```

### Statistics

Monitor database performance and usage:

```python
from app.core.multi_database_utils import get_database_stats_all

# Get statistics for all databases
stats = get_database_stats_all()
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in `.env`
   - Ensure database is running
   - Verify network connectivity

2. **Model Routing Issues**
   - Check model is registered in router
   - Verify database configuration exists
   - Check model's `__database__` attribute

3. **Migration Issues**
   - Run migrations for each database separately
   - Check database permissions
   - Verify database exists

### Debug Commands

```bash
# Check database health
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/database/health

# Get database statistics
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/database/stats

# Test specific database
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/database/analytics/health
```

## Performance Considerations

### Connection Pooling

Each database has its own connection pool:

- **Default**: 10 connections, 20 overflow
- **Analytics**: 5 connections, 10 overflow
- **Logging**: 5 connections, 10 overflow
- **Archive**: 3 connections, 5 overflow

### Query Optimization

- Use appropriate database for each query type
- Monitor query performance with database statistics
- Consider read replicas for analytics database

### Backup Strategy

- Regular backups for all databases
- Different backup schedules based on data importance
- Test restore procedures regularly

## Security

### Authentication

All database management endpoints require authentication:

- JWT token authentication
- API key authentication
- Role-based access control (future)

### Database Security

- Use strong passwords for all databases
- Limit database user permissions
- Enable SSL/TLS for database connections
- Regular security audits

## Migration from Single Database

1. **Backup existing data**
2. **Update configuration** to include multi-database settings
3. **Run migrations** on all databases
4. **Test thoroughly** before production deployment
5. **Monitor performance** and adjust as needed

## Future Enhancements

- **Read Replicas**: Support for read replicas
- **Sharding**: Automatic data sharding
- **Backup Automation**: Automated backup scheduling
- **Performance Monitoring**: Advanced performance metrics
- **Database Clustering**: Support for database clusters 