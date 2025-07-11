"""
Database session management for SQLAlchemy with multi-database support
"""
from typing import Generator, Dict, Optional, Any
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_database_config, get_multi_database_config
from app.core.database_router import get_database_router
from app.models.base import Base


class MultiDatabaseManager:
    """Manager for multiple database connections"""
    
    def __init__(self):
        self.config = get_multi_database_config()
        self.router = get_database_router()
        self._engines: Dict[str, Any] = {}
        self._session_factories: Dict[str, Any] = {}
        self._metadata: Dict[str, MetaData] = {}
    
    def get_engine(self, database_name: str = "default"):
        """Get or create engine for database"""
        if database_name not in self._engines:
            config = get_database_config(database_name)
            
            engine = create_engine(
                config.database_url,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                echo=config.echo,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self._engines[database_name] = engine
        
        return self._engines[database_name]
    
    def get_session_factory(self, database_name: str = "default"):
        """Get or create session factory for database"""
        if database_name not in self._session_factories:
            engine = self.get_engine(database_name)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self._session_factories[database_name] = SessionLocal
        
        return self._session_factories[database_name]
    
    def get_metadata(self, database_name: str = "default") -> MetaData:
        """Get metadata for database"""
        if database_name not in self._metadata:
            self._metadata[database_name] = MetaData()
        return self._metadata[database_name]
    
    def get_session(self, database_name: str = "default") -> Session:
        """Get database session for specific database"""
        session_factory = self.get_session_factory(database_name)
        return session_factory()
    
    def get_session_for_model(self, model_class) -> Session:
        """Get database session for specific model"""
        database_name = self.router.get_database_for_model(model_class)
        return self.get_session(database_name)
    
    def create_tables_for_database(self, database_name: str):
        """Create tables for specific database"""
        engine = self.get_engine(database_name)
        metadata = self.get_metadata(database_name)
        
        # Get models for this database
        models = self.router.get_models_for_database(database_name)
        
        # Create tables for models in this database
        for model_name in models:
            # Import and register model with metadata
            # This would need to be implemented based on your model structure
            pass
        
        metadata.create_all(bind=engine)
    
    def create_all_tables(self):
        """Create tables for all databases"""
        databases = self.config.get_all_databases()
        
        for database_name in databases.keys():
            if self.router.is_database_configured(database_name):
                self.create_tables_for_database(database_name)
    
    def drop_tables_for_database(self, database_name: str):
        """Drop tables for specific database"""
        engine = self.get_engine(database_name)
        metadata = self.get_metadata(database_name)
        metadata.drop_all(bind=engine)
    
    def drop_all_tables(self):
        """Drop tables for all databases"""
        databases = self.config.get_all_databases()
        
        for database_name in databases.keys():
            if self.router.is_database_configured(database_name):
                self.drop_tables_for_database(database_name)
    
    def close_all_engines(self):
        """Close all database engines"""
        for engine in self._engines.values():
            engine.dispose()
        self._engines.clear()
        self._session_factories.clear()


# Global multi-database manager
multi_db_manager = MultiDatabaseManager()


# Legacy functions for backward compatibility
def create_database_engine(database_name: str = "default"):
    """Create database engine for specific database"""
    return multi_db_manager.get_engine(database_name)


def create_session_factory(database_name: str = "default"):
    """Create session factory for specific database"""
    return multi_db_manager.get_session_factory(database_name)


# Create global session factory for default database (backward compatibility)
SessionLocal = multi_db_manager.get_session_factory("default")


def get_db(database_name: str = "default") -> Generator[Session, None, None]:
    """Get database session for specific database"""
    session_factory = multi_db_manager.get_session_factory(database_name)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def get_db_for_model(model_class) -> Generator[Session, None, None]:
    """Get database session for specific model"""
    db = multi_db_manager.get_session_for_model(model_class)
    try:
        yield db
    finally:
        db.close()


def create_tables(database_name: str = "default"):
    """Create tables for specific database"""
    multi_db_manager.create_tables_for_database(database_name)


def create_all_tables():
    """Create tables for all databases"""
    multi_db_manager.create_all_tables()


def drop_tables(database_name: str = "default"):
    """Drop tables for specific database"""
    multi_db_manager.drop_tables_for_database(database_name)


def drop_all_tables():
    """Drop tables for all databases"""
    multi_db_manager.drop_all_tables()


def close_all_connections():
    """Close all database connections"""
    multi_db_manager.close_all_engines() 