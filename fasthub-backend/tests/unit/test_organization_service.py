"""
Unit tests for Organization Service
Tests business logic for organization operations
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.organization import Organization
from app.models.user import User
from app.services.organization_service import OrganizationService
from app.schemas.organization import OrganizationUpdate


@pytest_asyncio.fixture
async def org_service(db_session: AsyncSession) -> OrganizationService:
    """Create organization service instance"""
    return OrganizationService(db_session)


@pytest.mark.asyncio
async def test_create_organization(
    org_service: OrganizationService,
    owner_user: User
):
    """Test creating new organization"""
    # Act
    org = await org_service.create_organization(
        name="New Test Organization",
        owner_id=owner_user.id
    )
    
    # Assert
    assert org is not None
    assert org.name == "New Test Organization"
    assert org.owner_id == owner_user.id
    assert org.slug is not None
    assert org.id is not None


@pytest.mark.asyncio
async def test_get_organization_by_id(
    org_service: OrganizationService,
    test_organization: Organization
):
    """Test fetching organization by ID"""
    # Act
    org = await org_service.get_organization_by_id(test_organization.id)
    
    # Assert
    assert org is not None
    assert org.id == test_organization.id
    assert org.name == test_organization.name


@pytest.mark.asyncio
async def test_get_organization_by_id_not_found(
    org_service: OrganizationService
):
    """Test fetching non-existent organization"""
    # Act
    fake_uuid = uuid.UUID('00000000-0000-0000-0000-000000000001')
    org = await org_service.get_organization_by_id(fake_uuid)
    
    # Assert
    assert org is None


@pytest.mark.asyncio
async def test_get_organization_with_stats(
    org_service: OrganizationService,
    test_organization: Organization,
    owner_user: User,
    test_user: User,  # Ensure at least one member exists
    db_session: AsyncSession
):
    """Test fetching organization with statistics"""
    # Arrange - Set owner and email
    test_organization.owner_id = owner_user.id
    test_organization.email = "org@example.com"
    await db_session.commit()
    await db_session.refresh(test_organization)
    
    # Act
    org_with_stats = await org_service.get_organization_with_stats(test_organization.id)
    
    # Assert
    assert org_with_stats is not None
    assert org_with_stats.id == test_organization.id
    assert org_with_stats.name == test_organization.name
    assert org_with_stats.user_count >= 1  # At least test_user is member
    assert hasattr(org_with_stats, 'subscription_status')


@pytest.mark.asyncio
async def test_get_organization_with_stats_not_found(
    org_service: OrganizationService
):
    """Test fetching stats for non-existent organization"""
    # Act & Assert
    fake_uuid = uuid.UUID('00000000-0000-0000-0000-000000000001')
    with pytest.raises(HTTPException) as exc_info:
        await org_service.get_organization_with_stats(fake_uuid)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_update_organization(
    org_service: OrganizationService,
    test_organization: Organization,
    owner_user: User,
    db_session: AsyncSession
):
    """Test updating organization details"""
    # Arrange - Set owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    await db_session.refresh(test_organization)
    
    update_data = OrganizationUpdate(
        name="Updated Organization Name",
        nip="1234567890",
        phone="+48123456789"
    )
    
    # Act
    updated_org = await org_service.update_organization(
        org_id=test_organization.id,
        org_update=update_data,
        current_user=owner_user
    )
    
    # Assert
    assert updated_org.name == "Updated Organization Name"
    assert updated_org.nip == "1234567890"
    assert updated_org.phone == "+48123456789"


@pytest.mark.asyncio
async def test_update_organization_not_owner(
    org_service: OrganizationService,
    test_organization: Organization,
    test_user: User,
    owner_user: User,
    db_session: AsyncSession
):
    """Test updating organization by non-owner user"""
    # Arrange - Set different owner
    test_organization.owner_id = owner_user.id
    await db_session.commit()
    
    update_data = OrganizationUpdate(name="Hacked Name")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await org_service.update_organization(
            org_id=test_organization.id,
            org_update=update_data,
            current_user=test_user  # Not the owner
        )
    
    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.detail.lower() or "owner" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_update_organization_not_found(
    org_service: OrganizationService,
    owner_user: User
):
    """Test updating non-existent organization"""
    # Arrange
    update_data = OrganizationUpdate(name="New Name")
    fake_uuid = uuid.UUID('00000000-0000-0000-0000-000000000001')
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await org_service.update_organization(
            org_id=fake_uuid,
            org_update=update_data,
            current_user=owner_user
        )
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
