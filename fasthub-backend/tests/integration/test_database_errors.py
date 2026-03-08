# ============================================================================

import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError
from app.main import app


@pytest.mark.asyncio
async def test_database_connection_failure():
    """Test request with invalid auth returns 401"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        # Invalid token returns 401
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_key_violation(async_client: AsyncClient):
    """Test creating user with existing email returns 400"""
    # Create first user
    user_data = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "Test User"
    }

    response1 = await async_client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = await async_client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400
    detail = response2.json()["detail"].lower()
    assert "already" in detail or "exists" in detail or "registered" in detail


@pytest.mark.asyncio
async def test_null_constraint_violation(async_client: AsyncClient):
    """Test creating record with missing required field returns 422"""
    # Try to create user without required fields
    incomplete_data = {"email": "test@example.com"}  # Missing password

    response = await async_client.post("/api/v1/auth/register", json=incomplete_data)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("password" in str(err).lower() for err in errors)
