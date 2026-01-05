"""
Organization management service
Business logic for organization operations
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationComplete, OrganizationUpdate, OrganizationWithStats
from app.services.organization_repository import OrganizationRepository
from app.services.user_service import UserService


class OrganizationService:
    """Service for organization management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.user_service = UserService(db)

    async def create_organization(self, name: str, owner_id: UUID) -> Organization:
        """Create new organization"""
        return await self.org_repo.create(name=name, owner_id=owner_id)

    async def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        return await self.org_repo.get_by_id(org_id)

    async def get_organization_with_stats(self, org_id: int) -> OrganizationWithStats:
        """Get organization with statistics"""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Get user count
        user_count = await self.user_service.get_organization_user_count(org_id)

        # TODO: Get subscription status from Subscription model
        subscription_status = None

        return OrganizationWithStats(
            id=org.id,
            name=org.name,
            slug=org.slug,
            owner_id=org.owner_id,
            stripe_customer_id=org.stripe_customer_id,
            type=org.type,
            email=org.email,
            nip=org.nip,
            phone=org.phone,
            billing_street=org.billing_street,
            billing_city=org.billing_city,
            billing_postal_code=org.billing_postal_code,
            billing_country=org.billing_country,
            is_complete=org.is_complete,
            created_at=org.created_at,
            updated_at=org.updated_at,
            user_count=user_count,
            subscription_status=subscription_status,
        )

    async def update_organization(
        self, org_id: int, org_update: OrganizationUpdate, current_user: User
    ) -> Organization:
        """Update organization"""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Check if user is owner
        if org.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owner can update organization",
            )

        # Update fields
        if org_update.name is not None:
            org.name = org_update.name

        if org_update.slug is not None:
            # Check if slug already exists
            existing = await self.org_repo.get_by_slug(org_update.slug)
            if existing and existing.id != org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already in use"
                )
            org.slug = org_update.slug

        # Update billing fields
        if org_update.email is not None:
            org.email = org_update.email
        if org_update.phone is not None:
            org.phone = org_update.phone
        if org_update.nip is not None:
            org.nip = org_update.nip
        if org_update.billing_street is not None:
            org.billing_street = org_update.billing_street
        if org_update.billing_city is not None:
            org.billing_city = org_update.billing_city
        if org_update.billing_postal_code is not None:
            org.billing_postal_code = org_update.billing_postal_code
        if org_update.billing_country is not None:
            org.billing_country = org_update.billing_country

        return await self.org_repo.update(org)

    async def delete_organization(self, org_id: int, current_user: User) -> None:
        """Delete organization"""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Check if user is owner
        if org.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owner can delete organization",
            )

        # TODO: Check if organization has active subscriptions
        # TODO: Delete all users in organization

        await self.org_repo.delete(org)

    async def transfer_ownership(
        self, org_id: int, new_owner_id: UUID, current_user: User
    ) -> Organization:
        """Transfer organization ownership"""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Check if user is current owner
        if org.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owner can transfer ownership",
            )

        # Check if new owner exists and is in organization
        from app.services.user_repository import UserRepository

        user_repo = UserRepository(self.db)
        new_owner = await user_repo.get_by_id(new_owner_id)

        if not new_owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New owner not found")

        if new_owner.organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New owner must be a member of the organization",
            )

        # Transfer ownership
        org.owner_id = new_owner_id
        return await self.org_repo.update(org)

    async def complete_organization(
        self, org_id: int, org_data: OrganizationComplete
    ) -> Organization:
        """Complete organization onboarding with billing details"""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Update organization fields
        org.name = org_data.name
        org.type = org_data.type
        org.nip = org_data.nip
        org.phone = org_data.phone
        org.billing_street = org_data.billing_street
        org.billing_city = org_data.billing_city
        org.billing_postal_code = org_data.billing_postal_code
        org.billing_country = org_data.billing_country
        org.is_complete = True

        return await self.org_repo.update(org)
