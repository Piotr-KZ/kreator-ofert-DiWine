import pytest
from app.services.member_service import MemberService
from app.models.member import Member, MemberRole

@pytest.fixture
def member_service():
    return MemberService()

@pytest.mark.asyncio
async def test_add_member(db_session, member_service, test_organization, test_user):
    """Test adding member to organization"""
    member = await member_service.add_member(
        db_session,
        test_organization.id,
        test_user.id,
        MemberRole.ADMIN
    )
    assert member.role == MemberRole.ADMIN
    assert member.organization_id == test_organization.id

@pytest.mark.asyncio
async def test_add_member_duplicate(db_session, member_service, test_organization, test_user):
    """Test adding same user twice (should fail)"""
    await member_service.add_member(db_session, test_organization.id, test_user.id, MemberRole.ADMIN)
    
    with pytest.raises(ValueError, match="User already member"):
        await member_service.add_member(db_session, test_organization.id, test_user.id, MemberRole.MEMBER)

@pytest.mark.asyncio
async def test_remove_member(db_session, member_service, test_organization, test_user):
    """Test removing member from organization"""
    await member_service.add_member(db_session, test_organization.id, test_user.id, MemberRole.ADMIN)
    await member_service.remove_member(db_session, test_organization.id, test_user.id)
    
    member = await member_service.get_member(db_session, test_organization.id, test_user.id)
    assert member is None

@pytest.mark.asyncio
async def test_remove_last_owner(db_session, member_service, test_organization, test_user):
    """Test preventing removal of last owner"""
    # Assume test_user is OWNER
    with pytest.raises(ValueError, match="Cannot remove last owner"):
        await member_service.remove_member(db_session, test_organization.id, test_user.id)

@pytest.mark.asyncio
async def test_change_member_role(db_session, member_service, test_organization, test_user):
    """Test changing member role"""
    member = await member_service.add_member(db_session, test_organization.id, test_user.id, MemberRole.MEMBER)
    
    updated = await member_service.change_role(
        db_session,
        test_organization.id,
        test_user.id,
        MemberRole.ADMIN
    )
    assert updated.role == MemberRole.ADMIN

@pytest.mark.asyncio
async def test_get_organization_members(db_session, member_service, test_organization):
    """Test listing all organization members"""
    # Add 3 members
    from app.models.user import User
    user1 = User(email="user1@test.com", hashed_password="hash")
    user2 = User(email="user2@test.com", hashed_password="hash")
    db_session.add_all([user1, user2])
    await db_session.commit()
    
    await member_service.add_member(db_session, test_organization.id, user1.id, MemberRole.ADMIN)
    await member_service.add_member(db_session, test_organization.id, user2.id, MemberRole.MEMBER)
    
    members = await member_service.get_organization_members(db_session, test_organization.id)
    assert len(members) >= 2  # At least our 2 + possibly test_user

@pytest.mark.asyncio
async def test_get_user_memberships(db_session, member_service, test_user):
    """Test listing all user's memberships across organizations"""
    # Create 2 orgs
    from app.services.organization_service import OrganizationService
    org_service = OrganizationService()
    org1 = await org_service.create(db_session, name="Org 1")
    org2 = await org_service.create(db_session, name="Org 2")
    
    # Add to both
    await member_service.add_member(db_session, org1.id, test_user.id, MemberRole.OWNER)
    await member_service.add_member(db_session, org2.id, test_user.id, MemberRole.ADMIN)
    
    memberships = await member_service.get_user_memberships(db_session, test_user.id)
    assert len(memberships) == 2

@pytest.mark.asyncio
async def test_check_member_permissions(db_session, member_service, test_organization, test_user):
    """Test checking if member has permission"""
    await member_service.add_member(db_session, test_organization.id, test_user.id, MemberRole.ADMIN)
    
    # Admin can manage members
    has_perm = await member_service.has_permission(
        db_session,
        test_organization.id,
        test_user.id,
        "manage_members"
    )
    assert has_perm is True
    
    # But cannot manage billing (OWNER only)
    has_billing = await member_service.has_permission(
        db_session,
        test_organization.id,
        test_user.id,
        "manage_billing"
    )
    assert has_billing is False
