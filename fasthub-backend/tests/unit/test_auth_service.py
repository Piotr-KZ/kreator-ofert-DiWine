"""
Unit tests for authentication service
"""

from datetime import datetime, timedelta

import pytest

from app.core.security import create_access_token, verify_password
from app.models import User
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user(db_session):
    """Test user registration"""
    auth_service = AuthService(db_session)

    user_data = {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User",
        "organization_name": "New Org",
    }

    user, access_token, refresh_token = await auth_service.register(
        email=user_data["email"],
        password=user_data["password"],
        full_name=user_data["full_name"],
        organization_name=user_data["organization_name"],
    )

    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"]
    assert user.is_verified == True  # Auto-verified in boilerplate
    assert verify_password(user_data["password"], user.hashed_password)
    assert access_token is not None
    assert refresh_token is not None
    # Note: User model no longer has organization_id - uses memberships relationship instead
    assert user.id is not None  # User was created successfully


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session, test_user):
    """Test registration with duplicate email fails"""
    auth_service = AuthService(db_session)

    with pytest.raises(Exception):  # Should raise ValueError or similar
        await auth_service.register(
            email=test_user.email,  # Duplicate
            password="password123",
            full_name="Another User",
            organization_name="Another Org",
        )


@pytest.mark.asyncio
async def test_authenticate_user(db_session, test_user):
    """Test user authentication with correct credentials"""
    auth_service = AuthService(db_session)

    user = await auth_service.authenticate(
        email=test_user.email, password="testpassword123"  # From fixture
    )

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_authenticate_wrong_password(db_session, test_user):
    """Test authentication fails with wrong password"""
    auth_service = AuthService(db_session)

    user = await auth_service.authenticate(email=test_user.email, password="wrongpassword")

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_nonexistent_user(db_session):
    """Test authentication fails for nonexistent user"""
    auth_service = AuthService(db_session)

    user = await auth_service.authenticate(email="nonexistent@example.com", password="password123")

    assert user is None


@pytest.mark.asyncio
async def test_change_password(db_session, test_user):
    """Test password change"""
    auth_service = AuthService(db_session)

    new_password = "newsecurepassword123"
    await auth_service.change_password(
        user_id=test_user.id, current_password="testpassword123", new_password=new_password
    )

    # Verify new password works
    user = await auth_service.authenticate(email=test_user.email, password=new_password)
    assert user is not None


@pytest.mark.asyncio
async def test_change_password_wrong_current(db_session, test_user):
    """Test password change fails with wrong current password"""
    auth_service = AuthService(db_session)

    with pytest.raises(Exception):
        await auth_service.change_password(
            user_id=test_user.id,
            current_password="wrongpassword",
            new_password="newsecurepassword123",
        )


@pytest.mark.asyncio
async def test_generate_magic_link(db_session, test_user):
    """Test magic link generation"""
    auth_service = AuthService(db_session)

    token = await auth_service.generate_magic_link(test_user.email)

    assert token is not None
    assert len(token) > 20  # Should be a long random string

    # Verify token was saved to user
    await db_session.refresh(test_user)
    assert test_user.magic_link_token is not None
    assert test_user.magic_link_expires is not None


@pytest.mark.asyncio
async def test_verify_magic_link(db_session, test_user):
    """Test magic link verification"""
    auth_service = AuthService(db_session)

    # Generate token
    token = await auth_service.generate_magic_link(test_user.email)

    # Verify token
    user = await auth_service.verify_magic_link(token)

    assert user is not None
    assert user.id == test_user.id


@pytest.mark.asyncio
async def test_verify_expired_magic_link(db_session, test_user):
    """Test expired magic link fails"""
    auth_service = AuthService(db_session)

    # Manually set expired token
    test_user.magic_link_token = "expired_token"
    test_user.magic_link_expires = datetime.utcnow() - timedelta(minutes=1)
    await db_session.commit()

    user = await auth_service.verify_magic_link("expired_token")

    assert user is None
