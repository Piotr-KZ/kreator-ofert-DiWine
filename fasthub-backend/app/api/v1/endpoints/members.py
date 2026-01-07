"""
Members API endpoints
Handles team management: invite, list, remove, and update members
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import Member, MemberRole, Organization, User
from app.schemas.member import (
    MemberCreate,
    MemberListResponse,
    MemberResponse,
    MemberUpdate,
)

router = APIRouter(tags=["members"])


async def get_user_org_role(
    organization_id: UUID,
    current_user: User,
    db: AsyncSession,
) -> tuple[Organization, str]:
    """
    Get user's role in organization.
    Returns (organization, role) where role is 'owner', 'admin', or 'viewer'.
    Raises 403 if not a member.
    """
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if owner
    if org.owner_id == current_user.id:
        return (org, "owner")
    
    # Check membership
    result = await db.execute(
        select(Member).where(
            Member.organization_id == organization_id,
            Member.user_id == current_user.id,
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization",
        )
    
    return (org, member.role.value)


@router.post(
    "/organizations/{organization_id}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    organization_id: UUID,
    member_data: MemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite a new member to organization.
    Requires admin or owner role.
    """
    # Check permissions
    org, role = await get_user_org_role(organization_id, current_user, db)
    if role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can invite members",
        )
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == member_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {member_data.email} not found",
        )
    
    # Check if already a member
    result = await db.execute(
        select(Member).where(
            Member.user_id == user.id, Member.organization_id == organization_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization",
        )
    
    # Create membership
    new_member = Member(
        user_id=user.id,
        organization_id=organization_id,
        role=member_data.role,
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member, ["user"])
    
    return new_member


@router.get(
    "/organizations/{organization_id}/members",
    response_model=MemberListResponse,
)
async def list_members(
    organization_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    search: str = Query("", description="Search by name or email"),
    role: str = Query(None, description="Filter by role (admin/viewer)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all members of an organization with search and filter.
    Requires any membership (owner, admin, or viewer).
    Includes owner even if not in members table.
    
    Query parameters:
    - search: Search by name or email (case-insensitive)
    - role: Filter by role (admin/viewer)
    """
    # Check permissions (any member can view)
    await get_user_org_role(organization_id, current_user, db)
    
    # Get organization to check owner
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Build query for members with user details
    query = (
        select(Member)
        .where(Member.organization_id == organization_id)
        .options(selectinload(Member.user))
    )
    
    # Apply role filter if provided
    if role:
        try:
            role_enum = MemberRole(role.lower())
            query = query.where(Member.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Must be 'admin' or 'viewer'"
            )
    
    # Execute query
    result = await db.execute(query.order_by(Member.joined_at))
    members = list(result.scalars().all())
    
    # Apply search filter (in-memory, after loading user data)
    if search:
        search_lower = search.lower()
        members = [
            m for m in members
            if (m.user.full_name and search_lower in m.user.full_name.lower())
            or (m.user.email and search_lower in m.user.email.lower())
        ]
    
    # Check if owner is in members list
    owner_in_members = any(m.user_id == org.owner_id for m in members)
    
    # If owner not in members, add as virtual member (if matches filters)
    if not owner_in_members:
        # Get owner user
        result = await db.execute(
            select(User).where(User.id == org.owner_id)
        )
        owner_user = result.scalar_one_or_none()
        
        if owner_user:
            # Check if owner matches search filter
            matches_search = True
            if search:
                search_lower = search.lower()
                matches_search = (
                    (owner_user.full_name and search_lower in owner_user.full_name.lower())
                    or (owner_user.email and search_lower in owner_user.email.lower())
                )
            
            # Check if owner matches role filter (owner is treated as admin)
            matches_role = True
            if role and role.lower() != "admin":
                matches_role = False
            
            # Add owner if matches all filters
            if matches_search and matches_role:
                # Create virtual member object for owner
                virtual_member = Member(
                    id=0,  # Virtual ID
                    user_id=org.owner_id,
                    organization_id=organization_id,
                    role=MemberRole.ADMIN,  # Treat owner as admin
                    joined_at=org.created_at,
                )
                virtual_member.user = owner_user
                # Insert at beginning of list
                members.insert(0, virtual_member)
    
    # Apply pagination
    total = len(members)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_members = members[start:end]
    
    return MemberListResponse(members=paginated_members, total=total)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from organization.
    Requires admin or owner role.
    Cannot remove organization owner.
    """
    # Get member
    result = await db.execute(
        select(Member).where(Member.id == member_id).options(selectinload(Member.user))
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check permissions
    org, role = await get_user_org_role(member.organization_id, current_user, db)
    if role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can remove members",
        )
    
    # Get organization to check owner
    result = await db.execute(
        select(Organization).where(Organization.id == member.organization_id)
    )
    org = result.scalar_one()
    
    # Cannot remove owner
    if member.user_id == org.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove organization owner",
        )
    
    # Remove member
    await db.delete(member)
    await db.commit()
    
    return None


@router.patch("/members/{member_id}", response_model=MemberResponse)
async def update_member_role(
    member_id: int,
    member_update: MemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update member's role in organization.
    Requires admin or owner role.
    Cannot change owner's role.
    """
    # Get member
    result = await db.execute(
        select(Member).where(Member.id == member_id).options(selectinload(Member.user))
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check permissions
    org, role = await get_user_org_role(member.organization_id, current_user, db)
    if role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change member roles",
        )
    
    # Get organization to check owner
    result = await db.execute(
        select(Organization).where(Organization.id == member.organization_id)
    )
    org = result.scalar_one()
    
    # Cannot change owner's role
    if member.user_id == org.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change organization owner's role",
        )
    
    # Update role
    member.role = member_update.role
    await db.commit()
    await db.refresh(member, ["user"])
    
    return member
