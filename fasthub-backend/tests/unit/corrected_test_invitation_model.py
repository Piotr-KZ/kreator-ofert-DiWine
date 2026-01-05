"""Test Invitation model"""
import pytest
from datetime import datetime, timedelta
from app.models.invitation import Invitation

def test_invitation_creation():
    """Test invitation basic fields"""
    token = "abc123xyz"
    expires = datetime.utcnow() + timedelta(days=7)
    
    inv = Invitation(
        email="newuser@test.com",
        organization_id=1,
        invited_by=1,
        role="member",
        token=token,
        expires_at=expires
    )
    assert inv.email == "newuser@test.com"
    assert inv.role == "member"
    assert inv.token == token

def test_invitation_not_accepted_by_default():
    """Test invitation is not accepted by default"""
    inv = Invitation(
        email="test@test.com",
        organization_id=1,
        role="member",
        token="token123",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    assert inv.accepted_at is None

def test_invitation_expires_in_future():
    """Test expiry date is in future"""
    expires = datetime.utcnow() + timedelta(days=7)
    inv = Invitation(
        email="test@test.com",
        organization_id=1,
        role="member",
        token="token123",
        expires_at=expires
    )
    assert inv.expires_at > datetime.utcnow()
