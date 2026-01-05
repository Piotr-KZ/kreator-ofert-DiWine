"""
Integration tests for Members API endpoints
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User
from app.models.organization import Organization


@pytest.mark.asyncio
async def test_list_organization_members(
    async_client: AsyncClient,
    test_organization: Organization,
    test_user: User,
    auth_headers: dict
):
    """Test GET /api/v1/organizations/{id}/members - List members"""
    response = await async_client.get(
        f"/api/v1/organizations/{test_organization.id}/members",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least test_user
    # Check that test_user is in members
    member_ids = [member["user_id"] for member in data]
    assert str(test_user.id) in member_ids


@pytest.mark.asyncio
async def test_add_member(
    async_client: AsyncClient,
    test_organization: Organization,
    owner_user: User,
    db_session
):
    """Test POST /api/v1/organizations/{id}/members - Add member"""
    # Set owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    
    # Create a new user to add as member
    from app.models.user import User as UserModel
    from app.core.security import get_password_hash
    new_user = UserModel(
        email="newmember@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="New Member",
        is_active=True,
        is_verified=True
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    
    # Create auth headers for owner
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(owner_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.post(
        f"/api/v1/organizations/{test_organization.id}/members",
        json={
            "user_id": str(new_user.id),
            "role": "viewer"
        },
        headers=headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == str(new_user.id)
    assert data["role"] == "viewer"


@pytest.mark.asyncio
async def test_update_member_role(
    async_client: AsyncClient,
    test_organization: Organization,
    test_user: User,
    owner_user: User,
    db_session
):
    """Test PATCH /api/v1/organizations/{id}/members/{user_id} - Update role"""
    # Set owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    
    # Create auth headers for owner
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(owner_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.patch(
        f"/api/v1/organizations/{test_organization.id}/members/{test_user.id}",
        json={"role": "admin"},
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_remove_member(
    async_client: AsyncClient,
    test_organization: Organization,
    owner_user: User,
    db_session
):
    """Test DELETE /api/v1/organizations/{id}/members/{user_id} - Remove member"""
    # Set owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    
    # Create a user to remove
    from app.models.user import User as UserModel
    from app.models.member import Member, MemberRole
    from app.core.security import get_password_hash
    
    remove_user = UserModel(
        email="remove@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Remove User",
        is_active=True,
        is_verified=True
    )
    db_session.add(remove_user)
    await db_session.flush()
    
    # Add as member
    member = Member(
        user_id=remove_user.id,
        organization_id=test_organization.id,
        role=MemberRole.VIEWER
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(remove_user)
    
    # Create auth headers for owner
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(owner_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.delete(
        f"/api/v1/organizations/{test_organization.id}/members/{remove_user.id}",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify member is removed
    get_response = await async_client.get(
        f"/api/v1/organizations/{test_organization.id}/members",
        headers=headers
    )
    data = get_response.json()
    member_ids = [m["user_id"] for m in data]
    assert str(remove_user.id) not in member_ids
