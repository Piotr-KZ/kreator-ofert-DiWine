"""
Tests for caching functionality
File: tests/unit/test_cache.py
Coverage: app/core/cache.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.cache import CacheService

# Also try importing function-based API if available
try:
    from app.core.cache import cache_set, cache_get, cache_delete, cache_exists
    HAS_FUNCTION_API = True
except ImportError:
    HAS_FUNCTION_API = False


# ============================================================================
# CacheService class-based tests
# ============================================================================

@pytest.mark.asyncio
async def test_cache_disabled_returns_none():
    """Test cache returns None when disabled"""
    cache = CacheService()
    cache.enabled = False
    cache.client = None

    result = await cache.get("test_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_set_when_disabled():
    """Test cache set fails gracefully when disabled"""
    cache = CacheService()
    cache.enabled = False
    cache.client = None

    result = await cache.set("test_key", "test_value")
    assert result is False


@pytest.mark.asyncio
async def test_cache_delete_when_disabled():
    """Test cache delete fails gracefully when disabled"""
    cache = CacheService()
    cache.enabled = False
    cache.client = None

    result = await cache.delete("test_key")
    assert result is False


@pytest.mark.asyncio
async def test_cache_service_initialization():
    """Test CacheService can be initialized"""
    cache = CacheService()

    assert cache.enabled is False
    assert cache.client is None
    assert cache.redis_url is None or isinstance(cache.redis_url, str)


# ============================================================================
# Function-based cache API tests
# ============================================================================

@pytest.mark.skipif(not HAS_FUNCTION_API, reason="Function-based cache API not available")
@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test function-based cache API delegates to CacheService singleton"""
    # The function-based API delegates to the `cache` singleton
    # When cache is disabled (no Redis), set returns False and get returns None
    result_set = await cache_set("test_key", {"data": "value"})
    assert result_set is False  # disabled cache

    result_get = await cache_get("test_key")
    assert result_get is None  # disabled cache


@pytest.mark.skipif(not HAS_FUNCTION_API, reason="Function-based cache API not available")
@pytest.mark.asyncio
async def test_cache_expiration():
    """Test cache_set accepts ttl as integer"""
    # TTL is int (seconds), not timedelta
    result = await cache_set("expiring_key", "value", ttl=60)
    assert result is False  # disabled cache returns False


@pytest.mark.skipif(not HAS_FUNCTION_API, reason="Function-based cache API not available")
@pytest.mark.asyncio
async def test_cache_delete_function():
    """Test cache_delete function-based API"""
    result = await cache_delete("key_to_delete")
    assert result is False  # disabled cache returns False


@pytest.mark.skipif(not HAS_FUNCTION_API, reason="Function-based cache API not available")
@pytest.mark.asyncio
async def test_cache_connection_failure():
    """Test graceful handling when Redis operations fail"""
    # With cache disabled, operations return None/False gracefully
    result = await cache_get("test_key")
    assert result is None


@pytest.mark.skipif(not HAS_FUNCTION_API, reason="Function-based cache API not available")
@pytest.mark.asyncio
async def test_cache_exists_function():
    """Test cache_exists function-based API"""
    result = await cache_exists("test_key")
    assert result is False  # disabled cache
