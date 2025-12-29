"""
Monitoring and error tracking
Sentry integration for production error monitoring
"""

import logging
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """
    Initialize Sentry error tracking

    Only initializes if SENTRY_DSN is configured.
    Integrates with FastAPI, SQLAlchemy, and logging.
    """
    if not settings.SENTRY_DSN:
        logger.warning("Sentry DSN not configured - error tracking disabled")
        return

    # Configure Sentry integrations
    integrations = [
        # FastAPI integration
        FastApiIntegration(
            transaction_style="endpoint",  # Group by endpoint name
            failed_request_status_codes=[500, 502, 503, 504],  # Track server errors
        ),
        # SQLAlchemy integration
        SqlalchemyIntegration(),
        # Logging integration
        LoggingIntegration(
            level=logging.INFO,  # Capture info and above
            event_level=logging.ERROR,  # Send errors to Sentry
        ),
    ]

    # Initialize Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=settings.APP_VERSION,
        integrations=integrations,
        # Performance monitoring
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        # Error sampling
        sample_rate=1.0,  # Send all errors
        # Additional options
        attach_stacktrace=True,  # Attach stack traces to messages
        send_default_pii=False,  # Don't send personally identifiable information
        max_breadcrumbs=50,  # Keep last 50 breadcrumbs
        debug=settings.DEBUG,  # Enable debug mode in development
        # Before send hook to filter sensitive data
        before_send=before_send_filter,
    )

    logger.info(f"Sentry initialized for environment: {settings.SENTRY_ENVIRONMENT}")


def before_send_filter(event: dict, hint: dict) -> Optional[dict]:
    """
    Filter sensitive data before sending to Sentry

    Args:
        event: Sentry event dict
        hint: Additional context

    Returns:
        Modified event or None to drop the event
    """
    # Filter sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["Authorization", "Cookie", "X-API-Key"]

        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"

    # Filter sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        query = event["request"]["query_string"]
        if "token" in query.lower() or "password" in query.lower():
            event["request"]["query_string"] = "[Filtered]"

    return event


def capture_exception(error: Exception, context: Optional[dict] = None) -> None:
    """
    Manually capture exception to Sentry

    Args:
        error: Exception to capture
        context: Additional context dict
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: Optional[dict] = None) -> None:
    """
    Manually capture message to Sentry

    Args:
        message: Message to capture
        level: Log level (debug, info, warning, error, fatal)
        context: Additional context dict
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(
    user_id: str, email: Optional[str] = None, username: Optional[str] = None
) -> None:
    """
    Set user context for Sentry events

    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    sentry_sdk.set_user({"id": user_id, "email": email, "username": username})


def clear_user_context() -> None:
    """Clear user context"""
    sentry_sdk.set_user(None)
