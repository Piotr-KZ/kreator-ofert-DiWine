"""
Tests for caching functionality
File: tests/unit/test_cache.py
Coverage: app/core/cache.py
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import timedelta
from app.core.cache import cache_set, cache_get, cache_delete, cache_exists


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Test setting and retrieving cached values from Redis"""
    key = "test_key"
    value = {"data": "test_value", "count": 42}
    
    with patch('app.core.cache.redis_client') as mock_redis:
        mock_redis.set = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"data": "test_value", "count": 42}')
        
        await cache_set(key, value)
        result = await cache_get(key)
        
        assert result == value
        mock_redis.set.assert_called_once()
        mock_redis.get.assert_called_once_with(f"cache:{key}")


@pytest.mark.asyncio
async def test_cache_expiration():
    """Test cache entries expire after TTL"""
    key = "expiring_key"
    value = "test_value"
    ttl_seconds = 60
    
    with patch('app.core.cache.redis_client') as mock_redis:
        mock_redis.setex = AsyncMock()
        
        await cache_set(key, value, ttl=timedelta(seconds=ttl_seconds))
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == ttl_seconds


@pytest.mark.asyncio
async def test_cache_delete():
    """Test deleting cached entries"""
    key = "key_to_delete"
    
    with patch('app.core.cache.redis_client') as mock_redis:
        mock_redis.delete = AsyncMock(return_value=1)
        
        result = await cache_delete(key)
        
        assert result is True
        mock_redis.delete.assert_called_once_with(f"cache:{key}")


@pytest.mark.asyncio
async def test_cache_connection_failure():
    """Test graceful handling when Redis is unavailable"""
    key = "test_key"
    
    with patch('app.core.cache.redis_client') as mock_redis:
        mock_redis.get = AsyncMock(side_effect=ConnectionError("Redis down"))
        
        result = await cache_get(key)
        assert result is None  # Should return None instead of raising
