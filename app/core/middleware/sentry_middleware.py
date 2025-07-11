"""
Sentry middleware for FastAPI integration
"""
import time
import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.sentry import set_user, set_tag, set_context, capture_exception, capture_message


class SentryMiddleware(BaseHTTPMiddleware):
    """Sentry middleware for FastAPI"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and capture Sentry data"""
        start_time = time.time()
        
        # Set request context
        self._set_request_context(request)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Set response context
            self._set_response_context(response, start_time)
            
            return response
            
        except Exception as e:
            # Capture exception in Sentry
            self._capture_exception(e, request)
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
    
    def _set_request_context(self, request: Request):
        """Set request context in Sentry"""
        try:
            # Set request tags
            set_tag("http.method", request.method)
            set_tag("http.url", str(request.url))
            set_tag("http.path", request.url.path)
            set_tag("http.query", str(request.url.query))
            
            # Set request context
            set_context("request", {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": {
                    "ip": request.client.host if request.client else None,
                    "port": request.client.port if request.client else None,
                }
            })
            
            # Set user context if available
            self._set_user_context(request)
            
        except Exception as e:
            self.logger.error(f"Failed to set request context in Sentry: {e}")
    
    def _set_response_context(self, response: Response, start_time: float):
        """Set response context in Sentry"""
        try:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Set response tags
            set_tag("http.status_code", str(response.status_code))
            set_tag("http.duration_ms", str(duration))
            
            # Set response context
            set_context("response", {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "duration_ms": duration
            })
            
        except Exception as e:
            self.logger.error(f"Failed to set response context in Sentry: {e}")
    
    def _set_user_context(self, request: Request):
        """Set user context in Sentry if available"""
        try:
            # Check if user is authenticated
            if hasattr(request.state, "user"):
                user = request.state.user
                if hasattr(user, "id"):
                    set_user(
                        user_id=str(user.id),
                        email=getattr(user, "email", None),
                        username=getattr(user, "username", None)
                    )
            
            # Check for API key authentication
            api_key = request.headers.get("X-API-Key")
            if api_key:
                set_tag("auth.method", "api_key")
                set_tag("auth.api_key", api_key[:8] + "..." if len(api_key) > 8 else api_key)
            
            # Check for JWT authentication
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                set_tag("auth.method", "jwt")
                set_tag("auth.token", authorization[:20] + "..." if len(authorization) > 20 else authorization)
                
        except Exception as e:
            self.logger.error(f"Failed to set user context in Sentry: {e}")
    
    def _capture_exception(self, exception: Exception, request: Request):
        """Capture exception in Sentry with additional context"""
        try:
            # Set additional context for the exception
            set_context("exception", {
                "type": type(exception).__name__,
                "message": str(exception),
                "request_method": request.method,
                "request_url": str(request.url),
            })
            
            # Capture the exception
            capture_exception(
                exception,
                tags={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": "500"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to capture exception in Sentry: {e}")


def add_sentry_middleware(app):
    """Add Sentry middleware to FastAPI app"""
    app.add_middleware(SentryMiddleware)
    return app 