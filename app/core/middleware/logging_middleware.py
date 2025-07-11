"""
Logging middleware for FastAPI
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.logging_config import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("app.api.middleware")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start time
        start_time = time.time()
        
        # Get request details
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        self.logger.info(
            f"Request: {method} {url} - IP: {client_ip} - User-Agent: {user_agent}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            self.logger.info(
                f"Response: {method} {url} - Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = str(id(request))
            
            return response
            
        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log error
            self.logger.error(
                f"Error: {method} {url} - Exception: {str(e)} - "
                f"Time: {process_time:.3f}s"
            )
            raise


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("app.api.request_id")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Add request ID to headers
        request.headers.__dict__["_list"].append(
            (b"x-request-id", request_id.encode())
        )
        
        # Log request ID
        self.logger.debug(f"Request ID: {request_id} for {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to log performance metrics"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("app.api.performance")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        content_length = response.headers.get("content-length", 0)
        
        # Log performance metrics
        self.logger.info(
            f"Performance: {request.method} {request.url} - "
            f"Time: {process_time:.3f}s - Size: {content_length} bytes"
        )
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Content-Length"] = str(content_length)
        
        return response


def add_logging_middleware(app):
    """Add logging middleware to FastAPI app"""
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(LoggingMiddleware) 