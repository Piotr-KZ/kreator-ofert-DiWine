"""
Social Login Providers — gotowe konfiguracje OAuth dla Google, GitHub, Microsoft.

Użycie:
    from fasthub_core.auth.social_providers import get_provider_config, SUPPORTED_PROVIDERS

    config = get_provider_config("google")
    # → OAuthConfig z URL-ami, scopes, PKCE settings

Dodawanie nowego providera:
    1. Dodaj PROVIDER_CONFIGS["myprovider"] = { ... }
    2. Dodaj USERINFO_URLS["myprovider"] = "https://..."
    3. Dodaj parser w _parse_userinfo()
    4. Dodaj pola w User model (myprovider_id)
    5. Dodaj zmienne w config.py (MYPROVIDER_CLIENT_ID, MYPROVIDER_CLIENT_SECRET)
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from fasthub_core.integrations.oauth import OAuthConfig

logger = logging.getLogger(__name__)


# Konfiguracje providerów (URL-e, scopes)
PROVIDER_CONFIGS: Dict[str, dict] = {
    "google": {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["openid", "email", "profile"],
        "pkce_enabled": False,
        "extra_params": {"prompt": "consent"},
    },
    "github": {
        "authorization_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": ["user:email", "read:user"],
        "pkce_enabled": False,
        "extra_params": {},
    },
    "microsoft": {
        "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scopes": ["openid", "email", "profile", "User.Read"],
        "pkce_enabled": True,
        "extra_params": {},
    },
}

# URL-e do pobrania danych użytkownika po zalogowaniu
USERINFO_URLS: Dict[str, str] = {
    "google": "https://www.googleapis.com/oauth2/v2/userinfo",
    "github": "https://api.github.com/user",
    "microsoft": "https://graph.microsoft.com/v1.0/me",
}

# URL do pobrania emaili z GitHub (osobny endpoint)
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

SUPPORTED_PROVIDERS = list(PROVIDER_CONFIGS.keys())


@dataclass
class SocialUserInfo:
    """Dane użytkownika pobrane z providera OAuth."""
    provider: str
    external_id: str
    email: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str] = None


def get_provider_config(
    provider: str,
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = None,
) -> OAuthConfig:
    """
    Zbuduj OAuthConfig dla danego providera.

    Args:
        provider: "google", "github", "microsoft"
        client_id: OAuth Client ID (lub z config)
        client_secret: OAuth Client Secret (lub z config)
        redirect_uri: Callback URL (lub z config)

    Returns:
        OAuthConfig gotowy do użycia z OAuthManager
    """
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(f"Unknown provider: {provider}. Supported: {SUPPORTED_PROVIDERS}")

    # Pobierz credentials z config jeśli nie podano
    if not client_id or not client_secret:
        from fasthub_core.config import get_settings
        settings = get_settings()

        if provider == "google":
            client_id = client_id or settings.GOOGLE_CLIENT_ID
            client_secret = client_secret or settings.GOOGLE_CLIENT_SECRET
            redirect_uri = redirect_uri or getattr(settings, "GOOGLE_REDIRECT_URI", None)
        elif provider == "github":
            client_id = client_id or getattr(settings, "GITHUB_CLIENT_ID", None)
            client_secret = client_secret or getattr(settings, "GITHUB_CLIENT_SECRET", None)
            redirect_uri = redirect_uri or getattr(settings, "GITHUB_REDIRECT_URI", None)
        elif provider == "microsoft":
            client_id = client_id or getattr(settings, "MICROSOFT_CLIENT_ID", None)
            client_secret = client_secret or getattr(settings, "MICROSOFT_CLIENT_SECRET", None)
            redirect_uri = redirect_uri or getattr(settings, "MICROSOFT_REDIRECT_URI", None)

    if not client_id or not client_secret:
        raise ValueError(f"Missing credentials for {provider}. Set {provider.upper()}_CLIENT_ID and {provider.upper()}_CLIENT_SECRET.")

    # Domyślny redirect_uri
    if not redirect_uri:
        from fasthub_core.config import get_settings
        settings = get_settings()
        backend_url = getattr(settings, "BACKEND_URL", "http://localhost:8000")
        redirect_uri = f"{backend_url}/api/v1/auth/{provider}/callback"

    provider_config = PROVIDER_CONFIGS[provider]

    return OAuthConfig(
        provider=provider,
        client_id=client_id,
        client_secret=client_secret,
        authorization_url=provider_config["authorization_url"],
        token_url=provider_config["token_url"],
        scopes=provider_config["scopes"],
        redirect_uri=redirect_uri,
        pkce_enabled=provider_config["pkce_enabled"],
        extra_params=provider_config["extra_params"],
    )


async def fetch_user_info(provider: str, access_token: str) -> SocialUserInfo:
    """
    Pobierz dane użytkownika z providera OAuth.

    Args:
        provider: "google", "github", "microsoft"
        access_token: OAuth access token

    Returns:
        SocialUserInfo z email, name, avatar
    """
    import httpx

    if provider not in USERINFO_URLS:
        raise ValueError(f"Unknown provider: {provider}")

    url = USERINFO_URLS[provider]
    headers = {"Authorization": f"Bearer {access_token}"}

    # GitHub wymaga Accept header
    if provider == "github":
        headers["Accept"] = "application/vnd.github+json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # GitHub nie zawsze zwraca email w /user — trzeba pobrać z /user/emails
        if provider == "github" and not data.get("email"):
            emails_resp = await client.get(GITHUB_EMAILS_URL, headers=headers)
            if emails_resp.status_code == 200:
                emails = emails_resp.json()
                primary = next((e for e in emails if e.get("primary")), None)
                if primary:
                    data["email"] = primary["email"]

    return _parse_userinfo(provider, data)


def _parse_userinfo(provider: str, data: dict) -> SocialUserInfo:
    """Parsuj odpowiedź providera do SocialUserInfo."""

    if provider == "google":
        return SocialUserInfo(
            provider="google",
            external_id=str(data.get("id", "")),
            email=data.get("email"),
            full_name=data.get("name"),
            avatar_url=data.get("picture"),
        )

    elif provider == "github":
        return SocialUserInfo(
            provider="github",
            external_id=str(data.get("id", "")),
            email=data.get("email"),
            full_name=data.get("name") or data.get("login"),
            avatar_url=data.get("avatar_url"),
        )

    elif provider == "microsoft":
        return SocialUserInfo(
            provider="microsoft",
            external_id=str(data.get("id", "")),
            email=data.get("mail") or data.get("userPrincipalName"),
            full_name=data.get("displayName"),
            avatar_url=None,  # Microsoft Graph wymaga osobnego requesta na avatar
        )

    raise ValueError(f"Unknown provider: {provider}")
