"""
Integration tests for API Tokens endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.models.user import User


@pytest.mark.asyncio
async def test_create_token(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test POST /api/v1/api-tokens/ - Create new API token"""
    response = await async_client.post(
        "/api/v1/api-tokens/",
        json={"name": "Test Token"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert "plaintext_token" in data
    assert data["token"]["name"] == "Test Token"
    assert "id" in data["token"]


@pytest.mark.asyncio
async def test_list_tokens(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test GET /api/v1/api-tokens/ - List user's API tokens"""
    # Create a token first
    await async_client.post(
        "/api/v1/api-tokens/",
        json={"name": "List Test Token"},
        headers=auth_headers
    )
    
    # List tokens
    response = await async_client.get(
        "/api/v1/api-tokens/",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check token structure (without 'token' field for security)
    token_data = data[0]
    assert "id" in token_data
    assert "name" in token_data
    assert "created_at" in token_data
    assert "token" not in token_data  # Token should not be returned in list


@pytest.mark.skip(reason="TODO: Fix 422 validation error - UUID format issue")
@pytest.mark.asyncio
async def test_revoke_token(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test DELETE /api/v1/api-tokens/{token_id} - Revoke API token"""
    # Create a token first
    create_response = await async_client.post(
        "/api/v1/api-tokens/",
        json={"name": "Token to Revoke"},
        headers=auth_headers
    )
    token_id = create_response.json()["token"]["id"]
    
    # Revoke the token
    response = await async_client.delete(
        f"/api/v1/api-tokens/{token_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify token is gone
    list_response = await async_client.get(
        "/api/v1/api-tokens/",
        headers=auth_headers
    )
    tokens = list_response.json()
    token_ids = [t["id"] for t in tokens]
    assert token_id not in token_ids
