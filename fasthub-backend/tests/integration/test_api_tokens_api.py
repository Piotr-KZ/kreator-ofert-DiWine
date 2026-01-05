"""
Integration tests for API Tokens API endpoints
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_token(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test POST /api/v1/api-tokens - Create new API token"""
    response = await async_client.post(
        "/api/v1/api-tokens",
        json={
            "name": "Test API Token",
            "scopes": ["read", "write"]
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test API Token"
    assert "token" in data  # Plain token returned only on creation
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tokens(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session
):
    """Test GET /api/v1/api-tokens - List user's API tokens"""
    # Create a token first
    from app.models.api_token import APIToken
    from app.core.security import get_password_hash
    
    token = APIToken(
        user_id=test_user.id,
        name="List Test Token",
        token_hash=get_password_hash("test_token_123"),
        scopes=["read"]
    )
    db_session.add(token)
    await db_session.commit()
    
    response = await async_client.get(
        "/api/v1/api-tokens",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check that our token is in the list
    token_names = [t["name"] for t in data]
    assert "List Test Token" in token_names


@pytest.mark.asyncio
async def test_revoke_token(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session
):
    """Test DELETE /api/v1/api-tokens/{id} - Revoke API token"""
    # Create a token to revoke
    from app.models.api_token import APIToken
    from app.core.security import get_password_hash
    
    token = APIToken(
        user_id=test_user.id,
        name="Revoke Test Token",
        token_hash=get_password_hash("revoke_token_123"),
        scopes=["read"]
    )
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)
    
    response = await async_client.delete(
        f"/api/v1/api-tokens/{token.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify token is deleted
    list_response = await async_client.get(
        "/api/v1/api-tokens",
        headers=auth_headers
    )
    data = list_response.json()
    token_ids = [t["id"] for t in data]
    assert str(token.id) not in token_ids


@pytest.mark.asyncio
async def test_validate_token(
    async_client: AsyncClient,
    test_user: User,
    db_session
):
    """Test POST /api/v1/api-tokens/validate - Validate API token"""
    # Create a token
    from app.models.api_token import APIToken
    from app.core.security import get_password_hash
    import secrets
    
    plain_token = secrets.token_urlsafe(32)
    token = APIToken(
        user_id=test_user.id,
        name="Validate Test Token",
        token_hash=get_password_hash(plain_token),
        scopes=["read", "write"]
    )
    db_session.add(token)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/v1/api-tokens/validate",
        json={"token": plain_token}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["valid"] is True
    assert data["user_id"] == str(test_user.id)
    assert "read" in data["scopes"]
    assert "write" in data["scopes"]


@pytest.mark.asyncio
async def test_validate_invalid_token(
    async_client: AsyncClient
):
    """Test validating invalid API token returns error"""
    response = await async_client.post(
        "/api/v1/api-tokens/validate",
        json={"token": "invalid_token_123"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["valid"] is False
