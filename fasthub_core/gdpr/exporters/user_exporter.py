"""Export user profile, organizations, and memberships."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fasthub_core.gdpr.export_registry import DataExporter


class UserExporter(DataExporter):

    async def get_export_name(self) -> str:
        return "user"

    async def export_user_data(self, user_id: UUID, db) -> Dict[str, Any]:
        from fasthub_core.users.models import User, Member, Organization

        result = await db.execute(
            select(User)
            .options(selectinload(User.memberships).selectinload(Member.organization))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return {}

        user_data = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_email_verified": user.is_email_verified,
            "email_verified_at": _dt(user.email_verified_at),
            "oauth_provider": user.oauth_provider,
            "avatar_url": user.avatar_url,
            "created_at": _dt(user.created_at),
            "updated_at": _dt(user.updated_at),
        }

        memberships = []
        organizations = []
        for m in user.memberships:
            memberships.append({
                "organization_id": str(m.organization_id),
                "role": m.role.value if m.role else None,
                "joined_at": _dt(m.joined_at),
            })
            org = m.organization
            if org:
                organizations.append({
                    "id": str(org.id),
                    "name": org.name,
                    "slug": org.slug,
                    "type": org.type,
                    "email": org.email,
                    "nip": org.nip,
                    "phone": org.phone,
                    "billing_street": org.billing_street,
                    "billing_city": org.billing_city,
                    "billing_postal_code": org.billing_postal_code,
                    "billing_country": org.billing_country,
                    "created_at": _dt(org.created_at),
                })

        return {
            "user": user_data,
            "memberships": memberships,
            "organizations": organizations,
        }


def _dt(val) -> str | None:
    return val.isoformat() if val else None
