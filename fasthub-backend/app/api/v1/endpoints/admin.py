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


@router.get("/organizations")
async def list_organizations(
    page: int = 1,
    per_page: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all organizations in the system
    
    **Super Admin only**
    
    Returns paginated list of all organizations with member counts.
    """
    from sqlalchemy import select, func
    from app.models.organization import Organization
    from app.models.member import Member
    from app.schemas.organization import OrganizationResponse
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = select(func.count(Organization.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Get organizations with member counts
    query = (
        select(
            Organization,
            func.count(Member.id).label('users_count')
        )
        .outerjoin(Member, Organization.id == Member.organization_id)
        .group_by(Organization.id)
        .order_by(Organization.created_at.desc())
        .limit(per_page)
        .offset(offset)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Build response
    items = []
    for org, users_count in rows:
        org_dict = {
            "id": str(org.id),
            "name": org.name,
            "slug": org.slug,
            "type": org.type,
            "owner_id": str(org.owner_id) if org.owner_id else None,
            "billing_street": org.billing_street,
            "billing_city": org.billing_city,
            "billing_postal_code": org.billing_postal_code,
            "billing_country": org.billing_country,
            "email": org.email,
            "phone": org.phone,
            "created_at": org.created_at.isoformat() if org.created_at else None,
            "updated_at": org.updated_at.isoformat() if org.updated_at else None,
            "users_count": users_count,
        }
        items.append(org_dict)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }
