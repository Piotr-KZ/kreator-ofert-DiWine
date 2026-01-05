"""Test Pydantic schemas validation"""
import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.schemas.auth import Token

def test_user_create_valid():
    """Test valid user creation data"""
    data = {
        "email": "test@test.com",
        "password": "securepass123",
        "full_name": "Test User"
    }
    user = UserCreate(**data)
    assert user.email == "test@test.com"
    assert user.password == "securepass123"

def test_user_create_invalid_email():
    """Test invalid email fails validation"""
    data = {
        "email": "notanemail",
        "password": "pass123"
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_create_password_too_short():
    """Test password minimum length"""
    data = {
        "email": "test@test.com",
        "password": "123"  # Too short
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_update_partial():
    """Test user update allows partial data"""
    data = {"full_name": "New Name"}
    user = UserUpdate(**data)
    assert user.full_name == "New Name"
    assert user.email is None  # Not provided

def test_organization_create_valid():
    """Test valid organization creation"""
    data = {
        "name": "Test Company",
        "email": "info@test.com"
    }
    org = OrganizationCreate(**data)
    assert org.name == "Test Company"

def test_organization_name_required():
    """Test organization name is required"""
    data = {"email": "test@test.com"}
    with pytest.raises(ValidationError):
        OrganizationCreate(**data)

def test_token_schema():
    """Test JWT token schema"""
    data = {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "token_type": "bearer"
    }
    token = Token(**data)
    assert token.token_type == "bearer"
