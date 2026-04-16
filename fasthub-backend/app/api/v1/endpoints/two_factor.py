"""
2FA TOTP endpoints — setup, verify, authenticate, disable, regenerate backup codes.
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.security import (
    create_2fa_temp_token,
    create_access_token,
    create_refresh_token,
    decode_2fa_temp_token,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse

router = APIRouter()


# === Schemas ===

class Setup2FARequest(BaseModel):
    password: str


class Setup2FAResponse(BaseModel):
    qr_code: str
    provisioning_uri: str
    backup_codes: List[str]
    message: str = "Zeskanuj QR code i wpisz kod z aplikacji"


class Verify2FARequest(BaseModel):
    code: str


class Authenticate2FARequest(BaseModel):
    temp_token: str
    code: str


class Disable2FARequest(BaseModel):
    password: str
    code: str


class RegenerateBackupRequest(BaseModel):
    password: str
    code: str


class RegenerateBackupResponse(BaseModel):
    backup_codes: List[str]


# === Encryption helpers ===

def _encrypt(value: str) -> str:
    try:
        from fasthub_core.security.encryption import encrypt_credentials
        return encrypt_credentials({"v": value})
    except Exception:
        return value


def _decrypt(value: str) -> str:
    try:
        from fasthub_core.security.encryption import decrypt_credentials
        result = decrypt_credentials(value)
        if isinstance(result, dict):
            return result.get("v", "")
        return str(result)
    except Exception:
        return value


# === Endpoints ===

@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_2fa(
    body: Setup2FARequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Setup 2FA — generates QR code and backup codes."""
    if current_user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA jest już włączone")

    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Nieprawidłowe hasło")

    from fasthub_core.auth.totp import TOTPService

    totp = TOTPService(issuer_name=getattr(settings, "TOTP_ISSUER_NAME", "WebCreator"))
    secret = totp.generate_secret()
    uri = totp.generate_provisioning_uri(secret, current_user.email)
    qr_code = totp.generate_qr_code_base64(uri)
    backup_codes = totp.generate_backup_codes()

    # Encrypt and save (NOT enabled yet — user must verify)
    current_user.totp_secret = _encrypt(secret)
    current_user.backup_codes = _encrypt(json.dumps(backup_codes))
    current_user.totp_enabled = False
    db.add(current_user)
    await db.commit()

    return Setup2FAResponse(
        qr_code=qr_code,
        provisioning_uri=uri,
        backup_codes=backup_codes,
    )


@router.post("/2fa/verify")
async def verify_2fa(
    body: Verify2FARequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify TOTP code to activate 2FA."""
    if current_user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA jest już włączone")

    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="Najpierw wykonaj /auth/2fa/setup")

    from fasthub_core.auth.totp import TOTPService

    totp = TOTPService()
    secret = _decrypt(current_user.totp_secret)

    if not totp.verify_code(secret, body.code):
        raise HTTPException(status_code=400, detail="Nieprawidłowy kod")

    current_user.totp_enabled = True
    current_user.totp_verified_at = datetime.utcnow()
    db.add(current_user)
    await db.commit()

    return {"enabled": True, "message": "2FA zostało włączone"}


@router.post("/2fa/authenticate", response_model=TokenResponse)
async def authenticate_2fa(
    body: Authenticate2FARequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with TOTP code after login (requires temp_token)."""
    user_id = decode_2fa_temp_token(body.temp_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Nieprawidłowy lub wygasły token")

    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.totp_enabled:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    from fasthub_core.auth.totp import TOTPService

    totp = TOTPService()
    secret = _decrypt(user.totp_secret)
    authenticated = False

    # Try TOTP code first
    if totp.verify_code(secret, body.code):
        authenticated = True
    else:
        # Try backup code
        if user.backup_codes:
            decrypted_codes = _decrypt(user.backup_codes)
            valid, updated = totp.verify_backup_code(decrypted_codes, body.code)
            if valid:
                authenticated = True
                user.backup_codes = _encrypt(updated)

    if not authenticated:
        raise HTTPException(status_code=401, detail="Nieprawidłowy kod")

    # Issue full tokens
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    primary_org_id = await auth_service._get_user_primary_org_id(user.id)

    access_token = create_access_token(
        data={"sub": str(user.id), "org": str(primary_org_id) if primary_org_id else None}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    db.add(user)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/2fa/disable")
async def disable_2fa(
    body: Disable2FARequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Disable 2FA — requires password + TOTP code."""
    if not current_user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA nie jest włączone")

    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Nieprawidłowe hasło")

    from fasthub_core.auth.totp import TOTPService

    totp = TOTPService()
    secret = _decrypt(current_user.totp_secret)

    if not totp.verify_code(secret, body.code):
        raise HTTPException(status_code=400, detail="Nieprawidłowy kod TOTP")

    current_user.totp_enabled = False
    current_user.totp_secret = None
    current_user.totp_verified_at = None
    current_user.backup_codes = None
    db.add(current_user)
    await db.commit()

    return {"enabled": False, "message": "2FA zostało wyłączone"}


@router.post("/2fa/backup-codes/regenerate", response_model=RegenerateBackupResponse)
async def regenerate_backup_codes(
    body: RegenerateBackupRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate backup codes — requires password + TOTP code."""
    if not current_user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA nie jest włączone")

    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Nieprawidłowe hasło")

    from fasthub_core.auth.totp import TOTPService

    totp = TOTPService()
    secret = _decrypt(current_user.totp_secret)

    if not totp.verify_code(secret, body.code):
        raise HTTPException(status_code=400, detail="Nieprawidłowy kod TOTP")

    new_codes = totp.generate_backup_codes()
    current_user.backup_codes = _encrypt(json.dumps(new_codes))
    db.add(current_user)
    await db.commit()

    return RegenerateBackupResponse(backup_codes=new_codes)
