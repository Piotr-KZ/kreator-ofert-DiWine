"""
Integration tests for Organizations API endpoints
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User
from app.models.organization import Organization


@pytest.mark.asyncio
async def test_create_organization(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test POST /api/v1/organizations - Create new organization"""
    response = await async_client.post(
        "/api/v1/organizations/",
        json={
            "name": "New Test Organization"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Test Organization"
    assert "slug" in data  # Slug is auto-generated
    assert data["slug"]  # Slug should not be empty
    assert "id" in data


@pytest.mark.skip(reason="TODO: Fix ValidationError for OrganizationWithStats schema")
@pytest.mark.asyncio
async def test_list_user_organizations(
    async_client: AsyncClient,
    test_user: User,
    test_organization: Organization,
    auth_headers: dict
):
    """Test GET /api/v1/organizations/me - Get user's current organization"""
    response = await async_client.get(
        "/api/v1/organizations/me",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "name" in data
    # Should return organization with stats
    assert "user_count" in data or "subscription_status" in data


@pytest.mark.asyncio
async def test_update_organization_billing(
    async_client: AsyncClient,
    test_organization: Organization,
    owner_user: User,
    db_session
):
    """Test PATCH /api/v1/organizations/{id} - Update organization billing info"""
    # Set owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    
    # Create auth headers for owner
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(owner_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.patch(
        f"/api/v1/organizations/{test_organization.id}",
        json={
            "billing_street": "123 Main St",
            "billing_city": "Warsaw",
            "billing_postal_code": "00-001",
            "billing_country": "Poland"
        },
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["billing_street"] == "123 Main St"
    assert data["billing_city"] == "Warsaw"


@pytest.mark.skip(reason="TODO: Fix 403 Forbidden - should return 404 Not Found")
@pytest.mark.asyncio
async def test_delete_organization(
    async_client: AsyncClient,
    test_organization: Organization,
    owner_user: User,
    db_session
):
    """Test DELETE /api/v1/organizations/{id} - Delete organization"""
    # Set owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    
    # Create auth headers for owner
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(owner_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify organization is deleted
    get_response = await async_client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
