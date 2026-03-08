"""
InvitationService — create, accept, cancel, resend, cleanup.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy import select, update

from fasthub_core.invitations.models import Invitation, InvitationStatus

logger = logging.getLogger(__name__)


class InvitationService:
    def __init__(self, db):
        self.db = db

    async def create_invitation(
        self,
        email: str,
        organization_id: UUID,
        role: str,
        invited_by: UUID,
    ) -> Invitation:
        """Create invitation + send email."""
        from fasthub_core.config import get_settings
        settings = get_settings()
        expire_days = getattr(settings, "INVITATION_EXPIRE_DAYS", 7)
        max_pending = getattr(settings, "INVITATION_MAX_PENDING", 50)

        # Check max pending per org
        result = await self.db.execute(
            select(Invitation).where(
                Invitation.organization_id == organization_id,
                Invitation.status == InvitationStatus.pending,
            )
        )
        pending = result.scalars().all()
        if len(pending) >= max_pending:
            raise ValueError(f"Max {max_pending} pending invitations per organization")

        # Check duplicate
        existing = [i for i in pending if i.email == email]
        if existing:
            return existing[0]

        token = secrets.token_urlsafe(48)
        invitation = Invitation(
            email=email,
            token=token,
            organization_id=organization_id,
            role=role,
            invited_by=invited_by,
            status=InvitationStatus.pending,
            expires_at=datetime.utcnow() + timedelta(days=expire_days),
        )
        self.db.add(invitation)
        await self.db.flush()

        # Send invitation email
        await self._send_invitation_email(invitation)

        return invitation

    async def accept_invitation(self, token: str, user_id: UUID) -> Dict:
        """Accept invitation — add user to organization as member."""
        invitation = await self._get_by_token(token)
        if not invitation:
            raise ValueError("Invalid invitation token")

        if invitation.status != InvitationStatus.pending:
            raise ValueError(f"Invitation is {invitation.status.value}")

        if datetime.utcnow() > invitation.expires_at:
            invitation.status = InvitationStatus.expired
            await self.db.flush()
            raise ValueError("Invitation expired")

        # Add member
        from fasthub_core.users.models import Member

        member = Member(
            user_id=user_id,
            organization_id=invitation.organization_id,
            role=invitation.role,
        )
        self.db.add(member)

        invitation.status = InvitationStatus.accepted
        invitation.accepted_at = datetime.utcnow()
        invitation.accepted_user_id = user_id
        await self.db.flush()

        return {
            "organization_id": str(invitation.organization_id),
            "role": invitation.role,
        }

    async def cancel_invitation(self, invitation_id: UUID) -> bool:
        """Cancel a pending invitation."""
        result = await self.db.execute(
            select(Invitation).where(Invitation.id == invitation_id)
        )
        invitation = result.scalar_one_or_none()
        if not invitation or invitation.status != InvitationStatus.pending:
            return False

        invitation.status = InvitationStatus.canceled
        invitation.canceled_at = datetime.utcnow()
        await self.db.flush()
        return True

    async def resend_invitation(self, invitation_id: UUID) -> bool:
        """Resend invitation — new token, new expiry."""
        result = await self.db.execute(
            select(Invitation).where(Invitation.id == invitation_id)
        )
        invitation = result.scalar_one_or_none()
        if not invitation or invitation.status != InvitationStatus.pending:
            return False

        from fasthub_core.config import get_settings
        settings = get_settings()
        expire_days = getattr(settings, "INVITATION_EXPIRE_DAYS", 7)

        invitation.token = secrets.token_urlsafe(48)
        invitation.expires_at = datetime.utcnow() + timedelta(days=expire_days)
        await self.db.flush()

        await self._send_invitation_email(invitation)
        return True

    async def cleanup_expired(self) -> int:
        """Mark expired invitations. Run as cron job."""
        result = await self.db.execute(
            update(Invitation)
            .where(
                Invitation.status == InvitationStatus.pending,
                Invitation.expires_at < datetime.utcnow(),
            )
            .values(status=InvitationStatus.expired)
        )
        await self.db.flush()
        return result.rowcount

    async def _get_by_token(self, token: str) -> Optional[Invitation]:
        result = await self.db.execute(
            select(Invitation).where(Invitation.token == token)
        )
        return result.scalar_one_or_none()

    async def _send_invitation_email(self, invitation: Invitation) -> None:
        """Send invitation email using template engine."""
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

            from fasthub_core.email.send import send_templated_email
            await send_templated_email(
                template_name="invitation",
                to=invitation.email,
                subject=f"Zaproszenie do organizacji",
                context={
                    "inviter_name": "Administrator",
                    "org_name": str(invitation.organization_id),
                    "role_name": invitation.role,
                    "accept_url": f"{frontend_url}/invitations/accept/{invitation.token}",
                    "expires_in": "7 dni",
                },
            )
        except Exception as e:
            logger.warning(f"Failed to send invitation email: {e}")
