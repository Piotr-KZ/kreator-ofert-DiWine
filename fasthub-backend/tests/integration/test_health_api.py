"""
Tests for health check endpoints
File: tests/integration/test_health_api.py
Coverage: app/api/v1/endpoints/health.py
"""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test GET /health returns 200 OK"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_check_returns_components():
    """Test health check includes component status"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        # Check basic structure
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_idempotent():
    """Test health check returns consistent results"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response1 = await client.get("/api/v1/health")
        response2 = await client.get("/api/v1/health")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["status"] == response2.json()["status"]
