"""Test User model"""
import pytest
from app.models.user import User
from app.core.security import get_password_hash, verify_password

def test_user_password_hashing():
    """Test password is hashed on creation"""
    password = "securepassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 50
    assert verify_password(password, hashed) is True

def test_user_password_verification_wrong():
    """Test wrong password fails verification"""
    password = "correct"
    hashed = get_password_hash(password)
    
    assert verify_password("wrong", hashed) is False

def test_user_email_lowercase():
    """Test email is stored lowercase"""
    user = User(
        email="TEST@EXAMPLE.COM",
        hashed_password=get_password_hash("test")
    )
    assert user.email == "test@example.com"

def test_user_full_name_optional():
    """Test full_name is optional"""
    user = User(
        email="test@test.com",
        hashed_password=get_password_hash("test")
    )
    assert user.full_name is None

def test_user_default_values():
    """Test default values"""
    user = User(
        email="test@test.com",
        hashed_password=get_password_hash("test")
    )
    assert user.is_active is True
    assert user.is_verified is False
