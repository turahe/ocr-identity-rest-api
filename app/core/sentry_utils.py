"""
Sentry utilities for common operations
"""
import functools
import time
import logging
from typing import Any, Callable, Dict, Optional
from app.core.sentry import (
    capture_exception, capture_message, set_tag, 
    set_context, set_user, sentry_config
)


def sentry_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance and errors in Sentry"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not sentry_config.is_enabled():
            return func(*args, **kwargs)
        
        start_time = time.time()
        
        try:
            # Set function context
            set_context("function", {
                "name": func.__name__,
                "module": func.__module__,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            })
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Record success
            duration = (time.time() - start_time) * 1000
            set_tag("function.duration_ms", str(duration))
            set_tag("function.status", "success")
            
            return result
            
        except Exception as e:
            # Record error
            duration = (time.time() - start_time) * 1000
            set_tag("function.duration_ms", str(duration))
            set_tag("function.status", "error")
            set_tag("function.error_type", type(e).__name__)
            
            # Capture exception
            capture_exception(e, tags={
                "function": func.__name__,
                "module": func.__module__
            })
            
            raise
    
    return wrapper


def sentry_monitor_async(func: Callable) -> Callable:
    """Decorator to monitor async function performance and errors in Sentry"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not sentry_config.is_enabled():
            return await func(*args, **kwargs)
        
        start_time = time.time()
        
        try:
            # Set function context
            set_context("function", {
                "name": func.__name__,
                "module": func.__module__,
                "args_count": len(args),
                "kwargs_count": len(kwargs),
                "async": True
            })
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Record success
            duration = (time.time() - start_time) * 1000
            set_tag("function.duration_ms", str(duration))
            set_tag("function.status", "success")
            
            return result
            
        except Exception as e:
            # Record error
            duration = (time.time() - start_time) * 1000
            set_tag("function.duration_ms", str(duration))
            set_tag("function.status", "error")
            set_tag("function.error_type", type(e).__name__)
            
            # Capture exception
            capture_exception(e, tags={
                "function": func.__name__,
                "module": func.__module__,
                "async": True
            })
            
            raise
    
    return wrapper


class SentryTransaction:
    """Context manager for Sentry transactions"""
    
    def __init__(self, name: str, operation: str = "function", **tags):
        self.name = name
        self.operation = operation
        self.tags = tags
        self.start_time = None
        
    def __enter__(self):
        if sentry_config.is_enabled():
            self.start_time = time.time()
            set_tag("transaction.name", self.name)
            set_tag("transaction.operation", self.operation)
            for key, value in self.tags.items():
                set_tag(f"transaction.{key}", str(value))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if sentry_config.is_enabled() and self.start_time:
            duration = (time.time() - self.start_time) * 1000
            set_tag("transaction.duration_ms", str(duration))
            
            if exc_type:
                set_tag("transaction.status", "error")
                set_tag("transaction.error_type", exc_type.__name__)
                capture_exception(exc_val, tags={
                    "transaction": self.name,
                    "operation": self.operation
                })
            else:
                set_tag("transaction.status", "success")


def track_database_operation(operation: str, table: Optional[str] = None, **kwargs):
    """Track database operations in Sentry"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not sentry_config.is_enabled():
                return func(*args, **kwargs)
            
            with SentryTransaction(
                name=f"db.{operation}",
                operation="database",
                table=table or "unknown",
                **kwargs
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def track_external_api_call(service: str, endpoint: str, **kwargs):
    """Track external API calls in Sentry"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not sentry_config.is_enabled():
                return func(*args, **kwargs)
            
            with SentryTransaction(
                name=f"api.{service}.{endpoint}",
                operation="http",
                service=service,
                endpoint=endpoint,
                **kwargs
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def track_file_operation(operation: str, file_type: Optional[str] = None, **kwargs):
    """Track file operations in Sentry"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not sentry_config.is_enabled():
                return func(*args, **kwargs)
            
            with SentryTransaction(
                name=f"file.{operation}",
                operation="file",
                file_type=file_type or "unknown",
                **kwargs
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def capture_user_action(action: str, user_id: str, **context):
    """Capture user actions in Sentry"""
    if not sentry_config.is_enabled():
        return
    
    set_user(user_id)
    set_tag("user_action", action)
    
    if context:
        set_context("user_action", context)
    
    capture_message(
        f"User action: {action}",
        level="info",
        tags={"action": action, "user_id": user_id}
    )


def capture_system_event(event: str, level: str = "info", **context):
    """Capture system events in Sentry"""
    if not sentry_config.is_enabled():
        return
    
    set_tag("system_event", event)
    
    if context:
        set_context("system_event", context)
    
    capture_message(
        f"System event: {event}",
        level=level,
        tags={"event": event}
    )


def capture_performance_metric(metric: str, value: float, unit: str = "ms", **tags):
    """Capture performance metrics in Sentry"""
    if not sentry_config.is_enabled():
        return
    
    set_tag(f"metric.{metric}", str(value))
    set_tag(f"metric.{metric}.unit", unit)
    
    for key, val in tags.items():
        set_tag(f"metric.{metric}.{key}", str(val))
    
    # Log performance metrics
    logging.info(f"Performance metric: {metric}={value}{unit}")


def capture_business_metric(metric: str, value: Any, **context):
    """Capture business metrics in Sentry"""
    if not sentry_config.is_enabled():
        return
    
    set_tag(f"business.{metric}", str(value))
    
    if context:
        set_context(f"business_{metric}", context)
    
    capture_message(
        f"Business metric: {metric}={value}",
        level="info",
        tags={"metric": metric, "value": str(value)}
    )


def capture_error_with_context(error: Exception, context: Optional[Dict[str, Any]] = None, **tags):
    """Capture error with additional context"""
    if not sentry_config.is_enabled():
        return
    
    if context:
        set_context("error_context", context)
    
    for key, value in tags.items():
        set_tag(f"error.{key}", str(value))
    
    capture_exception(error, tags=tags)


def set_request_context(request_id: str, user_id: Optional[str] = None, **context):
    """Set request context in Sentry"""
    if not sentry_config.is_enabled():
        return
    
    set_tag("request.id", request_id)
    
    if user_id:
        set_user(user_id)
    
    if context:
        set_context("request", context)


def monitor_celery_task(task_name: str):
    """Decorator to monitor Celery tasks in Sentry"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not sentry_config.is_enabled():
                return func(*args, **kwargs)
            
            with SentryTransaction(
                name=f"celery.{task_name}",
                operation="celery",
                task=task_name
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator 