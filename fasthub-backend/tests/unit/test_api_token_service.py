import pytest
from app.services.api_token_service import APITokenService
from app.models.api_token import APIToken

@pytest.fixture
def token_service():
    return APITokenService()

@pytest.mark.asyncio
async def test_create_api_token(db_session, token_service, test_user):
    """Test API token creation"""
    token = await token_service.create(
        db_session,
        user_id=test_user.id,
        name="Production API Key",
        scopes=["read:users", "write:workflows"]
    )
    assert token.name == "Production API Key"
    assert "read:users" in token.scopes
    assert len(token.token) == 64  # SHA256 hex

@pytest.mark.asyncio
async def test_revoke_api_token(db_session, token_service, test_api_token):
    """Test revoking API token"""
    revoked = await token_service.revoke(db_session, test_api_token.id)
    assert revoked.is_active is False

@pytest.mark.asyncio
async def test_validate_api_token(db_session, token_service, test_api_token):
    """Test validating API token"""
    user = await token_service.validate(db_session, test_api_token.token)
    assert user.id == test_api_token.user_id

@pytest.mark.asyncio
async def test_validate_revoked_token(db_session, token_service, test_api_token):
    """Test validating revoked token"""
    await token_service.revoke(db_session, test_api_token.id)
    
    with pytest.raises(ValueError, match="Token revoked"):
        await token_service.validate(db_session, test_api_token.token)

@pytest.mark.asyncio
async def test_list_user_tokens(db_session, token_service, test_user):
    """Test listing user's API tokens"""
    await token_service.create(db_session, test_user.id, "Token 1", [])
    await token_service.create(db_session, test_user.id, "Token 2", [])
    
    tokens = await token_service.get_user_tokens(db_session, test_user.id)
    assert len(tokens) == 2

@pytest.mark.asyncio
async def test_token_expiration(db_session, token_service, test_api_token):
    """Test token expiration check"""
    import datetime
    test_api_token.expires_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    await db_session.commit()
    
    with pytest.raises(ValueError, match="Token expired"):
        await token_service.validate(db_session, test_api_token.token)
