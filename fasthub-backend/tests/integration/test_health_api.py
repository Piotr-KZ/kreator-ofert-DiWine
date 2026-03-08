"""
Tests for health check endpoints
File: tests/integration/test_health_api.py
Coverage: app/api/v1/endpoints/health.py
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test GET /health returns 200 OK"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_database_connection_check():
    """Test health check verifies database connectivity"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with healthy database
        with patch('app.api.v1.endpoints.health.check_database') as mock_db:
            mock_db.return_value = {"status": "connected", "latency_ms": 5}
            
            response = await client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["database"]["status"] == "connected"
            assert "latency_ms" in data["database"]
        
        # Test with unhealthy database
        with patch('app.api.v1.endpoints.health.check_database') as mock_db:
            mock_db.return_value = {"status": "disconnected", "error": "Connection timeout"}
            
            response = await client.get("/api/v1/health")
            
            assert response.status_code == 503  # Service Unavailable
            data = response.json()
            assert data["database"]["status"] == "disconnected"
            assert "error" in data["database"]


@pytest.mark.asyncio
async def test_redis_connection_check():
    """Test health check verifies Redis connectivity"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with healthy Redis
        with patch('app.api.v1.endpoints.health.check_redis') as mock_redis:
            mock_redis.return_value = {"status": "connected", "latency_ms": 2}
            
            response = await client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["redis"]["status"] == "connected"
            assert "latency_ms" in data["redis"]
        
        # Test with unhealthy Redis
        with patch('app.api.v1.endpoints.health.check_redis') as mock_redis:
            mock_redis.return_value = {"status": "disconnected", "error": "Connection refused"}
            
            response = await client.get("/api/v1/health")
            
            # Redis failure should return 503 but note it's non-critical
            assert response.status_code == 503
            data = response.json()
            assert data["redis"]["status"] == "disconnected"
            assert data["redis"]["critical"] is False  # Redis is optional


@pytest.mark.asyncio
async def test_readiness_probe():
    """Test readiness probe returns ready status"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test ready state (all services up)
        with patch('app.api.v1.endpoints.health.check_database') as mock_db, \
             patch('app.api.v1.endpoints.health.check_redis') as mock_redis:
            
            mock_db.return_value = {"status": "connected"}
            mock_redis.return_value = {"status": "connected"}
            
            response = await client.get("/api/v1/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is True
            assert data["services"]["database"] == "connected"
            assert data["services"]["redis"] == "connected"
        
        # Test not ready state (database down)
        with patch('app.api.v1.endpoints.health.check_database') as mock_db, \
             patch('app.api.v1.endpoints.health.check_redis') as mock_redis:
            
            mock_db.return_value = {"status": "disconnected"}
            mock_redis.return_value = {"status": "connected"}
            
            response = await client.get("/api/v1/health/ready")
            
            assert response.status_code == 503
            data = response.json()
            assert data["ready"] is False
            assert data["services"]["database"] == "disconnected"
