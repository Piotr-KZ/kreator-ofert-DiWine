import pytest
from app.services.cache_service import CacheService

@pytest.fixture
def cache_service():
    return CacheService()

@pytest.mark.asyncio
async def test_set_cache(cache_service):
    """Test setting cache value"""
    await cache_service.set("test_key", {"data": "value"}, ttl=60)
    value = await cache_service.get("test_key")
    assert value["data"] == "value"

@pytest.mark.asyncio
async def test_cache_expiration(cache_service):
    """Test cache TTL expiration"""
    await cache_service.set("expire_key", "value", ttl=1)
    
    import asyncio
    await asyncio.sleep(2)  # Wait for expiration
    
    value = await cache_service.get("expire_key")
    assert value is None

@pytest.mark.asyncio
async def test_delete_cache(cache_service):
    """Test deleting cache key"""
    await cache_service.set("delete_key", "value")
    await cache_service.delete("delete_key")
    
    value = await cache_service.get("delete_key")
    assert value is None

@pytest.mark.asyncio
async def test_clear_pattern(cache_service):
    """Test clearing keys by pattern"""
    await cache_service.set("user:1", "data1")
    await cache_service.set("user:2", "data2")
    await cache_service.set("org:1", "data3")
    
    await cache_service.clear_pattern("user:*")
    
    assert await cache_service.get("user:1") is None
    assert await cache_service.get("user:2") is None
    assert await cache_service.get("org:1") == "data3"  # Still exists
