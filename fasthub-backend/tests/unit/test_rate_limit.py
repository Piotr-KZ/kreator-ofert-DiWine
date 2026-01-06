"""
Tests for rate limiting functionality
File: tests/unit/test_rate_limit.py
Coverage: app/core/rate_limit.py
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.rate_limit import (
    check_rate_limit,
    increment_rate_limit,
    reset_rate_limit,
    is_ip_whitelisted,
)


def test_rate_limit_enforcement():
    """Test requests are blocked after exceeding rate limit"""
    identifier = "user:123"
    limit = 5
    window_seconds = 60
    
    with patch('app.core.rate_limit.redis_client') as mock_redis:
        # Simulate 6 requests (over limit of 5)
        mock_redis.get = MagicMock(return_value=b"6")
        
        result = check_rate_limit(identifier, limit, window_seconds)
        
        assert result is False  # Should block request
        mock_redis.get.assert_called_with(f"ratelimit:{identifier}")


def test_rate_limit_reset_after_window():
    """Test rate limit counter resets after time window"""
    identifier = "user:123"
    limit = 10
    window_seconds = 60
    
    with patch('app.core.rate_limit.redis_client') as mock_redis:
        mock_redis.get = MagicMock(return_value=None)  # No existing counter
        mock_redis.setex = MagicMock()
        mock_redis.incr = MagicMock(return_value=1)
        
        # First request - should set counter with TTL
        increment_rate_limit(identifier, window_seconds)
        
        # Verify counter is set with correct TTL
        mock_redis.setex.assert_called_with(
            f"ratelimit:{identifier}",
            window_seconds,
            1
        )
        
        # After window expires, counter should reset
        mock_redis.get = MagicMock(return_value=None)
        result = check_rate_limit(identifier, limit, window_seconds)
        assert result is True  # Should allow request


def test_rate_limit_per_endpoint():
    """Test different endpoints have different rate limits"""
    user_id = "user:123"
    
    # Different endpoints
    endpoint_auth = "/api/v1/auth/login"
    endpoint_api = "/api/v1/organizations"
    
    with patch('app.core.rate_limit.redis_client') as mock_redis:
        mock_redis.get = MagicMock(return_value=None)
        mock_redis.setex = MagicMock()
        
        # Auth endpoint: 5 requests per minute
        identifier_auth = f"{user_id}:{endpoint_auth}"
        result = check_rate_limit(identifier_auth, limit=5, window_seconds=60)
        assert result is True
        
        # API endpoint: 100 requests per minute
        identifier_api = f"{user_id}:{endpoint_api}"
        result = check_rate_limit(identifier_api, limit=100, window_seconds=60)
        assert result is True
        
        # Verify different keys are used
        assert mock_redis.get.call_count == 2
        calls = mock_redis.get.call_args_list
        assert calls[0][0][0] == f"ratelimit:{identifier_auth}"
        assert calls[1][0][0] == f"ratelimit:{identifier_api}"


def test_rate_limit_bypass():
    """Test whitelisted IPs bypass rate limiting"""
    whitelisted_ips = ["127.0.0.1", "10.0.0.1"]
    non_whitelisted_ip = "192.168.1.100"
    
    with patch('app.core.rate_limit.WHITELISTED_IPS', whitelisted_ips):
        # Whitelisted IPs should bypass
        assert is_ip_whitelisted("127.0.0.1") is True
        assert is_ip_whitelisted("10.0.0.1") is True
        
        # Non-whitelisted IP should not bypass
        assert is_ip_whitelisted(non_whitelisted_ip) is False
        
        # Check that whitelisted IP bypasses rate limit check
        with patch('app.core.rate_limit.redis_client') as mock_redis:
            # Even with high request count, whitelisted IP should pass
            mock_redis.get = MagicMock(return_value=b"1000")
            
            result = check_rate_limit(
                f"ip:{whitelisted_ips[0]}",
                limit=10,
                window_seconds=60,
                bypass_whitelist=True
            )
            assert result is True  # Should allow request
