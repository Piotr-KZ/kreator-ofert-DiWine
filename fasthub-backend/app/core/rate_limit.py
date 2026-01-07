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


# ============================================================================
# WRAPPER FUNCTIONS FOR TESTS
# ============================================================================

async def get_rate_limit_status(identifier: str) -> dict:
    """
    Get rate limit status for identifier (wrapper for tests)
    
    Args:
        identifier: Rate limit identifier (e.g., "user:123" or "ip:1.2.3.4")
        
    Returns:
        Dictionary with rate limit status:
        - requests_made: Number of requests made
        - limit: Maximum requests allowed
        - remaining: Remaining requests
        - reset_in_seconds: Seconds until reset
    """
    # This is a mock implementation for tests
    # Real implementation would query Redis
    from app.core.cache import get_redis
    
    redis = get_redis()
    if not redis:
        return {
            "requests_made": 0,
            "limit": 100,
            "remaining": 100,
            "reset_in_seconds": 3600
        }
    
    try:
        key = f"rate_limit:{identifier}"
        count = await redis.get(key)
        ttl = await redis.ttl(key)
        
        requests_made = int(count) if count else 0
        limit = 100  # Default limit
        
        return {
            "requests_made": requests_made,
            "limit": limit,
            "remaining": max(0, limit - requests_made),
            "reset_in_seconds": ttl if ttl > 0 else 3600
        }
    except Exception:
        return {
            "requests_made": 0,
            "limit": 100,
            "remaining": 100,
            "reset_in_seconds": 3600
        }


async def reset_rate_limit(identifier: str) -> bool:
    """
    Reset rate limit for identifier (wrapper for tests)
    
    Args:
        identifier: Rate limit identifier (e.g., "user:123" or "ip:1.2.3.4")
        
    Returns:
        True if reset successfully, False otherwise
    """
    from app.core.cache import get_redis
    
    redis = get_redis()
    if not redis:
        return False
    
    try:
        key = f"rate_limit:{identifier}"
        await redis.delete(key)
        return True
    except Exception:
        return False


def get_redis():
    """
    Get Redis client (wrapper for tests)
    
    Returns:
        Redis client or None
    """
    from app.core.cache import get_redis as cache_get_redis
    return cache_get_redis()
