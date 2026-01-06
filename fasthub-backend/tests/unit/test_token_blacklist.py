"""
Tests for JWT token blacklist functionality
File: tests/unit/test_token_blacklist.py
Coverage: app/core/token_blacklist.py
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from app.core.token_blacklist import (
    add_token_to_blacklist,
    is_token_blacklisted,
    get_token_expiry,
)


@pytest.mark.asyncio
async def test_add_token_to_blacklist():
    """Test adding JWT token to blacklist after logout"""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    with patch('app.core.token_blacklist.redis_client') as mock_redis:
        mock_redis.setex = AsyncMock()
        
        await add_token_to_blacklist(token, expiry)
        
        # Verify token was added to Redis with correct TTL
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"blacklist:{token}"
        assert call_args[0][1] > 0  # TTL should be positive
        assert call_args[0][2] == "1"


@pytest.mark.asyncio
async def test_is_token_blacklisted():
    """Test checking if token is blacklisted"""
    blacklisted_token = "blacklisted.jwt.token"
    valid_token = "valid.jwt.token"
    
    with patch('app.core.token_blacklist.redis_client') as mock_redis:
        # Mock Redis to return True for blacklisted token, False for valid
        async def mock_exists(key):
            return key == f"blacklist:{blacklisted_token}"
        
        mock_redis.exists = AsyncMock(side_effect=mock_exists)
        
        # Test blacklisted token
        result = await is_token_blacklisted(blacklisted_token)
        assert result is True
        
        # Test valid token
        result = await is_token_blacklisted(valid_token)
        assert result is False


@pytest.mark.asyncio
async def test_blacklist_expiration():
    """Test blacklisted tokens expire after JWT expiration time"""
    token = "test.jwt.token"
    expiry = datetime.utcnow() + timedelta(seconds=30)
    
    with patch('app.core.token_blacklist.redis_client') as mock_redis:
        mock_redis.setex = AsyncMock()
        
        await add_token_to_blacklist(token, expiry)
        
        # Verify TTL is approximately 30 seconds (allow 1 second variance)
        call_args = mock_redis.setex.call_args
        ttl = call_args[0][1]
        assert 29 <= ttl <= 31
        
        # Verify token expires after TTL
        mock_redis.exists = AsyncMock(return_value=False)
        result = await is_token_blacklisted(token)
        assert result is False


@pytest.mark.asyncio
async def test_blacklist_redis_failure():
    """Test graceful handling when Redis is unavailable"""
    token = "test.jwt.token"
    
    with patch('app.core.token_blacklist.redis_client') as mock_redis:
        # Simulate Redis connection failure
        mock_redis.exists = AsyncMock(side_effect=ConnectionError("Redis unavailable"))
        
        # Should return False (allow access) when Redis fails
        # Better to allow access than block legitimate users
        result = await is_token_blacklisted(token)
        assert result is False
        
        # Adding to blacklist should also fail gracefully
        mock_redis.setex = AsyncMock(side_effect=ConnectionError("Redis unavailable"))
        expiry = datetime.utcnow() + timedelta(hours=1)
        
        # Should not raise exception
        try:
            await add_token_to_blacklist(token, expiry)
        except ConnectionError:
            pytest.fail("Should handle Redis failure gracefully")
