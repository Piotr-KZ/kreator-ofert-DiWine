# ============================================================================

import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.schemas.member import MemberCreate, MemberUpdate
from app.schemas.api_token import APITokenCreate
from app.schemas.auth import LoginRequest
from app.schemas.admin import AdminUpdateUser


def test_user_schema_required_fields():
    """Test UserCreate requires email and password"""
    with pytest.raises(ValidationError) as exc:
        UserCreate()
    
    errors = exc.value.errors()
    required_fields = [err["loc"][0] for err in errors]
    assert "email" in required_fields
    assert "password" in required_fields


def test_user_schema_email_validation():
    """Test UserCreate validates email format"""
    with pytest.raises(ValidationError):
        UserCreate(email="invalid-email", password="Pass123!")


def test_user_schema_password_length():
    """Test UserCreate validates password minimum length"""
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", password="short")


def test_organization_schema_name_required():
    """Test OrganizationCreate requires name field"""
    with pytest.raises(ValidationError) as exc:
        OrganizationCreate()
    
    errors = exc.value.errors()
    assert any(err["loc"][0] == "name" for err in errors)


def test_organization_schema_name_length():
    """Test OrganizationCreate validates name length (max 255)"""
    with pytest.raises(ValidationError):
        OrganizationCreate(name="a" * 256)


def test_member_schema_email_required():
    """Test MemberCreate requires email field"""
    with pytest.raises(ValidationError) as exc:
        MemberCreate(role="admin")
    
    errors = exc.value.errors()
    assert any(err["loc"][0] == "email" for err in errors)


def test_member_schema_role_enum():
    """Test MemberCreate validates role is admin or viewer"""
    with pytest.raises(ValidationError):
        MemberCreate(email="test@example.com", role="invalid_role")


def test_api_token_schema_name_required():
    """Test APITokenCreate requires name field"""
    with pytest.raises(ValidationError) as exc:
        APITokenCreate()
    
    errors = exc.value.errors()
    assert any(err["loc"][0] == "name" for err in errors)


def test_api_token_schema_name_length():
    """Test APITokenCreate validates name length (max 255)"""
    with pytest.raises(ValidationError):
        APITokenCreate(name="a" * 256)


def test_auth_schema_email_format():
    """Test LoginRequest validates email format"""
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="Pass123!")


def test_auth_schema_password_required():
    """Test LoginRequest requires password field"""
    with pytest.raises(ValidationError) as exc:
        LoginRequest(email="test@example.com")
    
    errors = exc.value.errors()
    assert any(err["loc"][0] == "password" for err in errors)


def test_admin_schema_user_id_uuid():
    """Test AdminUpdateUser validates user_id is valid UUID"""
    with pytest.raises(ValidationError):
        AdminUpdateUser(user_id="not-a-uuid")


def test_user_update_schema_optional_fields():
    """Test UserUpdate allows partial updates"""
    # Should work with just one field
    user_update = UserUpdate(full_name="New Name")
    assert user_update.full_name == "New Name"
    assert user_update.email is None


def test_organization_update_schema_optional_fields():
    """Test OrganizationUpdate allows partial updates"""
    org_update = OrganizationUpdate(description="New description")
    assert org_update.description == "New description"
    assert org_update.name is None


def test_member_update_schema_role_only():
    """Test MemberUpdate only allows role field"""
    member_update = MemberUpdate(role="admin")
    assert member_update.role == "admin"
    
    # Should not have other fields
    assert not hasattr(member_update, "email")


# ====================================================================================
# PHASE 3: LOW PRIORITY - Rate Limiting Integration (5 tests)
# ====================================================================================
