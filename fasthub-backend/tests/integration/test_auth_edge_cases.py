import pytest
from uuid import uuid4
from unittest.mock import patch
from httpx import AsyncClient
from app.main import app

# Additional tests
# ============================================================================


@pytest.mark.asyncio
async def test_invalid_jwt_token():
    """Test request with malformed JWT returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.malformed.token"}
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower() or "malformed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_expired_jwt_token():
    """Test request with expired JWT returns 401"""
    from app.core.security import create_access_token
    from datetime import timedelta

    # Create expired token
    expired_token = create_access_token(
        data={"sub": str(uuid4())},
        expires_delta=timedelta(seconds=-1)
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_missing_authorization_header():
    """Test protected endpoint without auth header returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")

        # May return 401 or 403 depending on implementation
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_invalid_credentials():
    """Test login with wrong password returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_data = {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "credentials" in response.json()["detail"].lower() or "password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unverified_email_access():
    """Test unverified user cannot access protected endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create user
        user_data = {
            "email": "unverified@example.com",
            "password": "Password123!",
            "full_name": "Unverified User"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        token = response.json()["access_token"]

        # Try to access protected endpoint without verifying email
        with patch('app.api.deps.get_current_user') as mock_user:
            mock_user.return_value.email_verified = False

            response = await client.get(
                "/api/v1/organizations",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 403
            assert "verify" in response.json()["detail"].lower() or "email" in response.json()["detail"].lower()
