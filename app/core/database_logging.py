"""
Database logging service for tracking database operations
"""
import time
import logging
from typing import Any, Dict, Optional
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger, log_performance


class DatabaseLogger:
    """Database operation logger"""
    
    def __init__(self):
        self.logger = get_logger("app.database")
        self.setup_sqlalchemy_logging()
    
    def setup_sqlalchemy_logging(self):
        """Setup SQLAlchemy event listeners for logging"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            self.logger.debug(f"Executing SQL: {statement[:100]}...")
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            self.logger.info(f"SQL executed in {total:.3f}s: {statement[:100]}...")
        
        @event.listens_for(Engine, "handle_error")
        def handle_error(exception_context):
            self.logger.error(f"Database error: {exception_context.original}")
    
    def log_connection(self, database_name: str, operation: str):
        """Log database connection operations"""
        self.logger.info(f"Database connection: {operation} for {database_name}")
    
    def log_transaction(self, operation: str, table: Optional[str] = None):
        """Log database transaction operations"""
        if table:
            self.logger.info(f"Database transaction: {operation} on {table}")
        else:
            self.logger.info(f"Database transaction: {operation}")
    
    def log_query(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """Log database query"""
        if parameters:
            self.logger.debug(f"Query: {query} with parameters: {parameters}")
        else:
            self.logger.debug(f"Query: {query}")
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """Log database error"""
        if context:
            self.logger.error(f"Database error in {context}: {error}")
        else:
            self.logger.error(f"Database error: {error}")


# Global database logger instance
db_logger = DatabaseLogger()


def log_db_operation(operation: str):
    """Decorator to log database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            db_logger.log_transaction(operation)
            try:
                result = func(*args, **kwargs)
                db_logger.log_transaction(f"{operation} completed successfully")
                return result
            except Exception as e:
                db_logger.log_error(e, operation)
                raise
        return wrapper
    return decorator


def log_db_query(func):
    """Decorator to log database queries"""
    def wrapper(*args, **kwargs):
        # Extract query from function name or args
        query_name = func.__name__
        db_logger.log_query(f"Executing {query_name}")
        
        try:
            result = func(*args, **kwargs)
            db_logger.log_query(f"{query_name} completed successfully")
            return result
        except Exception as e:
            db_logger.log_error(e, query_name)
            raise
    return wrapper


class DatabaseSessionLogger:
    """Logger for database session operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.logger = get_logger("app.database.session")
    
    def log_add(self, instance: Any):
        """Log adding an instance to session"""
        self.logger.info(f"Adding {instance.__class__.__name__} to session")
    
    def log_commit(self):
        """Log session commit"""
        self.logger.info("Committing database session")
    
    def log_rollback(self):
        """Log session rollback"""
        self.logger.warning("Rolling back database session")
    
    def log_close(self):
        """Log session close"""
        self.logger.debug("Closing database session")


def create_session_logger(session: Session) -> DatabaseSessionLogger:
    """Create a session logger for the given session"""
    return DatabaseSessionLogger(session) 