"""
Logging configuration for OCR Identity REST API
"""
import os
import sys
import logging
import logging.config
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import get_config


class LoggingConfig:
    """Logging configuration manager"""
    
    def __init__(self):
        self.config = get_config()
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary"""
        
        # Base configuration
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "simple": {
                    "format": "%(levelname)s - %(message)s"
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(timestamp)s %(level)s %(name)s %(message)s"
                },
                "colored": {
                    "()": "colorlog.ColoredFormatter",
                    "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "log_colors": {
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "red,bg_white"
                    }
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG" if self.config.debug else "INFO",
                    "formatter": "colored" if self.config.debug else "simple",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "app.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "error.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "access_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "access.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console", "file", "error_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "app": {
                    "handlers": ["console", "file", "error_file"],
                    "level": "DEBUG" if self.config.debug else "INFO",
                    "propagate": False
                },
                "app.api": {
                    "handlers": ["console", "access_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "app.core": {
                    "handlers": ["console", "file", "error_file"],
                    "level": "DEBUG" if self.config.debug else "INFO",
                    "propagate": False
                },
                "app.services": {
                    "handlers": ["console", "file", "error_file"],
                    "level": "DEBUG" if self.config.debug else "INFO",
                    "propagate": False
                },
                "app.tasks": {
                    "handlers": ["console", "file", "error_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "app.models": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "uvicorn": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "uvicorn.access": {
                    "handlers": ["access_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "fastapi": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "sqlalchemy": {
                    "handlers": ["console", "file"],
                    "level": "WARNING",
                    "propagate": False
                },
                "celery": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "boto3": {
                    "handlers": ["console", "file"],
                    "level": "WARNING",
                    "propagate": False
                },
                "botocore": {
                    "handlers": ["console", "file"],
                    "level": "WARNING",
                    "propagate": False
                },
                "spacy": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
        
        # Add JSON logging for production
        if self.config.environment == "production":
            config["handlers"]["json_file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": str(self.log_dir / "app.json"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
            config["loggers"]["app"]["handlers"].append("json_file")
        
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        try:
            config = self.get_logging_config()
            logging.config.dictConfig(config)
            
            # Get root logger
            logger = logging.getLogger()
            logger.info(f"Logging configured for environment: {self.config.environment}")
            logger.info(f"Log directory: {self.log_dir.absolute()}")
            
        except Exception as e:
            # Fallback to basic logging if configuration fails
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler(str(self.log_dir / "fallback.log"))
                ]
            )
            logging.error(f"Failed to setup logging configuration: {e}")


# Global logging config instance
logging_config = LoggingConfig()


def setup_logging():
    """Setup logging configuration"""
    logging_config.setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised exception: {e}")
            raise
    return wrapper


def log_performance(operation: str):
    """Decorator to log performance metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            logger = logging.getLogger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Performance: {operation} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Performance: {operation} failed after {execution_time:.3f}s: {e}")
                raise
        return wrapper
    return decorator


def log_database_operation(operation: str):
    """Decorator to log database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("app.models")
            logger.info(f"Database operation: {operation}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Database operation: {operation} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Database operation: {operation} failed: {e}")
                raise
        return wrapper
    return decorator


def log_api_request(method: str, path: str):
    """Decorator to log API requests"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("app.api")
            logger.info(f"API Request: {method} {path}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"API Response: {method} {path} - Success")
                return result
            except Exception as e:
                logger.error(f"API Response: {method} {path} - Error: {e}")
                raise
        return wrapper
    return decorator 