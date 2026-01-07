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




