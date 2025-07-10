# Database Migrations with Alembic

This project uses Alembic for database migrations, providing a robust way to manage database schema changes across different environments.

## 🏗️ Architecture

### Migration Structure
```
migrations/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Migration template
└── versions/           # Migration files
    └── 0001_initial_schema.py
```

### Models Structure
```
app/models/
├── __init__.py         # Model registry and metadata
├── base.py            # Base model class
├── user.py            # User model
├── identity_document.py # Identity document model
├── ocr_job.py         # OCR job model
└── audit_log.py       # Audit log model
```

## 🚀 Quick Start

### 1. Initialize Migrations (First Time)
```bash
# Initialize Alembic
python scripts/migrate.py init

# Create initial migration
python scripts/migrate.py create "Initial schema"

# Apply migrations
python scripts/migrate.py upgrade
```

### 2. Development Workflow
```bash
# Create a new migration
python scripts/migrate.py create "Add new feature"

# Apply migrations
python scripts/migrate.py upgrade

# Check current status
python scripts/migrate.py current
```

### 3. Docker Environment
```bash
# Development
./start-dev.sh  # Includes automatic migrations

# Staging
./start-staging.sh  # Includes automatic migrations

# Production
./start-prod.sh  # Includes automatic migrations
```

## 📋 Migration Commands

### Basic Commands
```bash
# Check database connection
python scripts/migrate.py check

# Show migration history
python scripts/migrate.py history

# Show current revision
python scripts/migrate.py current

# Show pending migrations
python scripts/migrate.py pending
```

### Migration Management
```bash
# Create new migration
python scripts/migrate.py create "Add user table"

# Upgrade to latest
python scripts/migrate.py upgrade

# Upgrade to specific revision
python scripts/migrate.py upgrade 0002

# Downgrade to specific revision
python scripts/migrate.py downgrade 0001

# Stamp database (mark as current without running)
python scripts/migrate.py stamp head
```

### Docker Commands
```bash
# Run migrations in development
docker-compose -f docker-compose.dev.yml exec app alembic upgrade head

# Run migrations in staging
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head

# Run migrations in production
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Identity Documents Table
```sql
CREATE TABLE identity_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    document_number VARCHAR(255),
    issuing_country VARCHAR(100),
    issue_date DATE,
    expiry_date DATE,
    extracted_data JSONB,
    file_path VARCHAR(500),
    s3_key VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    verification_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### Alembic Configuration (`alembic.ini`)
```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/ocr_identity_db
```

### Environment Configuration (`migrations/env.py`)
- Uses application configuration for database URL
- Imports all models for autogenerate support
- Configures logging and connection pooling

### Model Registry (`app/models/__init__.py`)
```python
from .base import Base
from .user import User
from .identity_document import IdentityDocument
from .ocr_job import OCRJob
from .audit_log import AuditLog

# Create metadata for Alembic
metadata = Base.metadata
```

## 📝 Creating Migrations

### 1. Model Changes
When you modify a model, create a migration:

```bash
# After modifying models
python scripts/migrate.py create "Add new field to user table"
```

### 2. Manual Migration
For complex changes, create manual migrations:

```python
# In migration file
def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('phone', sa.String(20)))
    
    # Create index
    op.create_index('ix_users_phone', 'users', ['phone'])

def downgrade() -> None:
    # Remove index
    op.drop_index('ix_users_phone', table_name='users')
    
    # Remove column
    op.drop_column('users', 'phone')
```

### 3. Data Migrations
For data changes:

```python
def upgrade() -> None:
    # Update existing data
    op.execute("UPDATE users SET is_verified = true WHERE email LIKE '%@company.com'")

def downgrade() -> None:
    # Revert data changes
    op.execute("UPDATE users SET is_verified = false WHERE email LIKE '%@company.com'")
```

## 🔍 Migration Best Practices

### 1. Naming Conventions
- Use descriptive names: `add_user_table`, `add_email_index`
- Include ticket/issue numbers: `add_user_table_issue_123`
- Use present tense: `add`, `create`, `modify`, `remove`

### 2. Migration Structure
```python
"""Add user table

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Migration logic here
    pass

def downgrade() -> None:
    # Rollback logic here
    pass
```

### 3. Testing Migrations
```bash
# Test upgrade
python scripts/migrate.py upgrade

# Test downgrade
python scripts/migrate.py downgrade 0001

# Verify current state
python scripts/migrate.py current
```

### 4. Environment-Specific Migrations
```bash
# Development
docker-compose -f docker-compose.dev.yml exec app alembic upgrade head

# Staging
docker-compose -f docker-compose.staging.yml exec app alembic upgrade head

# Production
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check configuration
python scripts/migrate.py check

# Verify database is running
docker-compose ps postgres
```

#### 2. Migration Conflicts
```bash
# Check current revision
python scripts/migrate.py current

# Check migration history
python scripts/migrate.py history

# Resolve conflicts manually
# Edit migration files as needed
```

#### 3. Model Import Errors
```bash
# Ensure all models are imported
# Check app/models/__init__.py

# Verify model syntax
python -c "from app.models import *"
```

#### 4. Autogenerate Issues
```bash
# Check model metadata
python -c "from app.models import metadata; print(metadata.tables.keys())"

# Verify model relationships
python -c "from app.models import User; print(User.__table__.columns)"
```

### Debugging Commands
```bash
# Show detailed migration info
alembic show 0001

# Show migration SQL
alembic upgrade 0001 --sql

# Check migration dependencies
alembic heads

# Show migration branches
alembic branches
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Database Migrations
  run: |
    docker-compose -f docker-compose.prod.yml exec -T app alembic upgrade head
```

### Pre-deployment Checklist
- [ ] Test migrations in development
- [ ] Test migrations in staging
- [ ] Backup production database
- [ ] Run migrations in production
- [ ] Verify application functionality

## 📚 Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🔧 Advanced Features

### 1. Multiple Database Support
```python
# In env.py
def get_url():
    """Get database URL based on environment"""
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        return "postgresql://prod_user:prod_pass@prod_host/prod_db"
    return "postgresql://dev_user:dev_pass@dev_host/dev_db"
```

### 2. Custom Migration Operations
```python
# In migration file
def upgrade() -> None:
    # Custom operation
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
```

### 3. Conditional Migrations
```python
def upgrade() -> None:
    # Only run in specific environment
    if os.getenv("ENVIRONMENT") == "production":
        op.execute("CREATE INDEX CONCURRENTLY idx_users_email ON users(email)")
    else:
        op.create_index('idx_users_email', 'users', ['email'])
``` 