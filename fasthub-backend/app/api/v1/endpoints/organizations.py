"""
Organizations management endpoints
API routes for organization operations
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_active_user,
    get_current_organization,
    require_organization_owner,
)
from app.db.session import get_db
from app.models.member import Member, MemberRole
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationComplete, OrganizationCreate, OrganizationResponse, OrganizationUpdate, OrganizationWithStats
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create organization for current user

    User becomes the owner and first admin member of the new organization.
    """
    org_service = OrganizationService(db)
    org = await org_service.create_organization(
        name=org_data.name,
        owner_id=current_user.id,
    )
    
    # Create owner membership as admin (legacy system)
    owner_member = Member(
        user_id=current_user.id,
        organization_id=org.id,
        role=MemberRole.ADMIN,
    )
    db.add(owner_member)
    await db.flush()

    # RBAC: create system roles and assign Owner to creator
    try:
        from fasthub_core.rbac.service import RBACService
        from fasthub_core.rbac.models import Role
        from sqlalchemy import select

        rbac = RBACService(db)
        await rbac.seed_organization_roles(org.id)
        owner_role_result = await db.execute(
            select(Role).where(
                Role.organization_id == org.id,
                Role.name == "Owner",
                Role.is_system == True,
            )
        )
        owner_role = owner_role_result.scalar_one_or_none()
        if owner_role:
            await rbac.assign_role(
                user_id=current_user.id,
                role_id=owner_role.id,
                organization_id=org.id,
            )
    except Exception:
        pass  # RBAC failure should not block org creation

    await db.commit()
    await db.refresh(org)

    return org


@router.get("/me", response_model=OrganizationWithStats)
async def get_current_organization(
    current_user: User = Depends(get_current_active_user),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's organization with statistics

    Returns organization details including user count and subscription status.
    """
    org_service = OrganizationService(db)
    return await org_service.get_organization_with_stats(organization.id)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get organization by ID

    Only accessible if user is member of the organization.
    """
    # Check if user is member
    from sqlalchemy import select
    result = await db.execute(
        select(Member).where(
            Member.user_id == current_user.id,
            Member.organization_id == org_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this organization"
        )

    org_service = OrganizationService(db)
    org = await org_service.get_organization_by_id(org_id)

    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return org


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_update: OrganizationUpdate,
    current_user: User = Depends(require_organization_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization

    Only organization owner can update organization details.
    """
    org_service = OrganizationService(db)
    org = await org_service.update_organization(org_id, org_update, current_user)
    await db.commit()
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: UUID,
    current_user: User = Depends(require_organization_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete organization

    Only organization owner can delete organization.
    This will also delete all users and data associated with the organization.
    """
    org_service = OrganizationService(db)
    await org_service.delete_organization(org_id, current_user)
    await db.commit()
    return None


@router.patch("/{org_id}/complete", response_model=OrganizationResponse)
async def complete_organization(
    org_id: UUID,
    org_data: OrganizationComplete,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete organization onboarding

    Updates organization with billing details and marks as complete.
    Only organization members can complete their organization.
    """
    # Check if user is member
    from sqlalchemy import select
    result = await db.execute(
        select(Member).where(
            Member.user_id == current_user.id,
            Member.organization_id == org_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this organization"
        )

    org_service = OrganizationService(db)
    org = await org_service.complete_organization(org_id, org_data)
    await db.commit()
    return org


@router.post("/{org_id}/transfer-ownership", response_model=OrganizationResponse)
async def transfer_ownership(
    org_id: UUID,
    new_owner_id: int,
    current_user: User = Depends(require_organization_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Transfer organization ownership

    Only current owner can transfer ownership to another member.
    New owner must be a member of the organization.
    """
    org_service = OrganizationService(db)
    org = await org_service.transfer_ownership(org_id, new_owner_id, current_user)
    await db.commit()
    return org


from pydantic import BaseModel, EmailStr

class InviteMemberRequest(BaseModel):
    """Schema for inviting member by email"""
    email: EmailStr
    role: str = "viewer"


@router.post("/invite")
async def invite_member(
    request: InviteMemberRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite user to organization by email
    
    If user exists and has no organization, adds them immediately.
    If user doesn't exist, returns success (invitation email would be sent in production).
    """
    from app.services.user_service import UserService
    from sqlalchemy import select
    
    # Get current user's organization
    org = current_user.organization
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )
    
    # Check permissions - only owner or admin can invite
    result = await db.execute(
        select(Member).where(
            Member.user_id == current_user.id,
            Member.organization_id == org.id
        )
    )
    current_member = result.scalar_one_or_none()
    
    if not current_member or current_member.role not in [MemberRole.ADMIN]:
        # Also allow owner
        if org.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owners and admins can invite members"
            )
    
    # Validate role
    valid_roles = ["viewer", "admin"]
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if user already exists
    user_service = UserService(db)
    existing_user = await user_service.get_by_email(request.email)
    
    if existing_user:
        # User exists - check if already in org
        if existing_user.organization_id == org.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )
        
        # User exists but in different org - can't invite
        if existing_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User belongs to another organization"
            )
        
        # User exists, no org - add to org
        existing_user.organization_id = org.id
        
        # Create member record
        member_role = MemberRole.ADMIN if request.role == "admin" else MemberRole.VIEWER
        new_member = Member(
            user_id=existing_user.id,
            organization_id=org.id,
            role=member_role,
        )
        db.add(new_member)
        await db.commit()
        
        return {
            "message": "User added to organization successfully",
            "user_id": str(existing_user.id),
            "email": existing_user.email,
            "role": request.role,
        }
    
    else:
        # User doesn't exist - in production would send invitation email
        # For now just return success
        return {
            "message": "Invitation sent successfully (user will need to sign up first)",
            "email": request.email,
            "role": request.role,
        }
