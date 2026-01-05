import pytest
from app.services.rate_limiter import RateLimiter

@pytest.fixture
def rate_limiter():
    return RateLimiter()

@pytest.mark.asyncio
async def test_rate_limit_allows_requests(rate_limiter):
    """Test rate limiter allows requests within limit"""
    key = "user:123:api_calls"
    limit = 10
    window = 60  # 60 seconds
    
    # First 10 requests should succeed
    for i in range(10):
        allowed = await rate_limiter.check(key, limit, window)
        assert allowed is True

@pytest.mark.asyncio
async def test_rate_limit_blocks_excess(rate_limiter):
    """Test rate limiter blocks requests over limit"""
    key = "user:456:api_calls"
    limit = 5
    window = 60
    
    # Use up limit
    for i in range(5):
        await rate_limiter.check(key, limit, window)
    
    # 6th request should be blocked
    allowed = await rate_limiter.check(key, limit, window)
    assert allowed is False

@pytest.mark.asyncio
async def test_rate_limit_resets(rate_limiter):
    """Test rate limiter resets after window"""
    key = "user:789:api_calls"
    limit = 3
    window = 2  # 2 seconds
    
    # Use up limit
    for i in range(3):
        await rate_limiter.check(key, limit, window)
    
    # Wait for reset
    import asyncio
    await asyncio.sleep(3)
    
    # Should allow again
    allowed = await rate_limiter.check(key, limit, window)
    assert allowed is True

@pytest.mark.asyncio
async def test_get_remaining_quota(rate_limiter):
    """Test getting remaining quota"""
    key = "user:999:api_calls"
    limit = 100
    window = 3600
    
    # Make 25 requests
    for i in range(25):
        await rate_limiter.check(key, limit, window)
    
    remaining = await rate_limiter.get_remaining(key, limit, window)
    assert remaining == 75
