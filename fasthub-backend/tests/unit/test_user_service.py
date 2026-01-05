"""
Unit tests for User Service
Tests business logic for user operations
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.organization import Organization
from app.services.user_service import UserService
from app.schemas.user import UserUpdate


@pytest_asyncio.fixture
async def user_service(db_session: AsyncSession) -> UserService:
    """Create user service instance"""
    return UserService(db_session)


@pytest_asyncio.fixture
async def another_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create another test user in the same organization"""
    from app.core.security import get_password_hash
    from app.models.member import Member, MemberRole
    
    user = User(
        email="another@example.com",
        hashed_password=get_password_hash("anotherpass123"),
        full_name="Another User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    
    # Create membership in same organization
    member = Member(
        user_id=user.id,
        organization_id=test_organization.id,
        role=MemberRole.VIEWER
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_get_user_by_id(
    user_service: UserService,
    test_user: User
):
    """Test fetching user by ID"""
    # Act
    user = await user_service.get_user_by_id(test_user.id)
    
    # Assert
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email
    assert user.full_name == test_user.full_name


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    user_service: UserService
):
    """Test fetching non-existent user"""
    # Act
    fake_uuid = uuid.UUID('00000000-0000-0000-0000-000000000001')
    user = await user_service.get_user_by_id(fake_uuid)
    
    # Assert
    assert user is None


@pytest.mark.asyncio
async def test_get_users_by_organization(
    user_service: UserService,
    test_organization: Organization,
    test_user: User,
    another_user: User
):
    """Test listing users in organization"""
    # Act
    users = await user_service.get_users_by_organization(
        organization_id=test_organization.id
    )
    
    # Assert
    assert len(users) >= 2  # At least test_user and another_user
    user_ids = [u.id for u in users]
    assert test_user.id in user_ids
    assert another_user.id in user_ids


@pytest.mark.asyncio
async def test_get_users_by_organization_with_pagination(
    user_service: UserService,
    test_organization: Organization,
    test_user: User  # Ensure at least one user exists
):
    """Test listing users with pagination"""
    # Act
    users_page1 = await user_service.get_users_by_organization(
        organization_id=test_organization.id,
        skip=0,
        limit=1
    )
    users_page2 = await user_service.get_users_by_organization(
        organization_id=test_organization.id,
        skip=1,
        limit=1
    )
    
    # Assert
    assert len(users_page1) == 1
    assert len(users_page2) >= 0  # May be 0 or 1 depending on total users
    if len(users_page2) > 0:
        assert users_page1[0].id != users_page2[0].id


@pytest.mark.asyncio
async def test_update_user_by_self(
    user_service: UserService,
    test_user: User
):
    """Test user updating their own profile"""
    # Arrange
    update_data = UserUpdate(
        full_name="Updated Name",
        email="newemail@example.com"
    )
    
    # Act
    updated_user = await user_service.update_user(
        user_id=test_user.id,
        user_update=update_data,
        current_user=test_user
    )
    
    # Assert
    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == "newemail@example.com"


@pytest.mark.asyncio
async def test_update_user_by_superuser(
    user_service: UserService,
    test_user: User,
    test_admin: User
):
    """Test superuser updating another user"""
    # Arrange
    update_data = UserUpdate(full_name="Admin Changed Name")
    
    # Act
    updated_user = await user_service.update_user(
        user_id=test_user.id,
        user_update=update_data,
        current_user=test_admin  # Superuser
    )
    
    # Assert
    assert updated_user.full_name == "Admin Changed Name"


@pytest.mark.asyncio
async def test_update_user_unauthorized(
    user_service: UserService,
    test_user: User,
    another_user: User
):
    """Test non-superuser updating another user (should fail)"""
    # Arrange
    update_data = UserUpdate(full_name="Hacked Name")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(
            user_id=another_user.id,
            user_update=update_data,
            current_user=test_user  # Not superuser, not same user
        )
    
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_update_user_not_found(
    user_service: UserService,
    test_user: User
):
    """Test updating non-existent user"""
    # Arrange
    update_data = UserUpdate(full_name="New Name")
    fake_uuid = uuid.UUID('00000000-0000-0000-0000-000000000001')
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(
            user_id=fake_uuid,
            user_update=update_data,
            current_user=test_user
        )
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
