# Testing Guide

This document provides comprehensive information about testing the OCR Identity REST API, including the media management features.

## 🧪 Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_media_models.py     # Unit tests for Media and Mediable models
├── test_media_utils.py      # Unit tests for MediaManager utilities
├── test_database_operations.py # Database operation tests
└── test_integration.py      # Integration tests for complete workflows
```

## 🚀 Quick Start

### Run All Tests
```bash
make test
# or
python scripts/run_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only
make test-unit
python scripts/run_tests.py --unit

# Integration tests only
make test-integration
python scripts/run_tests.py --integration

# With coverage report
make test-cov
python scripts/run_tests.py --coverage

# In watch mode (auto-rerun on changes)
make test-watch
python scripts/run_tests.py --watch
```

### Advanced Test Options
```bash
# Verbose output
make test-verbose
python scripts/run_tests.py --verbose

# Stop on first failure
make test-fast
python scripts/run_tests.py --fast

# Custom pytest arguments
python scripts/run_tests.py -k "test_media_creation"
```

## 📋 Test Categories

### 1. Unit Tests (`test_media_models.py`)

#### Media Model Tests
- **Media Creation**: Test creating media records with all fields
- **Parent-Child Relationships**: Test media hierarchy (original → thumbnail)
- **Soft Delete**: Test soft delete functionality
- **String Representation**: Test `__repr__` methods
- **Polymorphic Relationships**: Test polymorphic relationship properties

#### Mediable Model Tests
- **Mediable Creation**: Test creating polymorphic relationships
- **Relationship Validation**: Test foreign key constraints
- **String Representation**: Test `__repr__` methods

#### Model Relationship Tests
- **User Media Relationships**: Test User model media properties
- **Document Media Relationships**: Test IdentityDocument model media properties
- **Group Filtering**: Test filtering media by groups
- **Relationship Queries**: Test relationship queries

### 2. Utility Tests (`test_media_utils.py`)

#### MediaManager Tests
- **Media Creation**: Test `create_media()` method
- **Media Attachment**: Test `attach_media_to_model()` method
- **Media Detachment**: Test `detach_media_from_model()` method
- **Media Queries**: Test various query methods
- **Media Deletion**: Test soft delete functionality
- **Edge Cases**: Test error conditions and edge cases

#### Convenience Function Tests
- **User Functions**: Test `attach_media_to_user()` and `get_user_media()`
- **Document Functions**: Test `attach_media_to_document()` and `get_document_media()`
- **Group Filtering**: Test group-based filtering

### 3. Database Tests (`test_database_operations.py`)

#### Database Structure Tests
- **Table Structure**: Verify all required fields exist
- **Foreign Key Constraints**: Test relationship integrity
- **Index Usage**: Test query performance with indexes
- **Cascade Operations**: Test cascade delete behavior

#### Query Tests
- **Basic Queries**: Test simple SELECT operations
- **Complex Queries**: Test multi-condition queries
- **Join Queries**: Test relationship queries
- **Bulk Operations**: Test performance with large datasets

### 4. Integration Tests (`test_integration.py`)

#### Complete Workflow Tests
- **User Media Workflow**: Complete user media management
- **Document Media Workflow**: Complete document media management
- **Media Hierarchy**: Test parent-child media relationships
- **Multi-Model Media**: Test shared media across models
- **Bulk Operations**: Test large-scale operations

#### Error Handling Tests
- **Invalid References**: Test handling of invalid foreign keys
- **Non-existent Resources**: Test graceful error handling
- **Edge Cases**: Test boundary conditions

## 🛠️ Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

### Test Fixtures (`conftest.py`)

#### Database Fixtures
- **`db_session`**: In-memory SQLite database for testing
- **`sample_user`**: Test user with basic data
- **`sample_document`**: Test identity document
- **`sample_media`**: Test media record
- **`sample_mediable`**: Test polymorphic relationship

#### Usage Example
```python
def test_media_creation(db_session, sample_user):
    """Test creating media with user reference"""
    media = Media(
        name="Test Media",
        file_name="test.jpg",
        disk="local",
        mime_type="image/jpeg",
        size=1024000,
        created_by=sample_user.id
    )
    
    db_session.add(media)
    db_session.commit()
    
    assert media.id is not None
    assert media.created_by == sample_user.id
```

## 📊 Coverage Requirements

### Coverage Targets
- **Overall Coverage**: Minimum 80%
- **Model Coverage**: 100% for all models
- **Utility Coverage**: 100% for MediaManager
- **Integration Coverage**: 90% for workflows

### Coverage Reports
```bash
# Generate HTML coverage report
make test-cov

# View coverage in browser
open htmlcov/index.html
```

## 🔧 Test Utilities

### MediaManager Test Helpers
```python
# Create test media
media = MediaManager.create_media(
    db=db_session,
    name="Test Media",
    file_name="test.jpg",
    disk="s3",
    mime_type="image/jpeg",
    size=1024000,
    created_by=user.id
)

# Attach to model
attach_media_to_user(db_session, user, media, group="profile")

# Query media
user_media = get_user_media(db_session, user, group="profile")
```

### Database Test Helpers
```python
# Create test data
user = User(username="testuser", email="test@example.com")
db_session.add(user)
db_session.commit()

# Verify relationships
assert media.creator == user
assert media in user.created_media
```

## 🚨 Common Test Issues

### 1. Database Session Issues
**Problem**: Tests failing due to session state
**Solution**: Use fresh `db_session` fixture for each test

### 2. UUID Generation Issues
**Problem**: UUID conflicts in tests
**Solution**: Use `uuid.uuid4()` for test data

### 3. Relationship Loading Issues
**Problem**: Lazy loading not working in tests
**Solution**: Use `db_session.refresh()` after commits

### 4. Coverage Issues
**Problem**: Coverage not including all files
**Solution**: Ensure all modules are imported in tests

## 📈 Performance Testing

### Bulk Operations
```python
def test_bulk_media_operations(db_session, sample_user):
    """Test performance with large datasets"""
    # Create 100 media items
    media_list = []
    for i in range(100):
        media = MediaManager.create_media(...)
        media_list.append(media)
    
    # Test bulk attachment
    for media in media_list:
        attach_media_to_user(db_session, sample_user, media)
    
    # Verify performance
    user_media = get_user_media(db_session, sample_user)
    assert len(user_media) == 100
```

### Query Performance
```python
def test_query_performance(db_session, sample_user):
    """Test query performance with indexes"""
    # Create test data
    for i in range(1000):
        media = MediaManager.create_media(...)
        attach_media_to_user(db_session, sample_user, media)
    
    # Test indexed queries
    start_time = time.time()
    user_media = get_user_media(db_session, sample_user)
    query_time = time.time() - start_time
    
    assert query_time < 1.0  # Should complete in under 1 second
```

## 🔍 Debugging Tests

### Verbose Output
```bash
python scripts/run_tests.py --verbose -k "test_media_creation"
```

### Debug Specific Test
```bash
# Run single test with debugger
python -m pytest tests/test_media_models.py::TestMediaModel::test_media_creation -s
```

### Coverage Debug
```bash
# Generate detailed coverage report
python scripts/run_tests.py --coverage --verbose
```

## 📝 Writing New Tests

### Test Naming Convention
```python
def test_media_creation_with_parent(db_session, sample_user):
    """Test creating media with parent relationship"""
    # Test implementation
```

### Test Structure
```python
def test_feature_name(db_session, sample_user):
    """Test description"""
    # 1. Setup
    media = MediaManager.create_media(...)
    
    # 2. Execute
    result = attach_media_to_user(db_session, sample_user, media)
    
    # 3. Verify
    assert result is not None
    assert len(sample_user.media) == 1
```

### Test Categories
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test complete workflows
- **Performance Tests**: Test with large datasets
- **Error Tests**: Test error conditions

## 🎯 Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fresh fixtures for each test
- Clean up test data

### 2. Test Data
- Use realistic test data
- Test edge cases and boundary conditions
- Include error scenarios

### 3. Test Coverage
- Aim for 100% coverage of critical paths
- Test both success and failure scenarios
- Test performance with realistic data volumes

### 4. Test Maintenance
- Keep tests up to date with code changes
- Refactor tests when code is refactored
- Remove obsolete tests

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/) 