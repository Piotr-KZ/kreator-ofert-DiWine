"""Export notifications for user."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy import select

from fasthub_core.gdpr.export_registry import DataExporter


class NotificationExporter(DataExporter):

    async def get_export_name(self) -> str:
        return "notifications"

    async def export_user_data(self, user_id: UUID, db) -> Dict[str, Any]:
        from fasthub_core.notifications.models import Notification

        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        items = []
        for n in result.scalars().all():
            items.append({
                "id": str(n.id),
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": n.is_read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            })

        return {"notifications": items}
