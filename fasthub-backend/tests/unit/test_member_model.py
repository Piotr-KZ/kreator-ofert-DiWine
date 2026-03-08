# ============================================================================

import pytest
from uuid import uuid4
from datetime import datetime
from app.models.member import Member, MemberRole


def test_member_role_validation():
    """Test member role must be admin or viewer"""
    # Valid admin role
    admin_member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.ADMIN
    )
    assert admin_member.role == MemberRole.ADMIN
    assert admin_member.is_admin is True
    assert admin_member.is_viewer is False

    # Valid viewer role
    viewer_member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.VIEWER
    )
    assert viewer_member.role == MemberRole.VIEWER
    assert viewer_member.is_viewer is True
    assert viewer_member.is_admin is False

    # Invalid role should raise ValueError
    with pytest.raises(ValueError):
        Member(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=uuid4(),
            role="invalid_role"
        )


def test_member_permissions_check():
    """Test member permission properties and methods"""
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

    # Admin has admin permissions (property-based)
    assert admin.is_admin is True
    assert admin.is_viewer is False

    # Viewer has viewer permissions (property-based)
    assert viewer.is_admin is False
    assert viewer.is_viewer is True

    # Admin permissions (method-based)
    assert admin.can_edit_organization() is True
    assert admin.can_manage_members() is True
    assert admin.can_view() is True

    # Viewer permissions (method-based)
    assert viewer.can_edit_organization() is False
    assert viewer.can_manage_members() is False
    assert viewer.can_view() is True


def test_member_creation():
    """Test basic member creation"""
    member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.ADMIN,
        joined_at=datetime.utcnow()
    )

    assert member.role == MemberRole.ADMIN
    assert member.joined_at is not None
    assert isinstance(member.joined_at, datetime)


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
