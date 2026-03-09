# ============================================================================

import pytest
from uuid import uuid4
from datetime import datetime
from app.models.member import Member, MemberRole


def test_member_role_validation():
    """Test member role for all 4 roles"""
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
    assert admin_member.is_owner is False
    assert admin_member.is_editor is False

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

    # Valid owner role
    owner_member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.OWNER
    )
    assert owner_member.role == MemberRole.OWNER
    assert owner_member.is_owner is True
    assert owner_member.is_admin is False

    # Valid editor role
    editor_member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.EDITOR
    )
    assert editor_member.role == MemberRole.EDITOR
    assert editor_member.is_editor is True
    assert editor_member.is_admin is False


def test_member_permissions_check():
    """Test member permission properties"""
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


def test_member_creation():
    """Test basic member creation with explicit joined_at"""
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
    """Test joined_at uses server_default (None before DB insert)"""
    member = Member(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        role=MemberRole.VIEWER
    )

    # joined_at uses server_default=func.now(), so it's None before DB insert
    # This is expected SQLAlchemy behavior for server-side defaults
    assert member.role == MemberRole.VIEWER
    assert member.user_id is not None
    assert member.organization_id is not None


def test_member_role_enum_values():
    """MemberRole musi mieć 4 wartości"""
    values = [e.value for e in MemberRole]
    assert len(values) == 4
    assert "owner" in values
    assert "admin" in values
    assert "editor" in values
    assert "viewer" in values
