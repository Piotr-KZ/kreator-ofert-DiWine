"""
Integration tests for admin API endpoints
"""

from unittest.mock import patch

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_get_system_stats(async_client, test_admin, admin_headers):
    """Test get system statistics (admin only)"""
    response = await async_client.get("/api/v1/admin/stats", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "users" in data
    assert "organizations" in data
    assert "subscriptions" in data
    assert "invoices" in data
    assert isinstance(data["users"]["total"], int)
    assert isinstance(data["organizations"]["total"], int)


@pytest.mark.asyncio
async def test_get_system_stats_unauthorized(async_client, auth_headers):
    """Test get system stats fails for non-admin"""
    response = await async_client.get("/api/v1/admin/stats", headers=auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_recent_users(async_client, test_admin, admin_headers):
    """Test get recent users (admin only)"""
    response = await async_client.get(
        "/api/v1/admin/users/recent", headers=admin_headers, params={"limit": 10}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


@pytest.mark.asyncio
async def test_get_recent_subscriptions(async_client, test_admin, admin_headers):
    """Test get recent subscriptions (admin only)"""
    response = await async_client.get(
        "/api/v1/admin/subscriptions/recent", headers=admin_headers, params={"limit": 10}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
@patch("app.services.email_service.EmailService.send_broadcast_email")
async def test_broadcast_message(
    mock_send_email, async_client, test_admin, test_user, admin_headers
):
    """Test broadcast message to all users (admin only)"""

    mock_send_email.return_value = True

    response = await async_client.post(
        "/api/v1/admin/broadcast",
        headers=admin_headers,
        json={"title": "Important Announcement", "message": "This is a test broadcast message"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["users_notified"] >= 1


@pytest.mark.asyncio
async def test_broadcast_message_unauthorized(async_client, auth_headers):
    """Test broadcast message fails for non-admin"""
    response = await async_client.post(
        "/api/v1/admin/broadcast",
        headers=auth_headers,
        json={"subject": "Test", "message": "Test message"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
