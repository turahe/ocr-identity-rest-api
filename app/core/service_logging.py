"""
Service logging for external services (S3, Redis, Email, etc.)
"""
import time
import logging
from typing import Any, Dict, Optional
from functools import wraps
from app.core.logging_config import get_logger, log_performance


class ServiceLogger:
    """Logger for external service operations"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger(f"app.services.{service_name}")
    
    def log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """Log service operation"""
        if details:
            self.logger.info(f"{self.service_name} {operation}: {details}")
        else:
            self.logger.info(f"{self.service_name} {operation}")
    
    def log_error(self, operation: str, error: Exception, details: Optional[Dict[str, Any]] = None):
        """Log service error"""
        if details:
            self.logger.error(f"{self.service_name} {operation} error: {error} - {details}")
        else:
            self.logger.error(f"{self.service_name} {operation} error: {error}")
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log service performance"""
        if details:
            self.logger.info(f"{self.service_name} {operation} completed in {duration:.3f}s: {details}")
        else:
            self.logger.info(f"{self.service_name} {operation} completed in {duration:.3f}s")


class S3Logger(ServiceLogger):
    """Logger for S3 operations"""
    
    def __init__(self):
        super().__init__("s3")
    
    def log_upload(self, file_name: str, file_size: int, bucket: str):
        """Log S3 upload operation"""
        self.log_operation("upload", {
            "file_name": file_name,
            "file_size": file_size,
            "bucket": bucket
        })
    
    def log_download(self, file_name: str, bucket: str):
        """Log S3 download operation"""
        self.log_operation("download", {
            "file_name": file_name,
            "bucket": bucket
        })
    
    def log_delete(self, file_name: str, bucket: str):
        """Log S3 delete operation"""
        self.log_operation("delete", {
            "file_name": file_name,
            "bucket": bucket
        })


class RedisLogger(ServiceLogger):
    """Logger for Redis operations"""
    
    def __init__(self):
        super().__init__("redis")
    
    def log_get(self, key: str):
        """Log Redis get operation"""
        self.log_operation("get", {"key": key})
    
    def log_set(self, key: str, ttl: Optional[int] = None):
        """Log Redis set operation"""
        details = {"key": key}
        if ttl:
            details["ttl"] = str(ttl)
        self.log_operation("set", details)
    
    def log_delete(self, key: str):
        """Log Redis delete operation"""
        self.log_operation("delete", {"key": key})


class EmailLogger(ServiceLogger):
    """Logger for email operations"""
    
    def __init__(self):
        super().__init__("email")
    
    def log_send(self, to_email: str, subject: str, has_attachments: bool = False):
        """Log email send operation"""
        self.log_operation("send", {
            "to_email": to_email,
            "subject": subject,
            "has_attachments": has_attachments
        })


class CeleryLogger(ServiceLogger):
    """Logger for Celery operations"""
    
    def __init__(self):
        super().__init__("celery")
    
    def log_task_start(self, task_name: str, task_id: str):
        """Log task start"""
        self.log_operation("task_start", {
            "task_name": task_name,
            "task_id": task_id
        })
    
    def log_task_complete(self, task_name: str, task_id: str, duration: float):
        """Log task completion"""
        self.log_performance("task_complete", duration, {
            "task_name": task_name,
            "task_id": task_id
        })
    
    def log_task_error(self, task_name: str, task_id: str, error: Exception):
        """Log task error"""
        self.log_error("task_error", error, {
            "task_name": task_name,
            "task_id": task_id
        })


# Global service loggers
s3_logger = S3Logger()
redis_logger = RedisLogger()
email_logger = EmailLogger()
celery_logger = CeleryLogger()


def log_service_operation(service_name: str, operation: str):
    """Decorator to log service operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(f"app.services.{service_name}")
            start_time = time.time()
            
            logger.info(f"Starting {service_name} {operation}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{service_name} {operation} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{service_name} {operation} failed after {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator


def log_s3_operation(operation: str):
    """Decorator to log S3 operations"""
    return log_service_operation("s3", operation)


def log_redis_operation(operation: str):
    """Decorator to log Redis operations"""
    return log_service_operation("redis", operation)


def log_email_operation(operation: str):
    """Decorator to log email operations"""
    return log_service_operation("email", operation)


def log_celery_operation(operation: str):
    """Decorator to log Celery operations"""
    return log_service_operation("celery", operation) 