"""
Sentry configuration for error monitoring and performance tracking
"""
import os
import logging
from typing import Optional, Dict, Any
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from app.core.config import get_config


class SentryConfig:
    """Sentry configuration manager"""
    
    def __init__(self):
        self.config = get_config()
        self.dsn = os.getenv("SENTRY_DSN")
        self.environment = self.config.environment
        self.debug = self.config.debug
        
    def is_enabled(self) -> bool:
        """Check if Sentry is enabled"""
        return bool(self.dsn and self.dsn.strip())
    
    def get_traces_sample_rate(self) -> float:
        """Get traces sample rate based on environment"""
        if self.environment == "production":
            return 0.1  # 10% of transactions
        elif self.environment == "staging":
            return 0.5  # 50% of transactions
        else:
            return 1.0  # 100% of transactions in development
    
    def get_profiles_sample_rate(self) -> float:
        """Get profiles sample rate based on environment"""
        if self.environment == "production":
            return 0.05  # 5% of profiles
        elif self.environment == "staging":
            return 0.2  # 20% of profiles
        else:
            return 1.0  # 100% of profiles in development
    
    def get_integrations(self) -> list:
        """Get Sentry integrations"""
        integrations = [
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            HttpxIntegration(),
            AsyncioIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ]
        return integrations
    
    def get_before_send(self):
        """Filter events before sending to Sentry"""
        def before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            # Filter out certain types of errors
            if "exception" in hint:
                exception = hint["exception"]
                # Filter out common non-critical errors
                if isinstance(exception, (KeyboardInterrupt, SystemExit)):
                    return None
                
                # Filter out specific error types if needed
                error_message = str(exception)
                if any(skip in error_message.lower() for skip in [
                    "connection refused",
                    "timeout",
                    "rate limit",
                    "authentication failed"
                ]):
                    return None
            
            # Add custom context
            event.setdefault("tags", {})
            event["tags"]["environment"] = self.environment
            event["tags"]["debug"] = str(self.debug)
            
            return event
        
        return before_send
    
    def get_before_send_transaction(self):
        """Filter transactions before sending to Sentry"""
        def before_send_transaction(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            # Filter out certain transactions
            if "transaction" in event:
                transaction_name = event["transaction"]
                # Filter out health checks and other noise
                if any(skip in transaction_name.lower() for skip in [
                    "/health",
                    "/metrics",
                    "/ping"
                ]):
                    return None
            
            return event
        
        return before_send_transaction
    
    def init_sentry(self):
        """Initialize Sentry with configuration"""
        if not self.is_enabled():
            logging.info("Sentry is not enabled (SENTRY_DSN not set)")
            return
        
        try:
            sentry_init(
                dsn=self.dsn,
                environment=self.environment,
                debug=self.debug,
                traces_sample_rate=self.get_traces_sample_rate(),
                profiles_sample_rate=self.get_profiles_sample_rate(),
                integrations=self.get_integrations(),
                before_send=self.get_before_send(),
                before_send_transaction=self.get_before_send_transaction(),
                # Additional configuration
                send_default_pii=False,  # Don't send PII by default
                auto_enabling_integrations=True,
                # Performance monitoring
                enable_tracing=True,
                # Session tracking
                auto_session_tracking=True,
                # Release tracking
                release=os.getenv("SENTRY_RELEASE", "2.0.0"),
                # Server name
                server_name=os.getenv("SENTRY_SERVER_NAME", "ocr-identity-api"),
            )
            logging.info(f"Sentry initialized successfully for environment: {self.environment}")
            
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {e}")
    
    def capture_exception(self, exception: Exception, **kwargs):
        """Capture an exception with additional context"""
        if not self.is_enabled():
            return
        
        try:
            from sentry_sdk import capture_exception as sentry_capture_exception
            sentry_capture_exception(exception, **kwargs)
        except Exception as e:
            logging.error(f"Failed to capture exception in Sentry: {e}")
    
    def capture_message(self, message: str, level: str = "info", **kwargs):
        """Capture a message with specified level"""
        if not self.is_enabled():
            return
        
        try:
            from sentry_sdk import capture_message as sentry_capture_message
            sentry_capture_message(message, level=level, **kwargs)
        except Exception as e:
            logging.error(f"Failed to capture message in Sentry: {e}")
    
    def set_user(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """Set user context for Sentry"""
        if not self.is_enabled():
            return
        
        try:
            from sentry_sdk import set_user as sentry_set_user
            sentry_set_user({
                "id": user_id,
                "email": email,
                "username": username
            })
        except Exception as e:
            logging.error(f"Failed to set user in Sentry: {e}")
    
    def set_tag(self, key: str, value: str):
        """Set a tag for Sentry"""
        if not self.is_enabled():
            return
        
        try:
            from sentry_sdk import set_tag as sentry_set_tag
            sentry_set_tag(key, value)
        except Exception as e:
            logging.error(f"Failed to set tag in Sentry: {e}")
    
    def set_context(self, name: str, data: Dict[str, Any]):
        """Set context data for Sentry"""
        if not self.is_enabled():
            return
        
        try:
            from sentry_sdk import set_context as sentry_set_context
            sentry_set_context(name, data)
        except Exception as e:
            logging.error(f"Failed to set context in Sentry: {e}")


# Global Sentry configuration instance
sentry_config = SentryConfig()


def init_sentry():
    """Initialize Sentry"""
    sentry_config.init_sentry()


def capture_exception(exception: Exception, **kwargs):
    """Capture an exception in Sentry"""
    sentry_config.capture_exception(exception, **kwargs)


def capture_message(message: str, level: str = "info", **kwargs):
    """Capture a message in Sentry"""
    sentry_config.capture_message(message, level, **kwargs)


def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None):
    """Set user context in Sentry"""
    sentry_config.set_user(user_id, email, username)


def set_tag(key: str, value: str):
    """Set a tag in Sentry"""
    sentry_config.set_tag(key, value)


def set_context(name: str, data: Dict[str, Any]):
    """Set context data in Sentry"""
    sentry_config.set_context(name, data) 