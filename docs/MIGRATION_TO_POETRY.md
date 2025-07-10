# Migration to Poetry - Dependency Management

This guide explains the migration from `requirements.txt` to Poetry for dependency management in the OCR Identity REST API project.

## 🚀 Why Poetry?

### Benefits of Poetry
- **Dependency Resolution**: Automatic resolution of dependency conflicts
- **Lock File**: Reproducible builds with `poetry.lock`
- **Virtual Environment Management**: Automatic virtual environment creation
- **Project Packaging**: Easy packaging and distribution
- **Modern Standards**: PEP 517/518 compliant
- **Development Groups**: Separate dev, test, and production dependencies

### Comparison

| Feature | requirements.txt | Poetry |
|---------|-----------------|---------|
| Dependency Resolution | Manual | Automatic |
| Lock File | No | Yes (poetry.lock) |
| Virtual Environment | Manual | Automatic |
| Development Dependencies | Mixed | Separate groups |
| Project Metadata | None | pyproject.toml |
| Scripts | None | Built-in support |

## 📦 Migration Steps

### 1. Install Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

### 2. Initialize Poetry Project

```bash
# Navigate to project directory
cd ocr-identity-rest-api

# Initialize Poetry (if not already done)
poetry init
```

### 3. Convert Dependencies

The `pyproject.toml` file has been created with all dependencies from `requirements.txt`:

#### Production Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.12"
uvicorn = {extras = ["standard"], version = "^0.34.1"}
sqlalchemy = "^2.0.27"
celery = "^5.3.4"
boto3 = "^1.34.0"
# ... and more
```

#### Development Dependencies
```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
black = "^23.11.0"
flake8 = "^6.1.0"
mypy = "^1.7.1"
# ... and more
```

### 4. Install Dependencies

```bash
# Install all dependencies (including dev)
poetry install

# Install only production dependencies
poetry install --only=main

# Install with specific groups
poetry install --with=dev,docs
```

## 🔄 Command Migration

### Old Commands (requirements.txt)
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Run tests
pytest

# Format code
black app/
```

### New Commands (Poetry)
```bash
# Install dependencies
poetry install

# Run application
poetry run python main.py
# or
poetry run uvicorn main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black app/
```

## 🐳 Docker Changes

### Updated Dockerfile
The Dockerfile now uses Poetry instead of pip:

```dockerfile
# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only=main --no-root
```

### Updated docker-compose.yml
```yaml
services:
  app:
    build:
      context: .
      target: development
    command: poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🛠️ Development Workflow

### Using Poetry Shell
```bash
# Activate Poetry virtual environment
poetry shell

# Now you can run commands directly
python main.py
pytest
black app/
```

### Using Poetry Run
```bash
# Run commands in Poetry environment without activating shell
poetry run python main.py
poetry run pytest
poetry run black app/
```

### Using Makefile
The Makefile has been updated to use Poetry:

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Show all commands
make help
```

## 📋 Dependency Management

### Adding Dependencies
```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Add with specific version
poetry add "package-name>=1.0.0,<2.0.0"
```

### Updating Dependencies
```bash
# Update all dependencies
poetry update

# Update specific dependency
poetry update package-name
```

### Removing Dependencies
```bash
# Remove dependency
poetry remove package-name

# Remove from specific group
poetry remove --group dev package-name
```

## 🔧 Configuration

### Poetry Configuration
```bash
# Configure Poetry to create virtual environments in project directory
poetry config virtualenvs.in-project true

# Configure Poetry to not ask for credentials
poetry config http-basic.pypi __token__ ""
```

### Environment Variables
The `.env` file remains the same, but you can now use Poetry to manage environment-specific dependencies.

## 📊 Project Structure

### New Files
- `pyproject.toml` - Project configuration and dependencies
- `poetry.lock` - Locked dependency versions
- `scripts/install_poetry.sh` - Poetry installation script

### Updated Files
- `Dockerfile` - Uses Poetry instead of pip
- `docker-compose.yml` - Updated commands to use Poetry
- `Makefile` - Updated to use Poetry commands
- `README.md` - Updated with Poetry instructions

### Removed Files
- `requirements.txt` - Replaced by pyproject.toml and poetry.lock

## 🧪 Testing the Migration

### 1. Install Poetry
```bash
# Run the installation script
./scripts/install_poetry.sh
```

### 2. Test Installation
```bash
# Test Poetry installation
poetry --version

# Test Python in Poetry environment
poetry run python --version

# Test key dependencies
poetry run python -c "import fastapi, sqlalchemy, celery, boto3; print('All dependencies available')"
```

### 3. Test Application
```bash
# Start services
docker-compose up -d

# Run migrations
poetry run alembic upgrade head

# Start application
poetry run uvicorn main:app --reload
```

## 🔍 Troubleshooting

### Common Issues

#### Poetry not found
```bash
# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

#### Virtual environment issues
```bash
# Remove existing virtual environment
poetry env remove python

# Create new virtual environment
poetry install
```

#### Dependency conflicts
```bash
# Update Poetry lock file
poetry lock --no-update

# Update all dependencies
poetry update
```

#### Docker build issues
```bash
# Clean Docker cache
docker system prune -a

# Rebuild with no cache
docker-compose build --no-cache
```

## 📈 Benefits Achieved

### 1. Better Dependency Management
- Automatic conflict resolution
- Reproducible builds
- Clear separation of dev/prod dependencies

### 2. Improved Development Experience
- Automatic virtual environment management
- Built-in script support
- Better project structure

### 3. Enhanced Docker Integration
- Multi-stage builds with Poetry
- Optimized layer caching
- Environment-specific configurations

### 4. Modern Python Standards
- PEP 517/518 compliance
- Standard project metadata
- Better packaging support

## 🚀 Next Steps

1. **Remove requirements.txt**: The file is no longer needed
2. **Update CI/CD**: Update any CI/CD pipelines to use Poetry
3. **Team Onboarding**: Share this guide with team members
4. **Documentation**: Update any project documentation
5. **Monitoring**: Monitor for any issues during the transition

## 📚 Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry GitHub Repository](https://github.com/python-poetry/poetry)
- [PEP 517 - Build System Interface](https://www.python.org/dev/peps/pep-0517/)
- [PEP 518 - Specifying Build System Requirements](https://www.python.org/dev/peps/pep-0518/)

---

**Note**: This migration provides a more robust and modern dependency management system while maintaining all existing functionality. The Poetry-based setup is more maintainable and follows Python best practices. 