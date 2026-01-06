"""
Redis cache service
Caching layer for performance optimization
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service for performance optimization"""

    def __init__(self):
        self.redis_url = settings.REDIS_URL if hasattr(settings, "REDIS_URL") else None
        self.client: Optional[redis.Redis] = None
        self.enabled = False

    async def connect(self):
        """Connect to Redis"""
        if not self.redis_url:
            logger.warning("Redis URL not configured - caching disabled")
            return

        try:
            self.client = await redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.client.ping()
            self.enabled = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Redis cache disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 300) -> bool:  # 5 minutes default
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            serialized = json.dumps(value, default=str)
            await self.client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

    async def clear(self) -> bool:
        """
        Clear all cache

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            await self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def cache_key(self, *parts: str) -> str:
        """
        Generate cache key from parts

        Args:
            *parts: Key parts

        Returns:
            Cache key string

        Example:
            cache_key("user", "123", "profile") -> "user:123:profile"
        """
        return ":".join(str(part) for part in parts)


# Singleton instance
cache = CacheService()


# Function-based API (for backward compatibility with tests)
async def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in cache with TTL (function-based API)
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds
    
    Returns:
        bool: True if successful
    """
    return await cache.set(key, value, expire=ttl)


async def cache_get(key: str) -> Optional[Any]:
    """
    Get value from cache (function-based API)
    
    Args:
        key: Cache key
    
    Returns:
        Optional[Any]: Cached value or None
    """
    return await cache.get(key)


async def cache_delete(key: str) -> bool:
    """
    Delete key from cache (function-based API)
    
    Args:
        key: Cache key
    
    Returns:
        bool: True if deleted
    """
    return await cache.delete(key)


async def cache_exists(key: str) -> bool:
    """
    Check if key exists in cache (function-based API)
    
    Args:
        key: Cache key
    
    Returns:
        bool: True if exists
    """
    if not cache.enabled or not cache.client:
        return False
    
    try:
        exists = await cache.client.exists(key)
        return exists > 0
    except Exception as e:
        logger.error(f"Cache exists error: {e}")
        return False


async def cache_clear_pattern(pattern: str) -> int:
    """
    Delete all keys matching pattern (function-based API)
    
    Args:
        pattern: Redis pattern
    
    Returns:
        int: Number of keys deleted
    """
    return await cache.delete_pattern(pattern)


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments (function-based API)
    
    Example:
        key = cache_key("user", user_id=123)
    """
    parts = [str(arg) for arg in args]
    
    if kwargs:
        kv_pairs = [f"{k}={v}" for k, v in sorted(kwargs.items())]
        parts.extend(kv_pairs)
    
    return ":".join(parts)
