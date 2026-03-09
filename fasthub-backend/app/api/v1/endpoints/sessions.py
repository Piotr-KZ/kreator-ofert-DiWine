"""
Session management endpoints — list, revoke, revoke all.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


class SessionInfo(BaseModel):
    id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    last_active_at: Optional[str] = None
    created_at: Optional[str] = None
    is_current: bool = False


class SessionListResponse(BaseModel):
    sessions: List[SessionInfo]


class RevokeAllResponse(BaseModel):
    revoked_count: int


def _get_current_jti(request: Request) -> Optional[str]:
    """Extract JTI from the current request's access token."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    payload = decode_access_token(token)
    return payload.get("jti") if payload else None


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all active sessions for the current user."""
    from fasthub_core.auth.session_models import UserSession

    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == current_user.id, UserSession.is_active == True)
        .order_by(UserSession.last_active_at.desc())
    )
    sessions = result.scalars().all()

    current_jti = _get_current_jti(request)

    items = []
    for s in sessions:
        items.append(SessionInfo(
            id=str(s.id),
            device_name=s.device_name,
            device_type=s.device_type,
            browser=s.browser,
            os=s.os,
            ip_address=s.ip_address,
            last_active_at=s.last_active_at.isoformat() if s.last_active_at else None,
            created_at=s.created_at.isoformat() if s.created_at else None,
            is_current=(s.token_jti == current_jti) if current_jti else False,
        ))

    # Sort: current first
    items.sort(key=lambda x: (not x.is_current, x.last_active_at or ""), reverse=False)

    return SessionListResponse(sessions=items)


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a specific session (cannot revoke current)."""
    from fasthub_core.auth.session_models import UserSession

    result = await db.execute(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id,
            UserSession.is_active == True,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesja nie znaleziona")

    current_jti = _get_current_jti(request)
    if current_jti and session.token_jti == current_jti:
        raise HTTPException(status_code=400, detail="Nie można unieważnić bieżącej sesji. Użyj /auth/logout.")

    session.is_active = False
    session.revoked_at = datetime.utcnow()
    db.add(session)

    # Blacklist the refresh token JTI
    try:
        from fasthub_core.auth.blacklist import blacklist_token
        remaining = (session.expires_at - datetime.utcnow()).total_seconds() if session.expires_at else 86400
        await blacklist_token(session.token_jti, expires_in=int(max(remaining, 0)))
    except Exception:
        pass

    await db.commit()
    return {"message": "Sesja unieważniona"}


@router.delete("/sessions")
async def revoke_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke all sessions except the current one."""
    from fasthub_core.auth.session_models import UserSession

    current_jti = _get_current_jti(request)

    result = await db.execute(
        select(UserSession).where(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True,
        )
    )
    sessions = result.scalars().all()

    revoked = 0
    for s in sessions:
        if current_jti and s.token_jti == current_jti:
            continue
        s.is_active = False
        s.revoked_at = datetime.utcnow()
        db.add(s)
        revoked += 1

        try:
            from fasthub_core.auth.blacklist import blacklist_token
            remaining = (s.expires_at - datetime.utcnow()).total_seconds() if s.expires_at else 86400
            await blacklist_token(s.token_jti, expires_in=int(max(remaining, 0)))
        except Exception:
            pass

    await db.commit()
    return RevokeAllResponse(revoked_count=revoked)
