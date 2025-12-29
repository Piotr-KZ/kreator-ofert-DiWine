"""
Admin endpoints
API routes for admin operations (admin-only)
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import BroadcastMessageRequest, BroadcastMessageResponse, SystemStatsResponse
from app.schemas.subscription import SubscriptionResponse
from app.schemas.user import UserResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.post("/broadcast", response_model=BroadcastMessageResponse)
async def broadcast_message(
    request: BroadcastMessageRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Broadcast message to all users or specific users

    **Admin only**

    Firebase equivalent: BroadcastMessageUseCase
    Sends notification to all active users or specific target users.
    """
    admin_service = AdminService(db)
    result = await admin_service.broadcast_message(
        title=request.title,
        message=request.message,
        target_user_ids=request.target_user_ids,
        url=request.url,
        emoji_icon=request.emoji_icon,
    )

    return result


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    Get system statistics

    **Admin only**

    Returns overview of:
    - Users (total, active, inactive)
    - Organizations
    - Subscriptions (total, active, inactive)
    - Invoices (total, paid, unpaid)
    """
    admin_service = AdminService(db)
    stats = await admin_service.get_system_stats()

    return stats


@router.get("/users/recent", response_model=List[UserResponse])
async def get_recent_users(
    limit: int = 10, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    Get recently registered users

    **Admin only**

    Returns list of most recently registered users.
    """
    admin_service = AdminService(db)
    users = await admin_service.get_recent_users(limit=limit)

    return users


@router.get("/subscriptions/recent", response_model=List[SubscriptionResponse])
async def get_recent_subscriptions(
    limit: int = 10, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    Get recently created subscriptions

    **Admin only**

    Returns list of most recently created subscriptions.
    """
    admin_service = AdminService(db)
    subscriptions = await admin_service.get_recent_subscriptions(limit=limit)

    return subscriptions
