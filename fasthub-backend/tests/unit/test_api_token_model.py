# ============================================================================

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.models.api_token import APIToken


def test_token_hash_validation():
    """Test token hash is validated correctly"""
    token = APIToken(
        id=uuid4(),
        name="Test Token",
        token_hash="hashed_token_value",
        user_id=uuid4(),
        organization_id=uuid4()
    )

    # Valid hash
    assert token.verify_token("correct_token") is True

    # Invalid hash
    assert token.verify_token("wrong_token") is False


def test_token_expiration_check():
    """Test expired tokens are detected"""
    # Expired token
    expired_token = APIToken(
        id=uuid4(),
        name="Expired Token",
        token_hash="hash",
        user_id=uuid4(),
        organization_id=uuid4(),
        expires_at=datetime.utcnow() - timedelta(days=1)
    )

    assert expired_token.is_expired is True
    assert expired_token.is_expired() is True
    assert expired_token.is_valid() is False

    # Valid token
    valid_token = APIToken(
        id=uuid4(),
        name="Valid Token",
        token_hash="hash",
        user_id=uuid4(),
        organization_id=uuid4(),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )

    assert valid_token.is_expired is False
    assert valid_token.is_expired() is False
    assert valid_token.is_valid() is True


def test_token_without_expiration():
    """Test tokens without expiration never expire"""
    token = APIToken(
        id=uuid4(),
        name="No Expiry Token",
        token_hash="hash",
        user_id=uuid4(),
        expires_at=None
    )

    assert token.is_expired is False
    assert token.is_valid() is True


def test_token_creation():
    """Test basic token creation"""
    token = APIToken(
        id=uuid4(),
        name="Test Token",
        token_hash="hashed_value",
        user_id=uuid4()
    )

    assert token.name == "Test Token"
    assert token.token_hash == "hashed_value"
    assert token.last_used_at is None


def test_last_used_timestamp_update():
    """Test last_used_at is updated on token use"""
    token = APIToken(
        id=uuid4(),
        name="Test Token",
        token_hash="hash",
        user_id=uuid4(),
        organization_id=uuid4(),
        last_used_at=None
    )

    assert token.last_used_at is None

    token.update_last_used()

    assert token.last_used_at is not None
    assert isinstance(token.last_used_at, datetime)
