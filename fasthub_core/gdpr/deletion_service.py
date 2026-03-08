"""
DeletionService — GDPR Art. 17 account deletion workflow.

Flow: request → 14 day grace → auto-export → anonymize → completed.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select

from fasthub_core.config import get_settings
from fasthub_core.gdpr.anonymize_service import AnonymizeService
from fasthub_core.gdpr.export_service import ExportService
from fasthub_core.gdpr.models import DeletionRequest


class DeletionService:
    """Manage account deletion workflow with grace period."""

    def __init__(self, db):
        self.db = db

    async def create_request(
        self,
        user_id: UUID,
        reason: Optional[str] = None,
    ) -> DeletionRequest:
        """Create a new deletion request with grace period."""
        # Check for existing pending request
        existing = await self._get_pending_request(user_id)
        if existing:
            return existing

        settings = get_settings()
        grace_days = getattr(settings, "GDPR_DELETION_GRACE_DAYS", 14)

        request = DeletionRequest(
            user_id=user_id,
            status="pending",
            execute_after=datetime.utcnow() + timedelta(days=grace_days),
            reason=reason,
        )
        self.db.add(request)
        await self.db.flush()
        return request

    async def cancel_request(self, user_id: UUID) -> Optional[DeletionRequest]:
        """Cancel a pending deletion request."""
        request = await self._get_pending_request(user_id)
        if not request:
            return None

        request.status = "canceled"
        request.canceled_at = datetime.utcnow()
        await self.db.flush()
        return request

    async def execute_request(self, request_id: UUID) -> DeletionRequest:
        """
        Execute deletion: export data → anonymize → mark completed.
        Called by cron/task queue after grace period.
        """
        result = await self.db.execute(
            select(DeletionRequest).where(DeletionRequest.id == request_id)
        )
        request = result.scalar_one_or_none()
        if not request or request.status != "pending":
            raise ValueError(f"Request {request_id} not found or not pending")

        if datetime.utcnow() < request.execute_after:
            raise ValueError("Grace period not expired yet")

        request.status = "processing"
        await self.db.flush()

        try:
            # Auto-export before anonymization
            settings = get_settings()
            auto_export = getattr(settings, "GDPR_AUTO_EXPORT_ON_DELETE", True)
            if auto_export:
                export_svc = ExportService(self.db)
                zip_bytes = await export_svc.generate_zip(request.user_id)
                # Store export (in real production: save to storage service)
                request.export_file_path = f"gdpr_exports/{request.user_id}_{datetime.utcnow().strftime('%Y%m%d')}.zip"

            # Anonymize
            anon_svc = AnonymizeService(self.db)
            await anon_svc.anonymize_user(request.user_id)

            request.status = "completed"
            request.executed_at = datetime.utcnow()
        except Exception:
            request.status = "failed"
            raise
        finally:
            await self.db.flush()

        return request

    async def get_due_requests(self) -> list:
        """Get all pending requests past their grace period."""
        result = await self.db.execute(
            select(DeletionRequest).where(
                DeletionRequest.status == "pending",
                DeletionRequest.execute_after <= datetime.utcnow(),
            )
        )
        return result.scalars().all()

    async def get_request_status(self, user_id: UUID) -> Optional[DeletionRequest]:
        """Get the most recent deletion request for a user."""
        result = await self.db.execute(
            select(DeletionRequest)
            .where(DeletionRequest.user_id == user_id)
            .order_by(DeletionRequest.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_pending_request(self, user_id: UUID) -> Optional[DeletionRequest]:
        result = await self.db.execute(
            select(DeletionRequest).where(
                DeletionRequest.user_id == user_id,
                DeletionRequest.status == "pending",
            )
        )
        return result.scalar_one_or_none()
