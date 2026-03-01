"""
API endpoints Notifications.
Prefix: /api/notifications
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.db.session import get_db
from fasthub_core.notifications.schemas import (
    NotificationList,
    PreferenceResponse,
    PreferenceUpdateRequest,
    UnreadCountResponse,
)
from fasthub_core.notifications.service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


# === POWIADOMIENIA ===

@router.get("", response_model=NotificationList)
async def get_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobierz powiadomienia zalogowanego usera"""
    notif = NotificationService(db)
    return await notif.get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        page=page,
        per_page=per_page,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liczba nieprzeczytanych powiadomien (dla badge w UI)"""
    notif = NotificationService(db)
    count = await notif.get_unread_count(current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Oznacz powiadomienie jako przeczytane"""
    notif = NotificationService(db)
    success = await notif.mark_as_read(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Powiadomienie nie znalezione")
    await db.commit()
    return {"status": "read"}


@router.post("/read-all")
async def mark_all_as_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Oznacz wszystkie powiadomienia jako przeczytane"""
    notif = NotificationService(db)
    count = await notif.mark_all_as_read(current_user.id)
    await db.commit()
    return {"status": "all_read", "count": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Usun powiadomienie"""
    notif = NotificationService(db)
    success = await notif.delete_notification(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Powiadomienie nie znalezione")
    await db.commit()
    return {"status": "deleted"}


# === PREFERENCJE ===

@router.get("/preferences", response_model=list[PreferenceResponse])
async def get_preferences(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pobierz preferencje powiadomien usera"""
    notif = NotificationService(db)
    return await notif.get_user_preferences(current_user.id)


@router.put("/preferences")
async def update_preference(
    request: PreferenceUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Zmien preferencje dla typu powiadomienia"""
    notif = NotificationService(db)
    result = await notif.update_preference(
        user_id=current_user.id,
        notification_type=request.notification_type,
        channel_inapp=request.channel_inapp,
        channel_email=request.channel_email,
    )
    await db.commit()
    return result
