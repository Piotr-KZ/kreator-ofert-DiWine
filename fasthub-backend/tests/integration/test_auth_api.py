"""
Integration tests for authentication API endpoints
"""

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_register(async_client):
    """Test user registration endpoint"""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePassword123",
            "full_name": "New User",
            "organization_name": "New Organization",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client, test_user):
    """Test registration with duplicate email fails"""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,  # Duplicate
            "password": "Password123",
            "full_name": "Another User",
            "organization_name": "Another Org",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_register_invalid_email(async_client):
    """Test registration with invalid email fails"""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "Password123",
            "full_name": "User",
            "organization_name": "Org",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login(async_client, test_user):
    """Test user login endpoint"""
    response = await async_client.post(
        "/api/v1/auth/login", json={"email": test_user.email, "password": "testpassword123"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, test_user):
    """Test login with wrong password fails"""
    response = await async_client.post(
        "/api/v1/auth/login", json={"email": test_user.email, "password": "wrongpassword"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    """Test login with nonexistent user fails"""
    response = await async_client.post(
        "/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "password123"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_me(async_client, test_user, auth_headers):
    """Test get current user endpoint"""
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_me_unauthorized(async_client):
    """Test get current user without auth fails"""
    response = await async_client.get("/api/v1/auth/me")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_change_password(async_client, test_user, auth_headers):
    """Test change password endpoint"""
    response = await async_client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "testpassword123", "new_password": "NewSecurePassword123"},
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify new password works
    login_response = await async_client.post(
        "/api/v1/auth/login", json={"email": test_user.email, "password": "NewSecurePassword123"}
    )
    assert login_response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_change_password_wrong_current(async_client, auth_headers):
    """Test change password with wrong current password fails"""
    response = await async_client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "wrongpassword", "new_password": "NewSecurePassword123"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_send_magic_link(async_client, test_user):
    """Test send magic link endpoint"""
    response = await async_client.post(
        "/api/v1/auth/magic-link/send", json={"email": test_user.email}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "If this email exists, a magic link has been sent"


@pytest.mark.asyncio
async def test_send_magic_link_nonexistent_user(async_client):
    """Test send magic link for nonexistent user"""
    response = await async_client.post(
        "/api/v1/auth/magic-link/send", json={"email": "nonexistent@example.com"}
    )

    # Should still return 200 to prevent email enumeration
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh_token(async_client, test_user):
    """Test refresh token endpoint"""
    # First login to get refresh token
    login_response = await async_client.post(
        "/api/v1/auth/login", json={"email": test_user.email, "password": "testpassword123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token to get new access token
    response = await async_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_logout(async_client, auth_headers):
    """Test logout endpoint"""
    response = await async_client.post("/api/v1/auth/logout", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Successfully logged out"
