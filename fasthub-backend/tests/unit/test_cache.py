"""
Tests for caching functionality
File: tests/unit/test_cache.py
Coverage: app/core/cache.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import timedelta
from app.core.cache import CacheService


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
