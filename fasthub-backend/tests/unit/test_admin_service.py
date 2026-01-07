"""
Unit tests for Admin Service
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.organization import Organization
from app.services.admin_service import AdminService


@pytest.fixture
def admin_service(db_session: AsyncSession) -> AdminService:
    """Create Admin Service instance"""
    return AdminService(db=db_session)


@pytest.mark.asyncio
async def test_get_system_stats(
    admin_service: AdminService,
    test_user: User,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test fetching system statistics"""
    # Act
    stats = await admin_service.get_system_stats()
    
    # Assert
    assert "users" in stats
    assert "organizations" in stats
    assert "subscriptions" in stats
    assert "invoices" in stats
    
    assert stats["users"]["total"] >= 1  # At least test_user
    assert stats["users"]["active"] >= 0
    assert stats["organizations"]["total"] >= 1  # At least test_organization


@pytest.mark.asyncio
async def test_get_recent_users(
    admin_service: AdminService,
    test_user: User,
    db_session: AsyncSession
):
    """Test fetching recent users"""
    # Act
    recent_users = await admin_service.get_recent_users(limit=10)
    
    # Assert
    assert len(recent_users) >= 1  # At least test_user
    assert isinstance(recent_users[0], User)
    # Most recent user should be first
    assert recent_users[0].created_at >= recent_users[-1].created_at


@pytest.mark.asyncio
async def test_get_recent_users_with_limit(
    admin_service: AdminService,
    test_user: User,
    db_session: AsyncSession
):
    """Test fetching recent users with limit"""
    # Act
    recent_users = await admin_service.get_recent_users(limit=1)
    
    # Assert
    assert len(recent_users) == 1
    assert isinstance(recent_users[0], User)


@pytest.mark.asyncio
async def test_broadcast_message_to_all(
    admin_service: AdminService,
    test_user: User,
    db_session: AsyncSession
):
    """Test broadcasting message to all users"""
    # Act
    result = await admin_service.broadcast_message(
        title="System Maintenance",
        message="The system will be down for maintenance on Sunday.",
        url="https://example.com/maintenance",
        emoji_icon="🔧"
    )
    
    # Assert
    assert result["status"] == "success"
    assert result["users_notified"] >= 1  # At least 1 active user
    assert len(result["target_emails"]) >= 1
    assert result["message"]["title"] == "System Maintenance"
    assert result["message"]["url"] == "https://example.com/maintenance"
    assert result["message"]["emoji"] == "🔧"


@pytest.mark.asyncio
async def test_broadcast_message_to_specific_users(
    admin_service: AdminService,
    test_user: User,
    db_session: AsyncSession
):
    """Test broadcasting message to specific users"""
    # Act
    result = await admin_service.broadcast_message(
        title="Important Update",
        message="Your account has been upgraded.",
        target_user_ids=[test_user.id]
    )
    
    # Assert
    assert result["status"] == "success"
    assert result["users_notified"] == 1
    assert len(result["target_emails"]) == 1
    assert test_user.email in result["target_emails"]


@pytest.mark.asyncio
async def test_broadcast_message_no_users_found(
    admin_service: AdminService,
    db_session: AsyncSession
):
    """Test broadcasting to non-existent users raises error"""
    # Arrange - Use non-existent user IDs
    import uuid
    fake_id = uuid.UUID('00000000-0000-0000-0000-000000000099')
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await admin_service.broadcast_message(
            title="Test",
            message="Test message",
            target_user_ids=[fake_id]
        )
    
    assert exc_info.value.status_code == 404
    assert "No users found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_recent_subscriptions(
    admin_service: AdminService,
    db_session: AsyncSession
):
    """Test fetching recent subscriptions"""
    # Act
    recent_subs = await admin_service.get_recent_subscriptions(limit=10)
    
    # Assert
    # May be empty if no subscriptions exist
    assert isinstance(recent_subs, list)
    if len(recent_subs) > 0:
        # If subscriptions exist, verify ordering
        assert recent_subs[0].created_at >= recent_subs[-1].created_at
