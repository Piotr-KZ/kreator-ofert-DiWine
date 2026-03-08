"""
Social Login Service — logika logowania przez Google, GitHub, Microsoft.

Flow:
1. GET /auth/{provider}/login → redirect do providera (Google, GitHub, Microsoft)
2. User loguje się u providera
3. Provider redirectuje na /auth/{provider}/callback?code=xxx&state=yyy
4. Callback: wymiana code → token → pobranie danych usera → JWT

Logika user linking:
- Email z OAuth istnieje w DB? → link social ID do istniejącego konta
- Email nie istnieje? → stwórz nowe konto (bez hasła, is_email_verified=True)
- Social ID już połączony? → zaloguj bezpośrednio

Użycie:
    service = SocialLoginService()
    url, state = await service.get_login_url("google")
    # → redirect user to url

    jwt_tokens = await service.handle_callback("google", code, state, db)
    # → {"access_token": "...", "refresh_token": "..."}
"""

import logging
import secrets
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.auth.service import create_access_token, create_refresh_token
from fasthub_core.auth.social_providers import (
    SUPPORTED_PROVIDERS,
    SocialUserInfo,
    fetch_user_info,
    get_provider_config,
)
from fasthub_core.integrations.oauth import OAuthManager, MemoryTokenStorage

logger = logging.getLogger(__name__)

# Globalne instancje OAuthManager (per provider) — trzymają pending states
_oauth_managers: Dict[str, OAuthManager] = {}


def _get_oauth_manager(provider: str) -> OAuthManager:
    """Pobierz lub stwórz OAuthManager dla providera."""
    if provider not in _oauth_managers:
        config = get_provider_config(provider)
        _oauth_managers[provider] = OAuthManager(config, MemoryTokenStorage())
    return _oauth_managers[provider]


def reset_oauth_managers():
    """Reset managerów (dla testów)."""
    _oauth_managers.clear()


class SocialLoginService:
    """
    Serwis social login — obsługuje cały flow OAuth → JWT.
    """

    async def get_login_url(self, provider: str) -> Tuple[str, str]:
        """
        Generuj URL do logowania przez providera.

        Args:
            provider: "google", "github", "microsoft"

        Returns:
            (authorization_url, state) — redirect usera na authorization_url
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}. Supported: {SUPPORTED_PROVIDERS}")

        manager = _get_oauth_manager(provider)
        url, state = await manager.get_authorization_url()
        logger.info(f"Social login initiated: provider={provider}")
        return url, state

    async def handle_callback(
        self,
        provider: str,
        code: str,
        state: str,
        db: AsyncSession,
    ) -> Dict[str, str]:
        """
        Obsłuż callback z providera OAuth.

        Args:
            provider: "google", "github", "microsoft"
            code: Authorization code z callback URL
            state: State z callback URL (weryfikacja CSRF)
            db: Sesja bazy danych

        Returns:
            {"access_token": "...", "refresh_token": "...", "token_type": "bearer", "is_new_user": True/False}
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        manager = _get_oauth_manager(provider)

        # 1. Wymień code na token
        tokens = await manager.exchange_code(code, state)

        # 2. Pobierz dane usera z providera
        user_info = await fetch_user_info(provider, tokens.access_token)

        if not user_info.email:
            raise ValueError(f"OAuth provider {provider} did not return email address")

        # 3. Znajdź lub stwórz usera
        user, is_new = await self._find_or_create_user(db, user_info)

        # 4. Generuj JWT
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        logger.info(f"Social login success: provider={provider}, email={user_info.email}, new_user={is_new}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "is_new_user": is_new,
        }

    async def _find_or_create_user(
        self,
        db: AsyncSession,
        user_info: SocialUserInfo,
    ) -> Tuple["User", bool]:
        """
        Znajdź istniejącego usera lub stwórz nowego.

        Logika:
        1. Szukaj po social ID (google_id, github_id, microsoft_id) → zaloguj
        2. Szukaj po email → link social ID do istniejącego konta
        3. Brak → stwórz nowe konto (bez hasła)
        """
        from fasthub_core.users.models import User, Organization

        provider_id_field = f"{user_info.provider}_id"

        # 1. Szukaj po social ID
        stmt = select(User).where(
            getattr(User, provider_id_field) == user_info.external_id
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update avatar jeśli się zmieniło
            if user_info.avatar_url and user.avatar_url != user_info.avatar_url:
                user.avatar_url = user_info.avatar_url
                await db.flush()
            return user, False

        # 2. Szukaj po email
        stmt = select(User).where(User.email == user_info.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Link social ID do istniejącego konta
            setattr(user, provider_id_field, user_info.external_id)
            if user_info.avatar_url and not user.avatar_url:
                user.avatar_url = user_info.avatar_url
            if not user.is_email_verified:
                user.is_email_verified = True
            await db.flush()
            logger.info(f"Linked {user_info.provider} to existing user: {user.email}")
            return user, False

        # 3. Stwórz nowe konto
        user = User(
            email=user_info.email,
            hashed_password="",  # Brak hasła — social login only
            full_name=user_info.full_name or "",
            is_active=True,
            is_verified=True,
            is_email_verified=True,  # Email zweryfikowany przez providera
            avatar_url=user_info.avatar_url,
            oauth_provider=user_info.provider,
        )
        setattr(user, provider_id_field, user_info.external_id)
        db.add(user)
        await db.flush()

        # Stwórz domyślną organizację
        slug = user_info.email.split("@")[0].lower().replace(".", "-")[:50]
        # Dodaj random suffix żeby uniknąć kolizji
        slug = f"{slug}-{secrets.token_hex(3)}"

        org = Organization(
            name=f"{user_info.full_name or user_info.email.split('@')[0]}'s Organization",
            slug=slug,
            owner_id=user.id,
            is_complete=False,
        )
        db.add(org)
        await db.commit()

        logger.info(f"New user created via {user_info.provider}: {user.email}")
        return user, True


# Singleton
_social_login_service = None


def get_social_login_service() -> SocialLoginService:
    """Pobierz singleton SocialLoginService."""
    global _social_login_service
    if _social_login_service is None:
        _social_login_service = SocialLoginService()
    return _social_login_service
