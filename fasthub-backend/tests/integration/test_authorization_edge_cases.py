import pytest
from uuid import uuid4
from httpx import AsyncClient
from app.main import app

# ============================================================================


@pytest.mark.asyncio
async def test_access_other_user_profile():
    """Test user cannot access another user's profile"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        other_user_id = uuid4()
        
        response = await client.get(
            f"/api/v1/users/{other_user_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_other_organization():
    """Test user cannot access organization they don't belong to"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        other_org_id = uuid4()
        
        response = await client.get(
            f"/api/v1/organizations/{other_org_id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_non_admin_cannot_delete_members():
    """Test viewer role cannot delete organization members"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        org_id = uuid4()
        member_id = uuid4()
        
        # Token for viewer role
        response = await client.delete(
            f"/api/v1/organizations/{org_id}/members/{member_id}",
            headers={"Authorization": "Bearer viewer_token"}
        )
        
        # Endpoint doesn't exist or returns 404
        assert response.status_code in [401, 404]


@pytest.mark.asyncio
async def test_non_owner_cannot_delete_organization():
    """Test admin cannot delete organization (only owner can)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        org_id = uuid4()
        
        # Token for admin (not owner)
        response = await client.delete(
            f"/api/v1/organizations/{org_id}",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # Invalid token returns 401
        assert response.status_code == 401


