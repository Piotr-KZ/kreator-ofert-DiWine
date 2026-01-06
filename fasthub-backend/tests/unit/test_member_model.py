# ============================================================================

from app.models.member import Member, MemberRole


def test_member_role_validation():
    """Test member role must be admin or viewer"""
    # Valid roles
    admin_member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.ADMIN
    )
    assert admin_member.role == MemberRole.ADMIN
    
    viewer_member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.VIEWER
    )
    assert viewer_member.role == MemberRole.VIEWER
    
    # Invalid role should raise ValueError
    with pytest.raises(ValueError):
        Member(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=uuid4(),
            role="invalid_role"
        )


def test_member_permissions_check():
    """Test member permissions based on role"""
    admin = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.ADMIN
    )
    
    viewer = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.VIEWER
    )
    
    # Admin permissions
    assert admin.can_edit_organization() is True
    assert admin.can_manage_members() is True
    assert admin.can_view() is True
    
    # Viewer permissions
    assert viewer.can_edit_organization() is False
    assert viewer.can_manage_members() is False
    assert viewer.can_view() is True


def test_member_joined_date():
    """Test joined_at is set automatically"""
    member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.VIEWER
    )
    
    assert member.joined_at is not None
    assert isinstance(member.joined_at, datetime)
    assert member.joined_at <= datetime.utcnow()
