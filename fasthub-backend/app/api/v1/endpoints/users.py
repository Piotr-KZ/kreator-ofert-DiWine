"""
Users management endpoints
API routes for user operations
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_superuser
from app.db.session import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.audit_service import AuditService
from sqlalchemy import select, func
from fastapi import Request


async def get_user_primary_org_id(user: User, db: AsyncSession) -> UUID:
    """Get user's primary organization ID (first membership)"""
    result = await db.execute(
        select(Member.organization_id)
        .where(Member.user_id == user.id)
        .order_by(Member.joined_at)
        .limit(1)
    )
    org_id = result.scalar_one_or_none()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no organization"
        )
    return org_id
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile

    Returns authenticated user's profile data.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile

    Allows authenticated users to update their own profile (full_name, email).
    Cannot change is_active or other admin fields.
    """
    user_service = UserService(db)
    
    # Users can only update their own profile
    user = await user_service.update_user(current_user.id, user_update, current_user)
    
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = Query(""),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users (system-wide for SuperAdmin)

    Returns list of ALL users in the system with pagination.
    Requires SuperAdmin authentication.
    """
    # Calculate skip from page
    skip = (page - 1) * per_page
    
    # SuperAdmin sees ALL users from ALL organizations
    query = select(User)
    
    # Apply search filter if provided
    if search:
        query = query.where(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()
    
    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(per_page)
    )
    users = result.scalars().all()
    
    return {
        "items": [UserResponse.model_validate(user) for user in users],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID

    Returns user details if user is in the same organization.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if user is in same organization
    if await get_user_primary_org_id(user, db) != await get_user_primary_org_id(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not in your organization"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user

    Users can update their own profile.
    Admins can update any user in their organization.
    Only admins can change roles and status.
    """
    user_service = UserService(db)
    
    # Get user before update (for audit log)
    result = await db.execute(select(User).where(User.id == user_id))
    user_before = result.scalar_one_or_none()
    
    user = await user_service.update_user(user_id, user_update, current_user)
    
    # Create audit log if SuperAdmin updated someone
    if current_user.is_superuser and user_before:
        changes = {}
        if user_update.full_name and user_update.full_name != user_before.full_name:
            changes["full_name"] = {"old": user_before.full_name, "new": user_update.full_name}
        if user_update.email and user_update.email != user_before.email:
            changes["email"] = {"old": user_before.email, "new": user_update.email}
        if user_update.is_active is not None and user_update.is_active != user_before.is_active:
            changes["is_active"] = {"old": user_before.is_active, "new": user_update.is_active}
        
        if changes:  # Only log if something actually changed
            audit_service = AuditService(db)
            await audit_service.log_action(
                user=current_user,
                action="user.update",
                resource_type="user",
                resource_id=user_id,
                extra_data=changes,
                request=request,
            )
    
    await db.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user

    Only admins can delete users.
    Cannot delete yourself.
    """
    user_service = UserService(db)
    
    # Get user details before deletion (for audit log)
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user_to_delete = result.scalar_one_or_none()
    
    if user_to_delete:
        # Create audit log
        audit_service = AuditService(db)
        await audit_service.log_action(
            user=current_user,
            action="user.delete",
            resource_type="user",
            resource_id=user_id,
            extra_data={
                "email": user_to_delete.email,
                "full_name": user_to_delete.full_name,
                "is_superuser": user_to_delete.is_superuser,
            },
            request=request,
        )
    
    await user_service.delete_user(user_id, current_user)
    await db.commit()
    return None
