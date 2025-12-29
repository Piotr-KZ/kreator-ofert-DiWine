"""
Integration tests for users API endpoints
"""

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_list_users(async_client, test_user, test_admin, admin_headers):
    """Test list users endpoint (admin only)"""
    response = await async_client.get("/api/v1/users/", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least test_user and test_admin


@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client, auth_headers):
    """Test list users fails for non-admin"""
    response = await async_client.get("/api/v1/users/", headers=auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_me(async_client, test_user, auth_headers):
    """Test get current user profile"""
    response = await async_client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_update_user_profile(async_client, test_user, auth_headers):
    """Test update user profile"""
    response = await async_client.put(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
        json={"full_name": "Updated Name", "email": test_user.email},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_other_user_profile_forbidden(
    async_client, test_user, test_admin, auth_headers
):
    """Test updating another user's profile is forbidden"""
    response = await async_client.put(
        f"/api/v1/users/{test_admin.id}",  # Try to update admin
        headers=auth_headers,  # Using regular user auth
        json={"full_name": "Hacked Name", "email": test_admin.email},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_user(async_client, test_user, admin_headers):
    """Test delete user (admin only)"""
    response = await async_client.delete(f"/api/v1/users/{test_user.id}", headers=admin_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_user_unauthorized(async_client, test_admin, auth_headers):
    """Test delete user fails for non-admin"""
    response = await async_client.delete(f"/api/v1/users/{test_admin.id}", headers=auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
