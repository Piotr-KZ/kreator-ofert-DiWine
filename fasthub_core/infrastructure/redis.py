"""
FastHub Core — Redis Service.

Connection pool singleton + cache + pub/sub + health check.
Fundament dla Event Bus, cache, queues.

Konfiguracja z fasthub_core/config.py:
  REDIS_URL, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_KEY_PREFIX
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("fasthub.redis")

# === SINGLETON CONNECTION POOL ===

_redis_client = None
_redis_url: Optional[str] = None


def _get_config():
    """Lazy load config to avoid import-time errors."""
    try:
        from fasthub_core.config import get_settings
        return get_settings()
    except Exception:
        return None


def _get_prefix() -> str:
    """Get Redis key prefix from config."""
    config = _get_config()
    if config:
        return getattr(config, "REDIS_KEY_PREFIX", "fasthub")
    return "fasthub"


async def get_redis():
    """
    Get Redis client (singleton).
    Creates connection pool on first call using settings from config.
    Returns None if Redis is unavailable.
    """
    global _redis_client, _redis_url

    if _redis_client is not None:
        return _redis_client

    try:
        import redis.asyncio as aioredis

        config = _get_config()
        if config and getattr(config, "REDIS_URL", None):
            url = config.REDIS_URL
        elif config:
            host = getattr(config, "REDIS_HOST", "localhost")
            port = getattr(config, "REDIS_PORT", 6379)
            db = getattr(config, "REDIS_DB", 0)
            url = f"redis://{host}:{port}/{db}"
        else:
            url = "redis://localhost:6379/0"

        _redis_url = url
        _redis_client = aioredis.from_url(
            url,
            decode_responses=True,
            max_connections=20,
        )
        logger.info(f"Redis connected: {url.split('@')[-1]}")
        return _redis_client

    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        return None


async def close_redis():
    """Close Redis connection pool."""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.close()
        except Exception:
            pass
        _redis_client = None
        logger.info("Redis connection closed")


async def redis_health_check() -> Dict[str, Any]:
    """
    Check Redis health. Returns dict with status and info.
    Always returns a dict — never raises.
    """
    try:
        client = await get_redis()
        if client is None:
            return {"status": "unavailable", "message": "Redis not configured or unreachable"}

        pong = await client.ping()
        info = await client.info("server")
        return {
            "status": "healthy" if pong else "unhealthy",
            "redis_version": info.get("redis_version", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# === PUB/SUB ===

async def publish_event(event_type: str, payload: Dict[str, Any]) -> int:
    """
    Publish event to Redis Pub/Sub channel.
    Channel name: {prefix}:events:{event_type}
    Returns number of subscribers that received the message.
    """
    try:
        client = await get_redis()
        if client is None:
            return 0

        prefix = _get_prefix()
        channel = f"{prefix}:events:{event_type}"
        message = json.dumps({
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        })
        result = await client.publish(channel, message)
        return result
    except Exception as e:
        logger.error(f"Failed to publish event {event_type}: {e}")
        return 0


async def subscribe_events(*event_types: str):
    """
    Subscribe to Redis Pub/Sub channels for given event types.
    Returns pubsub object for listening.
    Usage:
        pubsub = await subscribe_events("user.*", "billing.*")
        async for message in pubsub.listen():
            ...
    """
    try:
        client = await get_redis()
        if client is None:
            return None

        prefix = _get_prefix()
        pubsub = client.pubsub()
        patterns = [f"{prefix}:events:{et}" for et in event_types]
        await pubsub.psubscribe(*patterns)
        return pubsub
    except Exception as e:
        logger.error(f"Failed to subscribe to events: {e}")
        return None


async def subscribe_all_events():
    """Subscribe to ALL events (wildcard)."""
    prefix = _get_prefix()
    return await subscribe_events("*")


# === CACHE ===

async def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set cache value with TTL (seconds).
    Key is prefixed automatically: {prefix}:cache:{key}
    Value is JSON-serialized.
    """
    try:
        client = await get_redis()
        if client is None:
            return False

        prefix = _get_prefix()
        full_key = f"{prefix}:cache:{key}"
        serialized = json.dumps(value, default=str)
        await client.setex(full_key, ttl, serialized)
        return True
    except Exception as e:
        logger.error(f"Cache set failed for {key}: {e}")
        return False


async def get_cache(key: str) -> Optional[Any]:
    """
    Get cached value by key.
    Returns deserialized value or None if not found/expired.
    """
    try:
        client = await get_redis()
        if client is None:
            return None

        prefix = _get_prefix()
        full_key = f"{prefix}:cache:{key}"
        data = await client.get(full_key)
        if data is None:
            return None
        return json.loads(data)
    except Exception as e:
        logger.error(f"Cache get failed for {key}: {e}")
        return None


async def delete_cache(key: str) -> bool:
    """Delete cached value by key."""
    try:
        client = await get_redis()
        if client is None:
            return False

        prefix = _get_prefix()
        full_key = f"{prefix}:cache:{key}"
        result = await client.delete(full_key)
        return result > 0
    except Exception as e:
        logger.error(f"Cache delete failed for {key}: {e}")
        return False


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    try:
        client = await get_redis()
        if client is None:
            return False

        prefix = _get_prefix()
        full_key = f"{prefix}:cache:{key}"
        return await client.exists(full_key) > 0
    except Exception as e:
        logger.error(f"Cache exists check failed for {key}: {e}")
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """
    Delete all cache keys matching pattern.
    Pattern uses Redis SCAN matching: e.g. "user:*", "billing:*"
    Returns number of keys deleted.
    """
    try:
        client = await get_redis()
        if client is None:
            return 0

        prefix = _get_prefix()
        full_pattern = f"{prefix}:cache:{pattern}"
        deleted = 0
        async for key in client.scan_iter(match=full_pattern, count=100):
            await client.delete(key)
            deleted += 1
        return deleted
    except Exception as e:
        logger.error(f"Cache clear failed for pattern {pattern}: {e}")
        return 0


# === AI CACHE ===

def _ai_cache_key(text: str, schema: Any, model: str = "") -> str:
    """Generate deterministic cache key for AI response."""
    content = f"{text}:{str(schema)}:{model}"
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"ai:{model}:{content_hash}"


async def get_ai_cache(text: str, schema: Any, model: str = "") -> Optional[Dict]:
    """
    Get cached AI response by content hash.
    Returns cached result dict or None.
    """
    key = _ai_cache_key(text, schema, model)
    return await get_cache(key)


async def set_ai_cache(
    text: str, schema: Any, result: Dict, model: str = "", ttl: int = 86400
) -> bool:
    """
    Cache AI response. Default TTL: 24 hours.
    """
    key = _ai_cache_key(text, schema, model)
    return await set_cache(key, result, ttl)
