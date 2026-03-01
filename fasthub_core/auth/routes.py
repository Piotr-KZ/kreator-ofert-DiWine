"""
API endpoints Auth — logout, email verification.
Prefix: /api/auth
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.db.session import get_db
from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.auth.service import decode_access_token
from fasthub_core.auth.blacklist import blacklist_token

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user),
):
    """
    Wyloguj — token trafia na blacklistę.
    Od tego momentu token nie jest akceptowany mimo że nie wygasł.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload:
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti:
            now = datetime.utcnow().timestamp()
            remaining = max(int(exp - now), 0) if exp else 1800
            await blacklist_token(jti, expires_in=remaining)

    return {"status": "logged_out"}


@router.get("/verify-email")
async def verify_email(
    token: str = Query(..., description="Token z emaila weryfikacyjnego"),
    db: AsyncSession = Depends(get_db),
):
    """Weryfikuj email — user klika link z emaila"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    from fasthub_core.config import get_settings

    settings = get_settings()
    service = EmailVerificationService(
        db=db,
        secret_key=settings.SECRET_KEY,
        base_url=getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
    )
    result = await service.verify_email(token)

    if result["status"] == "verified":
        return {"message": "Email zweryfikowany pomyślnie", "email": result["email"]}
    elif result["status"] == "already_verified":
        return {"message": "Email był już wcześniej zweryfikowany"}
    elif result["status"] == "invalid_token":
        raise HTTPException(status_code=400, detail="Token nieważny lub wygasły")
    elif result["status"] == "user_not_found":
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")


@router.post("/resend-verification")
async def resend_verification(
    email: str = Query(..., description="Email do wysłania weryfikacji"),
    db: AsyncSession = Depends(get_db),
):
    """Wyślij ponownie email weryfikacyjny"""
    from fasthub_core.auth.email_verification import EmailVerificationService
    from fasthub_core.config import get_settings

    settings = get_settings()
    service = EmailVerificationService(
        db=db,
        secret_key=settings.SECRET_KEY,
        base_url=getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
    )
    url = await service.resend_verification(email)

    if url:
        # TODO: W przyszłości — wyślij email przez NotificationService
        logger.info(f"Verification URL: {url}")

    # ZAWSZE zwracaj OK — nie zdradzaj czy email istnieje w bazie (bezpieczeństwo)
    return {"message": "Jeśli konto z tym emailem istnieje, wyślemy link weryfikacyjny"}
