"""Test security utilities"""
import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password
)
from jose import jwt
from app.core.config import settings

def test_create_access_token():
    """Test JWT access token creation"""
    data = {"sub": "test@test.com"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 50
    
    # Decode and verify
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test@test.com"
    assert "exp" in decoded

def test_create_refresh_token():
    """Test JWT refresh token creation"""
    data = {"sub": "test@test.com"}
    token = create_refresh_token(data)
    
    assert isinstance(token, str)
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test@test.com"

def test_password_hash_uniqueness():
    """Test same password creates different hashes"""
    password = "samepassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    assert hash1 != hash2  # Bcrypt adds salt
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True

def test_password_verify_case_sensitive():
    """Test password verification is case-sensitive"""
    password = "Test123"
    hashed = get_password_hash(password)
    
    assert verify_password("Test123", hashed) is True
    assert verify_password("test123", hashed) is False
    assert verify_password("TEST123", hashed) is False
