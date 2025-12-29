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
