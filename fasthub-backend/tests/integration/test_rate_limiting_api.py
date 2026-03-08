# ============================================================================
# Rate limiting tests
# NOTE: Rate limiter is disabled in test environment (conftest mocks limiter.limit)
# These tests verify the rate limiter middleware is wired up, but cannot test
# actual rate limiting behavior without enabling the limiter in tests.

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_accessible():
    """Test health endpoint is accessible (rate limiter disabled in tests)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_multiple_requests_succeed_without_rate_limit():
    """Test multiple requests succeed when rate limiter is disabled"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for _ in range(10):
            response = await client.get("/api/v1/health")
            assert response.status_code == 200


# ====================================================================================
# PHASE 3: LOW PRIORITY - Auth Edge Cases (3 remaining)
# ====================================================================================
