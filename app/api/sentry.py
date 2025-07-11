"""
Sentry testing and monitoring API endpoints
"""
from typing import Dict, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user_or_apikey
from app.models.user import User
from app.core.sentry import (
    capture_exception, capture_message, set_tag, 
    set_context, set_user, sentry_config
)
from app.core.sentry_utils import (
    SentryTransaction, capture_user_action, 
    capture_system_event, capture_performance_metric,
    capture_business_metric, capture_error_with_context
)

router = APIRouter(prefix="/sentry", tags=["sentry"])


@router.get("/test", summary="Test Sentry configuration")
async def test_sentry(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Test Sentry configuration and basic functionality.
    
    Returns:
        Dictionary with Sentry status and test results
    """
    if not sentry_config.is_enabled():
        return {
            "status": "disabled",
            "message": "Sentry is not enabled (SENTRY_DSN not set)",
            "environment": sentry_config.environment
        }
    
    # Test basic Sentry functionality
    try:
        # Set user context
        if isinstance(current_user, User):
            set_user(str(current_user.id), str(current_user.email), str(current_user.username))
        
        # Set some tags
        set_tag("test", "sentry_api")
        set_tag("endpoint", "/sentry/test")
        
        # Set context
        set_context("test_context", {
            "test_type": "configuration",
            "user_type": "authenticated" if isinstance(current_user, User) else "api_key"
        })
        
        # Capture a test message
        capture_message("Sentry test message from API", level="info")
        
        return {
            "status": "enabled",
            "environment": sentry_config.environment,
            "debug": sentry_config.debug,
            "message": "Sentry is working correctly",
            "user_context": "set" if isinstance(current_user, User) else "api_key"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Sentry test failed: {str(e)}",
            "environment": sentry_config.environment
        }


@router.post("/test/error", summary="Test error capture")
async def test_error_capture(
    error_type: str = "ValueError",
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Test error capture in Sentry.
    
    Args:
        error_type: Type of error to generate (ValueError, RuntimeError, etc.)
        
    Returns:
        Dictionary with test results
    """
    if not sentry_config.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sentry is not enabled"
        )
    
    try:
        # Set user context
        if isinstance(current_user, User):
            set_user(str(current_user.id), str(current_user.email), str(current_user.username))
        
        # Generate the specified error
        if error_type == "ValueError":
            raise ValueError("Test ValueError from Sentry API")
        elif error_type == "RuntimeError":
            raise RuntimeError("Test RuntimeError from Sentry API")
        elif error_type == "TypeError":
            raise TypeError("Test TypeError from Sentry API")
        elif error_type == "KeyError":
            raise KeyError("Test KeyError from Sentry API")
        else:
            raise Exception(f"Test {error_type} from Sentry API")
            
    except Exception as e:
        # Capture the error with context
        capture_error_with_context(
            e,
            context={
                "test_type": "error_capture",
                "error_type": error_type,
                "endpoint": "/sentry/test/error"
            },
            test="error_capture",
            error_type=error_type
        )
        
        return {
            "status": "error_captured",
            "error_type": error_type,
            "message": f"Error '{error_type}' captured in Sentry",
            "error": str(e)
        }


@router.post("/test/performance", summary="Test performance monitoring")
async def test_performance_monitoring(
    duration_ms: int = 1000,
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Test performance monitoring in Sentry.
    
    Args:
        duration_ms: Duration to simulate in milliseconds
        
    Returns:
        Dictionary with performance test results
    """
    if not sentry_config.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sentry is not enabled"
        )
    
    import time
    
    with SentryTransaction(
        name="test.performance",
        operation="test",
        duration_ms=duration_ms
    ):
        # Simulate work
        time.sleep(duration_ms / 1000)
        
        # Capture performance metric
        capture_performance_metric(
            "test_duration",
            duration_ms,
            unit="ms",
            test_type="performance"
        )
        
        return {
            "status": "performance_monitored",
            "duration_ms": duration_ms,
            "message": f"Performance test completed in {duration_ms}ms"
        }


@router.post("/test/user-action", summary="Test user action capture")
async def test_user_action_capture(
    action: str = "test_action",
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Test user action capture in Sentry.
    
    Args:
        action: Action name to capture
        
    Returns:
        Dictionary with test results
    """
    if not sentry_config.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sentry is not enabled"
        )
    
    if isinstance(current_user, User):
        user_id = str(current_user.id)
        capture_user_action(
            action,
            user_id,
            endpoint="/sentry/test/user-action",
            test_type="user_action"
        )
        
        return {
            "status": "user_action_captured",
            "action": action,
            "user_id": user_id,
            "message": f"User action '{action}' captured in Sentry"
        }
    else:
        return {
            "status": "skipped",
            "message": "User action capture skipped (API key authentication)"
        }


@router.post("/test/system-event", summary="Test system event capture")
async def test_system_event_capture(
    event: str = "test_system_event",
    level: str = "info",
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Test system event capture in Sentry.
    
    Args:
        event: Event name to capture
        level: Log level (info, warning, error)
        
    Returns:
        Dictionary with test results
    """
    if not sentry_config.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sentry is not enabled"
        )
    
    capture_system_event(
        event,
        level=level,
        endpoint="/sentry/test/system-event",
        test_type="system_event"
    )
    
    return {
        "status": "system_event_captured",
        "event": event,
        "level": level,
        "message": f"System event '{event}' captured in Sentry"
    }


@router.post("/test/business-metric", summary="Test business metric capture")
async def test_business_metric_capture(
    metric: str = "test_metric",
    value: Any = 42,
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Test business metric capture in Sentry.
    
    Args:
        metric: Metric name
        value: Metric value
        
    Returns:
        Dictionary with test results
    """
    if not sentry_config.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sentry is not enabled"
        )
    
    capture_business_metric(
        metric,
        value,
        endpoint="/sentry/test/business-metric",
        test_type="business_metric"
    )
    
    return {
        "status": "business_metric_captured",
        "metric": metric,
        "value": value,
        "message": f"Business metric '{metric}={value}' captured in Sentry"
    }


@router.get("/status", summary="Get Sentry status")
async def get_sentry_status(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Get Sentry configuration status.
    
    Returns:
        Dictionary with Sentry status information
    """
    return {
        "enabled": sentry_config.is_enabled(),
        "environment": sentry_config.environment,
        "debug": sentry_config.debug,
        "dsn_configured": bool(sentry_config.dsn),
        "traces_sample_rate": sentry_config.get_traces_sample_rate(),
        "profiles_sample_rate": sentry_config.get_profiles_sample_rate(),
        "integrations_count": len(sentry_config.get_integrations())
    } 