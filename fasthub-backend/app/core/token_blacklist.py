"""
Token Blacklist Service

Manages JWT token blacklist using Redis (SYNC version).
When a user logs out, their token is added to the blacklist
and cannot be used for authentication until it expires.
"""

from datetime import datetime, timezone
from typing import Optional
import logging
from redis import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class TokenBlacklist:
    """Token blacklist manager using Redis (sync)"""

    _redis_client: Optional[Redis] = None

    @classmethod
    def get_redis(cls) -> Optional[Redis]:
        """
        Get sync Redis client (cached singleton)

        Returns:
            Redis client or None if connection fails
        """
        if cls._redis_client is None:
            try:
                cls._redis_client = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                cls._redis_client.ping()  # Test connection
                logger.info("✅ Redis connected (sync)")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                cls._redis_client = None

        return cls._redis_client

    @classmethod
    def add_token(cls, token: str, expires_at: datetime) -> bool:
        """
        Add token to blacklist (SYNC)

        Args:
            token: JWT token to blacklist
            expires_at: Token expiration datetime

        Returns:
            True if added successfully, False otherwise
        """
        redis = cls.get_redis()
        if not redis:
            logger.warning("Redis unavailable - token NOT blacklisted")
            return False

        try:
            key = f"blacklist:{token}"
            # Use timezone-aware datetime to calculate correct TTL
            # datetime.utcnow() returns local time in EST timezone, not UTC!
            now = datetime.now(timezone.utc).replace(tzinfo=None)  # Naive UTC datetime
            ttl = int((expires_at - now).total_seconds())

            if ttl <= 0:
                logger.warning(f"Token already expired (TTL={ttl})")
                return False

            redis.setex(key, ttl, "1")  # SYNC - no await!
            logger.info(f"✅ Token blacklisted: {key[:50]}... (TTL={ttl}s)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to blacklist token: {e}")
            return False

    @classmethod
    def is_blacklisted(cls, token: str) -> bool:
        """
        Check if token is blacklisted (SYNC)

        Args:
            token: JWT token to check

        Returns:
            True if blacklisted, False otherwise
        """
        redis = cls.get_redis()
        if not redis:
            return False  # Fail open - allow access if Redis unavailable

        try:
            key = f"blacklist:{token}"
            exists = redis.exists(key)  # SYNC - no await!

            if exists:
                logger.info(f"⛔ Token is blacklisted: {key[:50]}...")

            return bool(exists)

        except Exception as e:
            logger.error(f"❌ Blacklist check failed: {e}")
            return False  # Fail open

    @classmethod
    def remove_token(cls, token: str) -> bool:
        """
        Remove token from blacklist (for testing/admin purposes)

        Args:
            token: JWT token to remove

        Returns:
            True if removed successfully, False otherwise
        """
        redis = cls.get_redis()
        if not redis:
            return False

        try:
            key = f"blacklist:{token}"
            deleted = redis.delete(key)
            logger.info(f"Token removed from blacklist: {key[:50]}...")
            return bool(deleted)

        except Exception as e:
            logger.error(f"Failed to remove token from blacklist: {e}")
            return False

    @classmethod
    def get_stats(cls) -> dict:
        """
        Get blacklist statistics

        Returns:
            Dictionary with stats (count, sample keys)
        """
        redis = cls.get_redis()
        if not redis:
            return {"error": "Redis unavailable"}

        try:
            keys = redis.keys("blacklist:*")
            return {
                "total_blacklisted": len(keys),
                "sample_keys": [k[:60] + "..." for k in keys[:5]],
            }

        except Exception as e:
            logger.error(f"Failed to get blacklist stats: {e}")
            return {"error": str(e)}

    @classmethod
    def clear_all(cls) -> bool:
        """
        Clear all blacklisted tokens (for testing/admin purposes)

        Returns:
            True if cleared successfully, False otherwise
        """
        redis = cls.get_redis()
        if not redis:
            return False

        try:
            keys = redis.keys("blacklist:*")
            if keys:
                deleted = redis.delete(*keys)
                logger.info(f"Cleared {deleted} blacklisted tokens")
                return True
            return True

        except Exception as e:
            logger.error(f"Failed to clear blacklist: {e}")
            return False


# ============================================================================
# WRAPPER FUNCTIONS FOR TESTS
# ============================================================================

def blacklist_token(token: str, expires_at: datetime) -> bool:
    """
    Wrapper function for tests - adds token to blacklist
    
    Args:
        token: JWT token to blacklist
        expires_at: Token expiration datetime
        
    Returns:
        True if added successfully, False otherwise
    """
    return TokenBlacklist.add_token(token, expires_at)


def is_token_blacklisted(token: str) -> bool:
    """
    Wrapper function for tests - checks if token is blacklisted
    
    Args:
        token: JWT token to check
        
    Returns:
        True if blacklisted, False otherwise
    """
    return TokenBlacklist.is_blacklisted(token)


def cleanup_expired_tokens() -> bool:
    """
    Wrapper function for tests - cleanup expired tokens
    
    Note: Redis automatically expires keys with TTL, so this is a no-op
    
    Returns:
        True always (Redis handles expiration automatically)
    """
    # Redis automatically removes expired keys, no manual cleanup needed
    return True


def get_redis():
    """
    Wrapper function for tests - get Redis client
    
    Returns:
        Redis client or None
    """
    return TokenBlacklist.get_redis()
