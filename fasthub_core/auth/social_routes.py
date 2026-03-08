"""
Social Login API endpoints — Google, GitHub, Microsoft.

Flow:
    GET  /auth/{provider}/login    → redirect do providera OAuth
    GET  /auth/{provider}/callback → callback z providera → JWT tokeny

Prefix: /api/auth (dodawany przez router)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.auth.social_login import get_social_login_service
from fasthub_core.auth.social_providers import SUPPORTED_PROVIDERS
from fasthub_core.config import get_settings
from fasthub_core.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Social Login"])


@router.get("/{provider}/login")
async def social_login(provider: str):
    """
    Rozpocznij logowanie przez providera OAuth.

    Redirect usera na stronę logowania Google/GitHub/Microsoft.
    Po zalogowaniu provider przekieruje na /auth/{provider}/callback.
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider}. Supported: {SUPPORTED_PROVIDERS}",
        )

    service = get_social_login_service()

    try:
        url, state = await service.get_login_url(provider)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse(url=url, status_code=302)


@router.get("/{provider}/callback")
async def social_callback(
    provider: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="CSRF state parameter"),
    error: Optional[str] = Query(None, description="Error from OAuth provider"),
    db: AsyncSession = Depends(get_db),
):
    """
    Callback z providera OAuth.

    Provider przekierowuje tutaj po zalogowaniu.
    Wymienia code na token, pobiera dane usera, generuje JWT.

    W trybie development: zwraca JSON z tokenami.
    W trybie production: redirect na frontend z tokenami w query params.
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider}",
        )

    # Obsługa błędu z providera (np. user odmówił dostępu)
    if error:
        settings = get_settings()
        frontend_url = settings.FRONTEND_URL
        return RedirectResponse(
            url=f"{frontend_url}/auth/error?error={error}&provider={provider}",
            status_code=302,
        )

    service = get_social_login_service()

    try:
        tokens = await service.handle_callback(provider, code, state, db)
    except ValueError as e:
        logger.warning(f"Social login failed: provider={provider}, error={e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Social login error: provider={provider}, error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Social login failed")

    settings = get_settings()

    # Production: redirect na frontend z tokenami
    if settings.ENVIRONMENT == "production":
        frontend_url = settings.FRONTEND_URL
        return RedirectResponse(
            url=(
                f"{frontend_url}/auth/callback"
                f"?access_token={tokens['access_token']}"
                f"&refresh_token={tokens['refresh_token']}"
                f"&is_new_user={tokens['is_new_user']}"
            ),
            status_code=302,
        )

    # Development: zwróć JSON (łatwiej do testowania)
    return tokens
