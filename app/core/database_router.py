"""
Database router for multi-database support
"""
from typing import Dict, Any, Optional
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_multi_database_config


class DatabaseRouter:
    """Router for handling multiple databases"""
    
    def __init__(self):
        self.config = get_multi_database_config()
        self._model_database_map: Dict[str, str] = {}
        self._database_metadata_map: Dict[str, MetaData] = {}
        
        # Initialize default routing
        self._init_default_routing()
    
    def _init_default_routing(self):
        """Initialize default model to database routing"""
        # Default routing - all models go to default database
        default_models = [
            'User', 'People', 'Media', 'IdentityDocument', 
            'AuditLog', 'OCRJob', 'Mediable'
        ]
        
        for model_name in default_models:
            self._model_database_map[model_name] = "default"
        
        # Analytics database routing
        analytics_models = [
            'AnalyticsEvent', 'UserActivity', 'SystemMetrics'
        ]
        
        for model_name in analytics_models:
            self._model_database_map[model_name] = "analytics"
        
        # Logging database routing
        logging_models = [
            'ApplicationLog', 'ErrorLog', 'AccessLog'
        ]
        
        for model_name in logging_models:
            self._model_database_map[model_name] = "logging"
        
        # Archive database routing
        archive_models = [
            'ArchivedMedia', 'ArchivedPeople', 'ArchivedUser'
        ]
        
        for model_name in archive_models:
            self._model_database_map[model_name] = "archive"
    
    def get_database_for_model(self, model_class: Any) -> str:
        """Get database name for a model class"""
        model_name = model_class.__name__
        
        # Check if model has explicit database binding
        if hasattr(model_class, '__database__'):
            return model_class.__database__
        
        # Check routing map
        if model_name in self._model_database_map:
            database_name = self._model_database_map[model_name]
            # Verify database is configured
            if self.config.get_database_config(database_name):
                return database_name
        
        # Default to main database
        return "default"
    
    def get_metadata_for_database(self, database_name: str) -> MetaData:
        """Get metadata for specific database"""
        if database_name not in self._database_metadata_map:
            self._database_metadata_map[database_name] = MetaData()
        return self._database_metadata_map[database_name]
    
    def get_all_metadata(self) -> Dict[str, MetaData]:
        """Get all database metadata"""
        databases = self.config.get_all_databases()
        metadata_dict = {}
        
        for db_name in databases.keys():
            metadata_dict[db_name] = self.get_metadata_for_database(db_name)
        
        return metadata_dict
    
    def add_model_to_database(self, model_class: Any, database_name: str):
        """Add model to specific database"""
        model_name = model_class.__name__
        self._model_database_map[model_name] = database_name
        
        # Set database binding on model class
        setattr(model_class, '__database__', database_name)
    
    def get_models_for_database(self, database_name: str) -> list:
        """Get all models for a specific database"""
        models = []
        for model_name, db_name in self._model_database_map.items():
            if db_name == database_name:
                models.append(model_name)
        return models
    
    def is_database_configured(self, database_name: str) -> bool:
        """Check if database is configured"""
        return self.config.get_database_config(database_name) is not None


# Global router instance
database_router = DatabaseRouter()


def get_database_router() -> DatabaseRouter:
    """Get the database router instance"""
    return database_router 