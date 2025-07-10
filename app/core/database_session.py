"""
Database session management for SQLAlchemy
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_database_config
from app.models.base import Base


def create_database_engine():
    """Create database engine"""
    config = get_database_config()
    
    engine = create_engine(
        config.database_url,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        echo=config.echo,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    return engine


def create_session_factory():
    """Create session factory"""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


# Create global session factory
SessionLocal = create_session_factory()


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables"""
    engine = create_database_engine()
    Base.metadata.drop_all(bind=engine) 