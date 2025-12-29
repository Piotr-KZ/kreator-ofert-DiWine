"""
Rate limiting middleware
Protects API endpoints from abuse and DDoS attacks
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],  # Default rate limit for all endpoints
    storage_uri=settings.REDIS_URL if settings.REDIS_URL else "memory://",
    strategy="fixed-window",  # or "moving-window" for more accurate limiting
    headers_enabled=True,  # Add rate limit headers to responses
)


# Rate limit configurations for different endpoint types
class RateLimits:
    """Predefined rate limits for different endpoint categories"""

    # Authentication endpoints (more restrictive)
    AUTH_LOGIN = "5/minute"  # 5 login attempts per minute
    AUTH_REGISTER = "3/hour"  # 3 registrations per hour
    AUTH_PASSWORD_RESET = "3/hour"  # 3 password reset requests per hour
    AUTH_MAGIC_LINK = "5/hour"  # 5 magic link requests per hour

    # API token endpoints
    API_TOKEN_CREATE = "10/hour"  # 10 token creations per hour
    API_TOKEN_LIST = "60/minute"  # 60 requests per minute

    # Public endpoints (moderate)
    PUBLIC_READ = "100/minute"  # 100 read requests per minute
    PUBLIC_WRITE = "30/minute"  # 30 write requests per minute

    # Protected endpoints (less restrictive for authenticated users)
    PROTECTED_READ = "200/minute"  # 200 read requests per minute
    PROTECTED_WRITE = "60/minute"  # 60 write requests per minute

    # Admin endpoints
    ADMIN = "100/minute"  # 100 admin requests per minute

    # Webhook endpoints (very permissive)
    WEBHOOK = "1000/hour"  # 1000 webhook calls per hour


def get_rate_limit_exceeded_handler():
    """
    Custom rate limit exceeded handler
    Returns consistent error response format
    """
    return _rate_limit_exceeded_handler
