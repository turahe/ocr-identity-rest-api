"""
Celery configuration for background task processing
"""
import os
from celery import Celery
from app.core.config import get_redis_config, get_config


def create_celery_app():
    """Create and configure Celery app"""
    config = get_config()
    redis_config = get_redis_config()
    
    # Create Celery app
    celery_app = Celery(
        "ocr_identity_api",
        broker=redis_config.redis_url,
        backend=redis_config.redis_url,
        include=[
            "app.tasks.ocr_tasks",
            "app.tasks.media_tasks"
        ]
    )
    
    # Configure Celery
    celery_app.conf.update(
        # Task settings
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        
        # Task routing
        task_routes={
            "app.tasks.ocr_tasks.*": {"queue": "ocr"},
            "app.tasks.media_tasks.*": {"queue": "media"},
        },
        
        # Worker settings
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        
        # Result settings
        result_expires=3600,  # 1 hour
        result_persistent=True,
        
        # Beat settings (for periodic tasks)
        beat_schedule={
            # Add periodic tasks here if needed
        },
        
        # Task execution settings
        task_always_eager=False,  # Set to True for testing
        task_eager_propagates=True,
        
        # Logging
        worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
    )
    
    # Set environment-specific settings
    if config.environment == "development":
        celery_app.conf.update(
            task_always_eager=True,  # Execute tasks synchronously in development
            worker_log_level="DEBUG",
        )
    elif config.environment == "production":
        celery_app.conf.update(
            worker_log_level="INFO",
            worker_max_memory_per_child=200000,  # 200MB
        )
    
    return celery_app


# Create global Celery app instance
celery_app = create_celery_app() 