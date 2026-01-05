import pytest
from app.services.organization_service import OrganizationService
from app.models.organization import Organization
from app.models.member import Member, MemberRole

@pytest.fixture
def organization_service():
    return OrganizationService()

@pytest.mark.asyncio
async def test_create_organization(db_session, organization_service):
    """Test organization creation"""
    org = await organization_service.create(
        db_session,
        name="Test Corp",
        email="admin@testcorp.com",
        tax_id="1234567890"
    )
    assert org.name == "Test Corp"
    assert org.slug == "test-corp"
    assert org.email == "admin@testcorp.com"

@pytest.mark.asyncio
async def test_create_organization_duplicate_slug(db_session, organization_service):
    """Test slug uniqueness"""
    await organization_service.create(db_session, name="Test Corp")
    
    # Should add suffix to slug
    org2 = await organization_service.create(db_session, name="Test Corp")
    assert org2.slug == "test-corp-1"

@pytest.mark.asyncio
async def test_get_organization_by_id(db_session, organization_service, test_organization):
    """Test fetching organization by ID"""
    org = await organization_service.get_by_id(db_session, test_organization.id)
    assert org.id == test_organization.id

@pytest.mark.asyncio
async def test_get_organization_by_slug(db_session, organization_service):
    """Test fetching organization by slug"""
    org = await organization_service.create(db_session, name="Acme Corp")
    found = await organization_service.get_by_slug(db_session, "acme-corp")
    assert found.id == org.id

@pytest.mark.asyncio
async def test_update_organization(db_session, organization_service, test_organization):
    """Test organization update"""
    updated = await organization_service.update(
        db_session,
        test_organization.id,
        name="New Name Corp"
    )
    assert updated.name == "New Name Corp"

@pytest.mark.asyncio
async def test_delete_organization(db_session, organization_service, test_organization):
    """Test organization deletion"""
    await organization_service.delete(db_session, test_organization.id)
    deleted = await organization_service.get_by_id(db_session, test_organization.id)
    assert deleted is None

@pytest.mark.asyncio
async def test_list_user_organizations(db_session, organization_service, test_user):
    """Test listing organizations user belongs to"""
    # Create 2 organizations
    org1 = await organization_service.create(db_session, name="Org 1")
    org2 = await organization_service.create(db_session, name="Org 2")
    
    # Add user as member
    from app.services.member_service import MemberService
    member_service = MemberService()
    await member_service.add_member(db_session, org1.id, test_user.id, MemberRole.ADMIN)
    await member_service.add_member(db_session, org2.id, test_user.id, MemberRole.MEMBER)
    
    orgs = await organization_service.get_user_organizations(db_session, test_user.id)
    assert len(orgs) == 2
