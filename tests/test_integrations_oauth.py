"""
Testy modułu OAuth Base (fasthub_core.integrations.oauth).
"""

import pytest
import asyncio


def test_oauth_imports():
    from fasthub_core.integrations.oauth import (
        OAuthConfig, OAuthTokens, OAuthState, OAuthManager,
        TokenStorage, MemoryTokenStorage
    )
    assert OAuthConfig is not None
    assert OAuthManager is not None


def test_oauth_tokens_expiry():
    from fasthub_core.integrations.oauth import OAuthTokens
    from datetime import datetime, timedelta

    expired = OAuthTokens(
        access_token="test",
        refresh_token="refresh",
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    assert expired.is_expired() == True
    assert expired.should_refresh() == True

    valid = OAuthTokens(
        access_token="test",
        refresh_token="refresh",
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    assert valid.is_expired() == False


def test_oauth_tokens_expires_in_seconds():
    from fasthub_core.integrations.oauth import OAuthTokens
    from datetime import datetime, timedelta

    tokens = OAuthTokens(
        access_token="test",
        expires_at=datetime.utcnow() + timedelta(seconds=600),
    )
    seconds = tokens.expires_in_seconds()
    assert seconds is not None
    assert 590 <= seconds <= 610


def test_oauth_tokens_no_expiry():
    from fasthub_core.integrations.oauth import OAuthTokens
    tokens = OAuthTokens(access_token="test")
    assert tokens.is_expired() == False
    assert tokens.should_refresh() == False
    assert tokens.expires_in_seconds() is None


def test_oauth_tokens_serialization():
    from fasthub_core.integrations.oauth import OAuthTokens
    from datetime import datetime, timedelta

    tokens = OAuthTokens(
        access_token="acc_test",
        refresh_token="ref_test",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        scope="read write"
    )
    d = tokens.to_dict()
    assert d["access_token"] == "acc_test"
    assert d["scope"] == "read write"

    restored = OAuthTokens.from_dict(d)
    assert restored.access_token == "acc_test"
    assert restored.scope == "read write"


def test_memory_token_storage():
    from fasthub_core.integrations.oauth import MemoryTokenStorage, OAuthTokens

    storage = MemoryTokenStorage()
    tokens = OAuthTokens(access_token="test", refresh_token="ref")

    asyncio.get_event_loop().run_until_complete(
        storage.save_tokens("google", "entity-1", tokens)
    )

    result = asyncio.get_event_loop().run_until_complete(
        storage.get_tokens("google", "entity-1")
    )
    assert result.access_token == "test"


def test_memory_token_storage_delete():
    from fasthub_core.integrations.oauth import MemoryTokenStorage, OAuthTokens

    storage = MemoryTokenStorage()
    tokens = OAuthTokens(access_token="test")

    asyncio.get_event_loop().run_until_complete(
        storage.save_tokens("github", "e-1", tokens)
    )
    asyncio.get_event_loop().run_until_complete(
        storage.delete_tokens("github", "e-1")
    )
    result = asyncio.get_event_loop().run_until_complete(
        storage.get_tokens("github", "e-1")
    )
    assert result is None


def test_oauth_config_creation():
    from fasthub_core.integrations.oauth import OAuthConfig
    config = OAuthConfig(
        provider="google",
        client_id="id",
        client_secret="secret",
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        scopes=["email", "profile"],
        redirect_uri="http://localhost:8000/callback",
    )
    assert config.provider == "google"
    assert config.pkce_enabled == False


def test_oauth_state_has_pkce_field():
    from fasthub_core.integrations.oauth import OAuthState
    state = OAuthState(
        state="random-string",
        provider="google",
        redirect_uri="http://localhost/callback",
        code_verifier="pkce-verifier-string"
    )
    assert state.code_verifier is not None


def test_database_token_storage_exists():
    from fasthub_core.integrations.oauth_storage import DatabaseTokenStorage
    assert DatabaseTokenStorage is not None


def test_no_autoflow_model_imports():
    import inspect
    from fasthub_core.integrations import oauth
    source = inspect.getsource(oauth)
    assert "from app.models" not in source
    assert "Integration" not in source  # model AutoFlow


def test_integrations_init_exports():
    """Integrations __init__ powinien eksportować kluczowe klasy"""
    from fasthub_core.integrations import (
        OAuthConfig, OAuthTokens, OAuthState,
        OAuthManager, TokenStorage, MemoryTokenStorage,
    )
    assert OAuthConfig is not None
