"""
FastHub Core — OAuth Base.

Universal OAuth2 flow with PKCE support.
Provides base classes for any OAuth provider (Google, Microsoft, GitHub, etc.)

Usage:
    config = OAuthConfig(
        provider="google",
        client_id="...",
        client_secret="...",
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        scopes=["email", "profile"],
        redirect_uri="http://localhost:8000/callback",
    )
    manager = OAuthManager(config, MemoryTokenStorage())
    url, state = await manager.get_authorization_url()
"""

import base64
import hashlib
import logging
import os
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("fasthub.oauth")


# === DATA CLASSES ===


@dataclass
class OAuthConfig:
    """Configuration for an OAuth2 provider."""
    provider: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    scopes: List[str]
    redirect_uri: str
    pkce_enabled: bool = False
    extra_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class OAuthTokens:
    """OAuth2 tokens with expiry management."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if access token is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() >= self.expires_at

    def expires_in_seconds(self) -> Optional[int]:
        """Seconds until token expires (negative if expired)."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds())

    def should_refresh(self, buffer_seconds: int = 300) -> bool:
        """Check if token should be refreshed (within buffer of expiry)."""
        if self.expires_at is None:
            return False
        threshold = datetime.utcnow() + timedelta(seconds=buffer_seconds)
        return threshold >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "token_type": self.token_type,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthTokens":
        expires_at = None
        if data.get("expires_at"):
            if isinstance(data["expires_at"], str):
                expires_at = datetime.fromisoformat(data["expires_at"])
            elif isinstance(data["expires_at"], datetime):
                expires_at = data["expires_at"]
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope"),
        )


@dataclass
class OAuthState:
    """OAuth2 state for CSRF protection and PKCE."""
    state: str
    provider: str
    redirect_uri: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    code_verifier: Optional[str] = None  # PKCE


# === TOKEN STORAGE ===


class TokenStorage(ABC):
    """Abstract base for persisting OAuth tokens."""

    @abstractmethod
    async def save_tokens(self, provider: str, entity_id: str, tokens: OAuthTokens) -> None:
        ...

    @abstractmethod
    async def get_tokens(self, provider: str, entity_id: str) -> Optional[OAuthTokens]:
        ...

    @abstractmethod
    async def delete_tokens(self, provider: str, entity_id: str) -> None:
        ...


class MemoryTokenStorage(TokenStorage):
    """In-memory token storage — for testing and development."""

    def __init__(self):
        self._store: Dict[str, OAuthTokens] = {}

    def _key(self, provider: str, entity_id: str) -> str:
        return f"{provider}:{entity_id}"

    async def save_tokens(self, provider: str, entity_id: str, tokens: OAuthTokens) -> None:
        self._store[self._key(provider, entity_id)] = tokens

    async def get_tokens(self, provider: str, entity_id: str) -> Optional[OAuthTokens]:
        return self._store.get(self._key(provider, entity_id))

    async def delete_tokens(self, provider: str, entity_id: str) -> None:
        self._store.pop(self._key(provider, entity_id), None)


# === PKCE HELPERS ===


def _generate_code_verifier() -> str:
    """Generate PKCE code verifier (43-128 chars)."""
    return secrets.token_urlsafe(64)


def _generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge (S256)."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


# === OAUTH MANAGER ===


class OAuthManager:
    """
    Universal OAuth2 manager.
    Handles authorization URL generation, code exchange, and token refresh.
    """

    def __init__(self, config: OAuthConfig, storage: TokenStorage):
        self.config = config
        self.storage = storage
        self._pending_states: Dict[str, OAuthState] = {}

    async def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate authorization URL for redirect.
        Returns (url, state) tuple.
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "state": state,
            "access_type": "offline",
        }
        params.update(self.config.extra_params)

        code_verifier = None
        if self.config.pkce_enabled:
            code_verifier = _generate_code_verifier()
            code_challenge = _generate_code_challenge(code_verifier)
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        # Store state for verification
        oauth_state = OAuthState(
            state=state,
            provider=self.config.provider,
            redirect_uri=self.config.redirect_uri,
            code_verifier=code_verifier,
        )
        self._pending_states[state] = oauth_state

        # Build URL
        from urllib.parse import urlencode
        url = f"{self.config.authorization_url}?{urlencode(params)}"
        return url, state

    async def exchange_code(self, code: str, state: str) -> OAuthTokens:
        """
        Exchange authorization code for tokens.
        Validates state, sends token request to provider.
        """
        import httpx

        # Validate state
        oauth_state = self._pending_states.pop(state, None)
        if oauth_state is None:
            raise ValueError("Invalid or expired OAuth state")

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        if oauth_state.code_verifier:
            data["code_verifier"] = oauth_state.code_verifier

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.token_url,
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            token_data = response.json()

        expires_at = None
        if "expires_in" in token_data:
            expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

        tokens = OAuthTokens(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at,
            token_type=token_data.get("token_type", "Bearer"),
            scope=token_data.get("scope"),
        )

        logger.info(f"OAuth tokens obtained for provider: {self.config.provider}")
        return tokens

    async def refresh_tokens(self, tokens: OAuthTokens) -> OAuthTokens:
        """
        Refresh expired access token using refresh_token.
        """
        import httpx

        if not tokens.refresh_token:
            raise ValueError("No refresh token available")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": tokens.refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.token_url,
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            token_data = response.json()

        expires_at = None
        if "expires_in" in token_data:
            expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

        refreshed = OAuthTokens(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", tokens.refresh_token),
            expires_at=expires_at,
            token_type=token_data.get("token_type", "Bearer"),
            scope=token_data.get("scope", tokens.scope),
        )

        logger.info(f"OAuth tokens refreshed for provider: {self.config.provider}")
        return refreshed
