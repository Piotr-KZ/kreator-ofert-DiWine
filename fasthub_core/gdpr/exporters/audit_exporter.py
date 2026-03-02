"""Export audit log entries for user."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy import select

from fasthub_core.gdpr.export_registry import DataExporter


class AuditExporter(DataExporter):

    async def get_export_name(self) -> str:
        return "audit_log"

    async def export_user_data(self, user_id: UUID, db) -> Dict[str, Any]:
        from fasthub_core.audit.models import AuditLog

        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
        )
        entries = []
        for a in result.scalars().all():
            entries.append({
                "id": str(a.id),
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "summary": a.summary,
                "ip_address": a.ip_address,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })

        return {"audit_entries": entries}
