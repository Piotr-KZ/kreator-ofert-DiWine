import pytest
from app.services.user_service import UserService
from app.models.user import User

@pytest.fixture
def user_service():
    return UserService()

@pytest.mark.asyncio
async def test_create_user(db_session, user_service):
    """Test user creation"""
    user = await user_service.create(
        db_session,
        email="newuser@test.com",
        password="securepass123",
        full_name="New User"
    )
    assert user.email == "newuser@test.com"
    assert user.full_name == "New User"

@pytest.mark.asyncio
async def test_get_user_by_id(db_session, user_service, test_user):
    """Test fetching user by ID"""
    user = await user_service.get_by_id(db_session, test_user.id)
    assert user.id == test_user.id

@pytest.mark.asyncio
async def test_get_user_by_email(db_session, user_service, test_user):
    """Test fetching user by email"""
    user = await user_service.get_by_email(db_session, test_user.email)
    assert user.id == test_user.id

@pytest.mark.asyncio
async def test_update_user_profile(db_session, user_service, test_user):
    """Test updating user profile"""
    updated = await user_service.update(
        db_session,
        test_user.id,
        full_name="Updated Name"
    )
    assert updated.full_name == "Updated Name"

@pytest.mark.asyncio
async def test_delete_user(db_session, user_service, test_user):
    """Test user deletion"""
    await user_service.delete(db_session, test_user.id)
    deleted = await user_service.get_by_id(db_session, test_user.id)
    assert deleted is None

@pytest.mark.asyncio
async def test_verify_user_email(db_session, user_service, test_user):
    """Test email verification"""
    test_user.email_verified = False
    await db_session.commit()
    
    verified = await user_service.verify_email(db_session, test_user.id)
    assert verified.email_verified is True

@pytest.mark.asyncio
async def test_list_user_organizations(db_session, user_service, test_user):
    """Test listing user's organizations"""
    # Create 2 orgs and add user
    from app.services.organization_service import OrganizationService
    from app.services.member_service import MemberService
    from app.models.member import MemberRole
    
    org_service = OrganizationService()
    member_service = MemberService()
    
    org1 = await org_service.create(db_session, name="Org 1")
    org2 = await org_service.create(db_session, name="Org 2")
    
    await member_service.add_member(db_session, org1.id, test_user.id, MemberRole.OWNER)
    await member_service.add_member(db_session, org2.id, test_user.id, MemberRole.MEMBER)
    
    orgs = await user_service.get_organizations(db_session, test_user.id)
    assert len(orgs) == 2
