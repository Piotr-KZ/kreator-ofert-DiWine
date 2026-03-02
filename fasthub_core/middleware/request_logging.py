"""
Request logging middleware
Logs all HTTP requests with structured data
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from fasthub_core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with structured data

    Logs:
    - Request method, path, query params
    - Response status code, duration
    - Client IP, user agent
    - User ID (if authenticated)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details
        """
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Get user ID from request state (set by auth dependency)
        user_id = getattr(request.state, "user_id", None)

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            error = None
        except Exception as e:
            status_code = 500
            error = str(e)
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Log request
            log_data = {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": client_ip,
                "user_agent": user_agent,
            }

            # Add optional fields
            if query_params:
                log_data["query_params"] = query_params
            if user_id:
                log_data["user_id"] = str(user_id)
            if error:
                log_data["error"] = error

            # Log with appropriate level
            if status_code >= 500:
                logger.error("request_failed %s", log_data)
            elif status_code >= 400:
                logger.warning("request_client_error %s", log_data)
            else:
                logger.info("request_completed %s", log_data)

        return response
