"""
Unit tests for API Token Service
Tests business logic for API token operations
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.api_token import APIToken
from app.services.api_token_service import APITokenService


@pytest_asyncio.fixture
async def token_service(db_session: AsyncSession) -> APITokenService:
    """Create API token service instance"""
    return APITokenService(db_session)


@pytest.mark.asyncio
async def test_generate_token(token_service: APITokenService):
    """Test generating random API token"""
    # Act
    token1 = token_service.generate_token()
    token2 = token_service.generate_token()
    
    # Assert
    assert len(token1) == 64  # 32 bytes = 64 hex characters
    assert len(token2) == 64
    assert token1 != token2  # Should be unique


@pytest.mark.asyncio
async def test_hash_token(token_service: APITokenService):
    """Test hashing API token"""
    # Arrange
    token = "test_token_12345"
    
    # Act
    hash1 = token_service.hash_token(token)
    hash2 = token_service.hash_token(token)
    
    # Assert
    assert len(hash1) == 64  # SHA-256 = 64 hex characters
    assert hash1 == hash2  # Same input = same hash
    assert hash1 != token  # Hash is different from original


@pytest.mark.asyncio
async def test_create_token(
    token_service: APITokenService,
    test_user: User
):
    """Test creating API token"""
    # Act
    api_token, plaintext_token = await token_service.create_token(
        user_id=test_user.id,
        name="Test Token"
    )
    
    # Assert
    assert api_token is not None
    assert api_token.id is not None
    assert api_token.user_id == test_user.id
    assert api_token.name == "Test Token"
    assert api_token.token_hash is not None
    assert len(plaintext_token) == 64
    assert api_token.token_hash != plaintext_token  # Hash != plaintext
    assert api_token.expires_at is None  # No expiration set


@pytest.mark.asyncio
async def test_create_token_with_expiration(
    token_service: APITokenService,
    test_user: User
):
    """Test creating API token with expiration"""
    # Act
    api_token, plaintext_token = await token_service.create_token(
        user_id=test_user.id,
        name="Expiring Token",
        expires_in_days=30
    )
    
    # Assert
    assert api_token.expires_at is not None
    # Should expire in approximately 30 days
    expected_expiry = datetime.utcnow() + timedelta(days=30)
    time_diff = abs((api_token.expires_at - expected_expiry).total_seconds())
    assert time_diff < 60  # Within 1 minute


@pytest.mark.asyncio
async def test_verify_token_valid(
    token_service: APITokenService,
    test_user: User
):
    """Test verifying valid API token"""
    # Arrange
    api_token, plaintext_token = await token_service.create_token(
        user_id=test_user.id,
        name="Valid Token"
    )
    
    # Act
    verified_user = await token_service.verify_token(plaintext_token)
    
    # Assert
    assert verified_user is not None
    assert verified_user.id == test_user.id
    assert verified_user.email == test_user.email


@pytest.mark.asyncio
async def test_verify_token_invalid(
    token_service: APITokenService
):
    """Test verifying invalid API token"""
    # Act
    verified_user = await token_service.verify_token("invalid_token_12345")
    
    # Assert
    assert verified_user is None


@pytest.mark.asyncio
async def test_verify_token_expired(
    token_service: APITokenService,
    test_user: User,
    db_session: AsyncSession
):
    """Test verifying expired API token"""
    # Arrange - Create token that expires in past
    plaintext_token = token_service.generate_token()
    token_hash = token_service.hash_token(plaintext_token)
    
    expired_token = APIToken(
        user_id=test_user.id,
        token_hash=token_hash,
        name="Expired Token",
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
    )
    db_session.add(expired_token)
    await db_session.commit()
    
    # Act
    verified_user = await token_service.verify_token(plaintext_token)
    
    # Assert
    assert verified_user is None  # Expired token should not verify


@pytest.mark.asyncio
async def test_list_user_tokens(
    token_service: APITokenService,
    test_user: User
):
    """Test listing all tokens for a user"""
    # Arrange - Create multiple tokens
    await token_service.create_token(test_user.id, "Token 1")
    await token_service.create_token(test_user.id, "Token 2")
    await token_service.create_token(test_user.id, "Token 3")
    
    # Act
    tokens = await token_service.list_tokens(test_user.id)
    
    # Assert
    assert len(tokens) >= 3
    token_names = [t.name for t in tokens]
    assert "Token 1" in token_names
    assert "Token 2" in token_names
    assert "Token 3" in token_names


@pytest.mark.asyncio
async def test_delete_token(
    token_service: APITokenService,
    test_user: User
):
    """Test deleting API token"""
    # Arrange
    api_token, plaintext_token = await token_service.create_token(
        test_user.id,
        "Token to Revoke"
    )
    
    # Act
    success = await token_service.delete_token(api_token.id, test_user.id)
    assert success is True
    
    # Verify token no longer works
    verified_user = await token_service.verify_token(plaintext_token)
    
    # Assert
    assert verified_user is None  # Token should be deleted
