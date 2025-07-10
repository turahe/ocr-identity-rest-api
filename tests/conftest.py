"""
Pytest configuration and fixtures for testing
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.models.user import User
from app.models.identity_document import IdentityDocument
from app.models.media import Media
from app.models.mediable import Mediable
from app.utils.media_utils import MediaManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Clean up
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_document(db_session, sample_user):
    """Create a sample identity document for testing."""
    document = IdentityDocument(
        user_id=sample_user.id,
        document_type="passport",
        document_number="TEST123456",
        issuing_country="USA",
        status="pending"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


@pytest.fixture
def sample_media(db_session, sample_user):
    """Create a sample media record for testing."""
    media = Media(
        name="Test Image",
        file_name="test.jpg",
        disk="local",
        mime_type="image/jpeg",
        size=1024000,
        created_by=sample_user.id,
        hash="testhash123",
        custom_attribute="test_media"
    )
    db_session.add(media)
    db_session.commit()
    db_session.refresh(media)
    return media


@pytest.fixture
def sample_mediable(db_session, sample_media, sample_user):
    """Create a sample mediable relationship for testing."""
    mediable = Mediable(
        media_id=sample_media.id,
        mediable_id=sample_user.id,
        mediable_type="User",
        group="profile"
    )
    db_session.add(mediable)
    db_session.commit()
    db_session.refresh(mediable)
    return mediable 