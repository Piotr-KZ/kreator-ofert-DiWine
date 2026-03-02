"""
Testy modułu Social Login (Brief 18).
Testuje: social_providers, social_login service, social_routes, user linking.
"""

import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import asdict

# Ustaw SECRET_KEY przed importami fasthub_core
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-social-login-tests-12345")


# ============================================================================
# 1. Import tests
# ============================================================================

def test_social_providers_imports():
    from fasthub_core.auth.social_providers import (
        PROVIDER_CONFIGS,
        USERINFO_URLS,
        SUPPORTED_PROVIDERS,
        SocialUserInfo,
        get_provider_config,
        fetch_user_info,
    )
    assert PROVIDER_CONFIGS is not None
    assert USERINFO_URLS is not None
    assert SUPPORTED_PROVIDERS is not None


def test_social_login_imports():
    from fasthub_core.auth.social_login import (
        SocialLoginService,
        get_social_login_service,
        reset_oauth_managers,
    )
    assert SocialLoginService is not None
    assert callable(get_social_login_service)


def test_social_routes_imports():
    from fasthub_core.auth.social_routes import router
    assert router is not None
    assert router.prefix == "/api/auth"


def test_auth_init_exports():
    from fasthub_core.auth import (
        social_login_router,
        SocialLoginService,
        get_social_login_service,
        SocialUserInfo,
        SUPPORTED_PROVIDERS,
        get_provider_config,
        fetch_user_info,
    )
    assert social_login_router is not None
    assert SocialLoginService is not None


def test_core_init_exports():
    from fasthub_core import (
        social_login_router,
        SocialLoginService,
        get_social_login_service,
        SUPPORTED_PROVIDERS,
    )
    assert social_login_router is not None


# ============================================================================
# 2. SocialUserInfo
# ============================================================================

def test_social_user_info_creation():
    from fasthub_core.auth.social_providers import SocialUserInfo

    info = SocialUserInfo(
        provider="google",
        external_id="123456",
        email="test@example.com",
        full_name="Test User",
        avatar_url="https://example.com/avatar.jpg",
    )
    assert info.provider == "google"
    assert info.external_id == "123456"
    assert info.email == "test@example.com"
    assert info.full_name == "Test User"
    assert info.avatar_url == "https://example.com/avatar.jpg"


def test_social_user_info_optional_avatar():
    from fasthub_core.auth.social_providers import SocialUserInfo

    info = SocialUserInfo(
        provider="github",
        external_id="789",
        email="user@example.com",
        full_name="GitHub User",
    )
    assert info.avatar_url is None


# ============================================================================
# 3. SUPPORTED_PROVIDERS
# ============================================================================

def test_supported_providers_list():
    from fasthub_core.auth.social_providers import SUPPORTED_PROVIDERS
    assert "google" in SUPPORTED_PROVIDERS
    assert "github" in SUPPORTED_PROVIDERS
    assert "microsoft" in SUPPORTED_PROVIDERS
    assert len(SUPPORTED_PROVIDERS) == 3


def test_provider_configs_complete():
    from fasthub_core.auth.social_providers import PROVIDER_CONFIGS
    for provider in ["google", "github", "microsoft"]:
        config = PROVIDER_CONFIGS[provider]
        assert "authorization_url" in config
        assert "token_url" in config
        assert "scopes" in config
        assert "pkce_enabled" in config
        assert isinstance(config["scopes"], list)
        assert len(config["scopes"]) > 0


def test_userinfo_urls_complete():
    from fasthub_core.auth.social_providers import USERINFO_URLS
    for provider in ["google", "github", "microsoft"]:
        assert provider in USERINFO_URLS
        assert USERINFO_URLS[provider].startswith("https://")


# ============================================================================
# 4. _parse_userinfo
# ============================================================================

def test_parse_google_userinfo():
    from fasthub_core.auth.social_providers import _parse_userinfo

    data = {
        "id": "google123",
        "email": "user@gmail.com",
        "name": "Google User",
        "picture": "https://lh3.googleusercontent.com/photo.jpg",
    }
    result = _parse_userinfo("google", data)
    assert result.provider == "google"
    assert result.external_id == "google123"
    assert result.email == "user@gmail.com"
    assert result.full_name == "Google User"
    assert result.avatar_url == "https://lh3.googleusercontent.com/photo.jpg"


def test_parse_github_userinfo():
    from fasthub_core.auth.social_providers import _parse_userinfo

    data = {
        "id": 456789,
        "email": "dev@github.com",
        "name": "GitHub Dev",
        "login": "ghdev",
        "avatar_url": "https://avatars.githubusercontent.com/u/456789",
    }
    result = _parse_userinfo("github", data)
    assert result.provider == "github"
    assert result.external_id == "456789"
    assert result.email == "dev@github.com"
    assert result.full_name == "GitHub Dev"
    assert result.avatar_url.startswith("https://avatars.githubusercontent.com")


def test_parse_github_userinfo_no_name():
    """GitHub user bez ustawionego name — fallback na login."""
    from fasthub_core.auth.social_providers import _parse_userinfo

    data = {
        "id": 111,
        "email": "dev@github.com",
        "name": None,
        "login": "mylogin",
    }
    result = _parse_userinfo("github", data)
    assert result.full_name == "mylogin"


def test_parse_microsoft_userinfo():
    from fasthub_core.auth.social_providers import _parse_userinfo

    data = {
        "id": "ms-uuid-123",
        "mail": "user@outlook.com",
        "displayName": "Microsoft User",
    }
    result = _parse_userinfo("microsoft", data)
    assert result.provider == "microsoft"
    assert result.external_id == "ms-uuid-123"
    assert result.email == "user@outlook.com"
    assert result.full_name == "Microsoft User"
    assert result.avatar_url is None  # Microsoft nie zwraca avatara z /me


def test_parse_microsoft_userinfo_upn_fallback():
    """Microsoft: mail=null → fallback na userPrincipalName."""
    from fasthub_core.auth.social_providers import _parse_userinfo

    data = {
        "id": "ms-456",
        "mail": None,
        "userPrincipalName": "user@company.onmicrosoft.com",
        "displayName": "Company User",
    }
    result = _parse_userinfo("microsoft", data)
    assert result.email == "user@company.onmicrosoft.com"


def test_parse_unknown_provider_raises():
    from fasthub_core.auth.social_providers import _parse_userinfo

    with pytest.raises(ValueError, match="Unknown provider"):
        _parse_userinfo("facebook", {"id": "1"})


# ============================================================================
# 5. get_provider_config
# ============================================================================

def test_get_provider_config_with_explicit_credentials():
    from fasthub_core.auth.social_providers import get_provider_config

    config = get_provider_config(
        "google",
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uri="http://localhost:8000/callback",
    )
    assert config.provider == "google"
    assert config.client_id == "test-client-id"
    assert config.client_secret == "test-client-secret"
    assert config.redirect_uri == "http://localhost:8000/callback"
    assert "openid" in config.scopes


def test_get_provider_config_github():
    from fasthub_core.auth.social_providers import get_provider_config

    config = get_provider_config(
        "github",
        client_id="gh-id",
        client_secret="gh-secret",
    )
    assert config.provider == "github"
    assert "user:email" in config.scopes
    assert config.pkce_enabled == False


def test_get_provider_config_microsoft_pkce():
    from fasthub_core.auth.social_providers import get_provider_config

    config = get_provider_config(
        "microsoft",
        client_id="ms-id",
        client_secret="ms-secret",
    )
    assert config.pkce_enabled == True


def test_get_provider_config_unknown_raises():
    from fasthub_core.auth.social_providers import get_provider_config

    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider_config("facebook", client_id="x", client_secret="y")


def test_get_provider_config_missing_credentials_raises():
    """Brak credentials w Settings → ValueError."""
    from fasthub_core.auth.social_providers import get_provider_config

    # Google bez podania credentials — Settings nie ma ich ustawionych
    with pytest.raises(ValueError, match="Missing credentials"):
        get_provider_config("google")


def test_get_provider_config_default_redirect_uri():
    """Brak redirect_uri → auto-generuj z BACKEND_URL."""
    from fasthub_core.auth.social_providers import get_provider_config

    config = get_provider_config(
        "google",
        client_id="test-id",
        client_secret="test-secret",
    )
    assert "/api/v1/auth/google/callback" in config.redirect_uri


# ============================================================================
# 6. SocialLoginService
# ============================================================================

def test_social_login_service_singleton():
    from fasthub_core.auth.social_login import get_social_login_service, SocialLoginService

    s1 = get_social_login_service()
    s2 = get_social_login_service()
    assert s1 is s2
    assert isinstance(s1, SocialLoginService)


def test_social_login_service_get_login_url_unsupported():
    from fasthub_core.auth.social_login import SocialLoginService

    service = SocialLoginService()
    with pytest.raises(ValueError, match="Unsupported provider"):
        asyncio.get_event_loop().run_until_complete(
            service.get_login_url("facebook")
        )


def test_social_login_service_handle_callback_unsupported():
    from fasthub_core.auth.social_login import SocialLoginService

    service = SocialLoginService()
    mock_db = MagicMock()
    with pytest.raises(ValueError, match="Unsupported provider"):
        asyncio.get_event_loop().run_until_complete(
            service.handle_callback("facebook", "code", "state", mock_db)
        )


def test_reset_oauth_managers():
    from fasthub_core.auth.social_login import reset_oauth_managers, _oauth_managers

    # Dodaj coś do managerów
    _oauth_managers["test"] = "dummy"
    assert "test" in _oauth_managers

    reset_oauth_managers()
    assert len(_oauth_managers) == 0


# ============================================================================
# 7. Social routes
# ============================================================================

def test_social_routes_registered():
    from fasthub_core.auth.social_routes import router

    routes = [r.path for r in router.routes]
    assert "/api/auth/{provider}/login" in routes
    assert "/api/auth/{provider}/callback" in routes


def test_social_routes_tags():
    from fasthub_core.auth.social_routes import router

    assert "Social Login" in router.tags


# ============================================================================
# 8. User model — social login fields
# ============================================================================

def test_user_model_has_social_fields():
    from fasthub_core.users.models import User

    assert hasattr(User, "google_id")
    assert hasattr(User, "github_id")
    assert hasattr(User, "microsoft_id")
    assert hasattr(User, "oauth_provider")
    assert hasattr(User, "avatar_url")


# ============================================================================
# 9. Config — OAuth settings
# ============================================================================

def test_config_has_oauth_settings():
    from fasthub_core.config import Settings

    # Sprawdź, że pola istnieją w modelu
    fields = Settings.model_fields
    assert "GOOGLE_CLIENT_ID" in fields
    assert "GOOGLE_CLIENT_SECRET" in fields
    assert "GITHUB_CLIENT_ID" in fields
    assert "GITHUB_CLIENT_SECRET" in fields
    assert "MICROSOFT_CLIENT_ID" in fields
    assert "MICROSOFT_CLIENT_SECRET" in fields
    assert "BACKEND_URL" in fields


def test_config_oauth_defaults():
    from fasthub_core.config import get_settings

    settings = get_settings()
    # Domyślne wartości — None
    assert settings.GOOGLE_CLIENT_ID is None
    assert settings.GITHUB_CLIENT_ID is None
    assert settings.MICROSOFT_CLIENT_ID is None
    assert settings.BACKEND_URL == "http://localhost:8000"


# ============================================================================
# 10. fetch_user_info (mock httpx)
# ============================================================================

def test_fetch_user_info_google():
    from fasthub_core.auth.social_providers import fetch_user_info

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "g123",
        "email": "user@gmail.com",
        "name": "Google User",
        "picture": "https://photo.url",
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient") as MockAsyncClient:
        MockAsyncClient.return_value = mock_client
        result = asyncio.get_event_loop().run_until_complete(
            fetch_user_info("google", "fake-access-token")
        )

    assert result.provider == "google"
    assert result.email == "user@gmail.com"
    assert result.external_id == "g123"


def test_fetch_user_info_github_with_email_fallback():
    """GitHub: /user nie zwraca email → pobierz z /user/emails."""
    from fasthub_core.auth.social_providers import fetch_user_info

    # /user response (bez emaila)
    user_response = MagicMock()
    user_response.status_code = 200
    user_response.json.return_value = {
        "id": 789,
        "email": None,
        "name": "GH User",
        "login": "ghuser",
        "avatar_url": "https://avatar.url",
    }
    user_response.raise_for_status = MagicMock()

    # /user/emails response
    emails_response = MagicMock()
    emails_response.status_code = 200
    emails_response.json.return_value = [
        {"email": "secondary@example.com", "primary": False},
        {"email": "primary@example.com", "primary": True},
    ]

    mock_client = AsyncMock()
    mock_client.get.side_effect = [user_response, emails_response]
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient") as MockAsyncClient:
        MockAsyncClient.return_value = mock_client
        result = asyncio.get_event_loop().run_until_complete(
            fetch_user_info("github", "fake-token")
        )

    assert result.email == "primary@example.com"
    assert result.provider == "github"


def test_fetch_user_info_microsoft():
    from fasthub_core.auth.social_providers import fetch_user_info

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "ms-uuid",
        "mail": "user@outlook.com",
        "displayName": "MS User",
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient") as MockAsyncClient:
        MockAsyncClient.return_value = mock_client
        result = asyncio.get_event_loop().run_until_complete(
            fetch_user_info("microsoft", "fake-token")
        )

    assert result.provider == "microsoft"
    assert result.email == "user@outlook.com"


def test_fetch_user_info_unknown_provider():
    from fasthub_core.auth.social_providers import fetch_user_info

    with pytest.raises(ValueError, match="Unknown provider"):
        asyncio.get_event_loop().run_until_complete(
            fetch_user_info("facebook", "token")
        )


# ============================================================================
# 11. Provider-specific config details
# ============================================================================

def test_google_config_has_consent_prompt():
    from fasthub_core.auth.social_providers import PROVIDER_CONFIGS
    assert PROVIDER_CONFIGS["google"]["extra_params"]["prompt"] == "consent"


def test_github_config_no_pkce():
    from fasthub_core.auth.social_providers import PROVIDER_CONFIGS
    assert PROVIDER_CONFIGS["github"]["pkce_enabled"] == False


def test_microsoft_config_has_pkce():
    from fasthub_core.auth.social_providers import PROVIDER_CONFIGS
    assert PROVIDER_CONFIGS["microsoft"]["pkce_enabled"] == True
