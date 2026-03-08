"""
AnonymizeService — GDPR Art. 17 data anonymization.

Replaces personal data with hashed placeholders instead of deleting records.
Preserves: invoices (5yr legal), audit trail (security), subscriptions (history).
"""

import hashlib
from uuid import UUID

from sqlalchemy import select, update


class AnonymizeService:
    """Replace personal data with anonymized placeholders."""

    def __init__(self, db):
        self.db = db

    async def anonymize_user(self, user_id: UUID) -> dict:
        """
        Full anonymization of a user's personal data.
        Returns summary of what was anonymized.
        """
        token = self._hash_token(str(user_id))
        anon_email = f"deleted_{token}@anonymized.local"
        anon_name = f"Deleted User {token}"
        summary = {}

        summary["user"] = await self._anonymize_user_record(user_id, anon_email, anon_name)
        summary["audit_logs"] = await self._anonymize_audit_logs(user_id, anon_email)
        summary["notifications"] = await self._anonymize_notifications(user_id)
        summary["organization"] = await self._handle_organization_ownership(user_id)

        await self.db.flush()
        return summary

    async def _anonymize_user_record(self, user_id: UUID, anon_email: str, anon_name: str) -> dict:
        from fasthub_core.users.models import User

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"status": "not_found"}

        user.email = anon_email
        user.full_name = anon_name
        user.hashed_password = "DELETED"
        user.is_active = False
        user.is_verified = False
        user.is_email_verified = False
        user.magic_link_token = None
        user.magic_link_expires = None
        user.google_id = None
        user.github_id = None
        user.microsoft_id = None
        user.oauth_provider = None
        user.avatar_url = None

        return {"status": "anonymized", "email": anon_email}

    async def _anonymize_audit_logs(self, user_id: UUID, anon_email: str) -> dict:
        from fasthub_core.audit.models import AuditLog

        result = await self.db.execute(
            update(AuditLog)
            .where(AuditLog.user_id == user_id)
            .values(user_email=anon_email, ip_address="0.0.0.0", user_agent=None)
        )
        return {"rows_updated": result.rowcount}

    async def _anonymize_notifications(self, user_id: UUID) -> dict:
        from fasthub_core.notifications.models import Notification

        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .values(title="[deleted]", message="[deleted]", link=None)
        )
        return {"rows_updated": result.rowcount}

    async def _handle_organization_ownership(self, user_id: UUID) -> dict:
        """
        Transfer ownership to next admin, or deactivate org if sole owner.
        """
        from fasthub_core.users.models import Organization, Member, MemberRole

        # Find orgs owned by this user
        result = await self.db.execute(
            select(Organization).where(Organization.owner_id == user_id)
        )
        orgs = result.scalars().all()
        summary = {"transferred": 0, "deactivated": 0}

        for org in orgs:
            # Find another admin in this org
            result = await self.db.execute(
                select(Member)
                .where(
                    Member.organization_id == org.id,
                    Member.user_id != user_id,
                    Member.role == MemberRole.ADMIN,
                )
                .limit(1)
            )
            next_admin = result.scalar_one_or_none()

            if next_admin:
                org.owner_id = next_admin.user_id
                summary["transferred"] += 1
            else:
                org.owner_id = None
                org.is_complete = False  # deactivate
                summary["deactivated"] += 1

        # Remove user's memberships
        from sqlalchemy import delete

        await self.db.execute(
            delete(Member).where(Member.user_id == user_id)
        )

        return summary

    @staticmethod
    def _hash_token(value: str) -> str:
        """Short hash for anonymized identifiers."""
        return hashlib.sha256(value.encode()).hexdigest()[:6]
