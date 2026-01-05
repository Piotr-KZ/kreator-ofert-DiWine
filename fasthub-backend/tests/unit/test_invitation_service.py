import pytest
from app.services.invitation_service import InvitationService
from app.models.invitation import Invitation, InvitationStatus
from app.models.member import MemberRole

@pytest.fixture
def invitation_service():
    return InvitationService()

@pytest.mark.asyncio
async def test_create_invitation(db_session, invitation_service, test_organization, test_user):
    """Test creating invitation"""
    invitation = await invitation_service.create(
        db_session,
        organization_id=test_organization.id,
        email="newmember@test.com",
        role=MemberRole.ADMIN,
        invited_by_id=test_user.id
    )
    assert invitation.email == "newmember@test.com"
    assert invitation.status == InvitationStatus.PENDING
    assert len(invitation.token) == 32  # UUID hex

@pytest.mark.asyncio
async def test_accept_invitation(db_session, invitation_service, test_invitation):
    """Test accepting invitation"""
    # Create user
    from app.models.user import User
    user = User(email=test_invitation.email, hashed_password="hash")
    db_session.add(user)
    await db_session.commit()
    
    # Accept invitation
    member = await invitation_service.accept(
        db_session,
        test_invitation.token,
        user.id
    )
    assert member.user_id == user.id
    assert member.organization_id == test_invitation.organization_id
    
    # Verify invitation marked as accepted
    await db_session.refresh(test_invitation)
    assert test_invitation.status == InvitationStatus.ACCEPTED

@pytest.mark.asyncio
async def test_accept_expired_invitation(db_session, invitation_service, test_invitation):
    """Test accepting expired invitation"""
    import datetime
    test_invitation.expires_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    await db_session.commit()
    
    with pytest.raises(ValueError, match="Invitation expired"):
        await invitation_service.accept(db_session, test_invitation.token, 999)

@pytest.mark.asyncio
async def test_revoke_invitation(db_session, invitation_service, test_invitation):
    """Test revoking invitation"""
    revoked = await invitation_service.revoke(db_session, test_invitation.id)
    assert revoked.status == InvitationStatus.REVOKED

@pytest.mark.asyncio
async def test_list_organization_invitations(db_session, invitation_service, test_organization):
    """Test listing pending invitations for organization"""
    # Create 2 pending, 1 accepted
    inv1 = await invitation_service.create(db_session, test_organization.id, "user1@test.com", MemberRole.MEMBER, 1)
    inv2 = await invitation_service.create(db_session, test_organization.id, "user2@test.com", MemberRole.MEMBER, 1)
    inv3 = await invitation_service.create(db_session, test_organization.id, "user3@test.com", MemberRole.ADMIN, 1)
    await invitation_service.revoke(db_session, inv3.id)
    
    pending = await invitation_service.get_pending_invitations(db_session, test_organization.id)
    assert len(pending) == 2
