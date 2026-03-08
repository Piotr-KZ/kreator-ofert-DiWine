"""Export subscriptions and invoices for user's organizations."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy import select

from fasthub_core.gdpr.export_registry import DataExporter


class BillingExporter(DataExporter):

    async def get_export_name(self) -> str:
        return "billing"

    async def export_user_data(self, user_id: UUID, db) -> Dict[str, Any]:
        from fasthub_core.users.models import Member
        from fasthub_core.billing.models import Subscription, Invoice

        # Get user's organization IDs
        result = await db.execute(
            select(Member.organization_id).where(Member.user_id == user_id)
        )
        org_ids = [row[0] for row in result.all()]

        if not org_ids:
            return {"subscriptions": [], "invoices": []}

        # Subscriptions
        result = await db.execute(
            select(Subscription).where(Subscription.organization_id.in_(org_ids))
        )
        subs = []
        for s in result.scalars().all():
            subs.append({
                "id": str(s.id),
                "organization_id": str(s.organization_id),
                "status": s.status.value if s.status else None,
                "stripe_price_id": s.stripe_price_id,
                "billing_interval": s.billing_interval,
                "current_period_start": _dt(s.current_period_start),
                "current_period_end": _dt(s.current_period_end),
                "trial_end": _dt(s.trial_end),
                "cancel_at_period_end": s.cancel_at_period_end,
                "canceled_at": _dt(s.canceled_at),
                "created_at": _dt(s.created_at),
            })

        # Invoices
        result = await db.execute(
            select(Invoice).where(Invoice.organization_id.in_(org_ids))
        )
        invs = []
        for i in result.scalars().all():
            invs.append({
                "id": str(i.id),
                "organization_id": str(i.organization_id),
                "invoice_number": i.invoice_number,
                "status": i.status.value if i.status else None,
                "amount": str(i.amount) if i.amount else None,
                "currency": i.currency,
                "description": i.description,
                "due_date": _dt(i.due_date),
                "paid_at": _dt(i.paid_at),
                "created_at": _dt(i.created_at),
            })

        return {"subscriptions": subs, "invoices": invs}


def _dt(val) -> str | None:
    return val.isoformat() if val else None
