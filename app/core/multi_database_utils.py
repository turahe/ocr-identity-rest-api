"""
Multi-database utilities and management functions
"""
import asyncio
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import get_multi_database_config, get_database_config
from app.core.database_session import multi_db_manager
from app.core.database_router import get_database_router


class MultiDatabaseUtils:
    """Utilities for managing multiple databases"""
    
    def __init__(self):
        self.config = get_multi_database_config()
        self.router = get_database_router()
    
    def get_configured_databases(self) -> List[str]:
        """Get list of configured database names"""
        databases = []
        all_dbs = self.config.get_all_databases()
        
        for db_name, db_config in all_dbs.items():
            if db_config and self._is_database_accessible(db_name):
                databases.append(db_name)
        
        return databases
    
    def _is_database_accessible(self, database_name: str) -> bool:
        """Check if database is accessible"""
        try:
            engine = multi_db_manager.get_engine(database_name)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def health_check_database(self, database_name: str) -> Dict[str, Any]:
        """Perform health check on specific database"""
        try:
            engine = multi_db_manager.get_engine(database_name)
            with engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute(text("SELECT 1 as test"))
                test_result = result.fetchone()
                
                # Get database info
                db_info = conn.execute(text("SELECT current_database() as db_name, version() as version"))
                db_info_result = db_info.fetchone()
                
                return {
                    "database": database_name,
                    "status": "healthy",
                    "test_query": test_result[0] if test_result else None,
                    "database_name": db_info_result[0] if db_info_result else None,
                    "version": db_info_result[1] if db_info_result else None
                }
        except Exception as e:
            return {
                "database": database_name,
                "status": "unhealthy",
                "error": str(e)
            }
    
    def health_check_all_databases(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all configured databases"""
        results = {}
        databases = self.get_configured_databases()
        
        for db_name in databases:
            results[db_name] = self.health_check_database(db_name)
        
        return results
    
    def get_database_stats(self, database_name: str) -> Dict[str, Any]:
        """Get statistics for specific database"""
        try:
            engine = multi_db_manager.get_engine(database_name)
            with engine.connect() as conn:
                # Get table count
                table_count = conn.execute(text("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)).fetchone()
                
                # Get database size
                db_size = conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size
                """)).fetchone()
                
                return {
                    "database": database_name,
                    "table_count": table_count[0] if table_count else 0,
                    "database_size": db_size[0] if db_size else "Unknown",
                    "status": "available"
                }
        except Exception as e:
            return {
                "database": database_name,
                "status": "unavailable",
                "error": str(e)
            }
    
    def get_all_database_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all databases"""
        stats = {}
        databases = self.get_configured_databases()
        
        for db_name in databases:
            stats[db_name] = self.get_database_stats(db_name)
        
        return stats
    
    def get_models_by_database(self) -> Dict[str, List[str]]:
        """Get models grouped by database"""
        model_groups = {}
        databases = self.get_configured_databases()
        
        for db_name in databases:
            models = self.router.get_models_for_database(db_name)
            if models:
                model_groups[db_name] = models
        
        return model_groups
    
    def execute_on_database(self, database_name: str, query: str, params: Optional[Dict] = None) -> Any:
        """Execute query on specific database"""
        try:
            engine = multi_db_manager.get_engine(database_name)
            with engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result.fetchall()
        except Exception as e:
            raise Exception(f"Error executing query on {database_name}: {str(e)}")
    
    def execute_on_all_databases(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute query on all databases"""
        results = {}
        databases = self.get_configured_databases()
        
        for db_name in databases:
            try:
                results[db_name] = self.execute_on_database(db_name, query, params)
            except Exception as e:
                results[db_name] = {"error": str(e)}
        
        return results
    
    def backup_database_info(self) -> Dict[str, Any]:
        """Get backup information for all databases"""
        backup_info = {}
        databases = self.get_configured_databases()
        
        for db_name in databases:
            config = get_database_config(db_name)
            backup_info[db_name] = {
                "host": config.host,
                "port": config.port,
                "database": config.database,
                "username": config.username,
                "url": config.database_url
            }
        
        return backup_info


# Global utility instance
multi_db_utils = MultiDatabaseUtils()


def get_multi_database_utils() -> MultiDatabaseUtils:
    """Get the multi-database utilities instance"""
    return multi_db_utils


# Convenience functions
def health_check_all() -> Dict[str, Dict[str, Any]]:
    """Health check all databases"""
    return multi_db_utils.health_check_all_databases()


def get_database_stats_all() -> Dict[str, Dict[str, Any]]:
    """Get stats for all databases"""
    return multi_db_utils.get_all_database_stats()


def get_configured_databases() -> List[str]:
    """Get list of configured databases"""
    return multi_db_utils.get_configured_databases()


def get_models_by_database() -> Dict[str, List[str]]:
    """Get models grouped by database"""
    return multi_db_utils.get_models_by_database() 