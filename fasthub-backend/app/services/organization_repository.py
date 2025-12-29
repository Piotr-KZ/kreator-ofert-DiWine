"""
Organization repository
Database operations for organizations
"""

import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


class OrganizationRepository:
    """Repository for organization database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        result = await self.db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        result = await self.db.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, name: str, owner_id: int, slug: Optional[str] = None) -> Organization:
        """Create new organization"""
        # Generate slug if not provided
        if not slug:
            slug = self._generate_slug(name)

        # Ensure slug is unique
        slug = await self._ensure_unique_slug(slug)

        organization = Organization(name=name, slug=slug, owner_id=owner_id)

        self.db.add(organization)
        await self.db.flush()
        await self.db.refresh(organization)
        return organization

    async def update(self, organization: Organization) -> Organization:
        """Update organization"""
        self.db.add(organization)
        await self.db.flush()
        await self.db.refresh(organization)
        return organization

    async def delete(self, organization: Organization) -> None:
        """Delete organization"""
        await self.db.delete(organization)
        await self.db.flush()

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from organization name"""
        # Convert to lowercase
        slug = name.lower()

        # Replace spaces and special characters with hyphens
        slug = re.sub(r"[^a-z0-9]+", "-", slug)

        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        return slug

    async def _ensure_unique_slug(self, slug: str) -> str:
        """Ensure slug is unique by appending number if needed"""
        original_slug = slug
        counter = 1

        while await self.get_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug
