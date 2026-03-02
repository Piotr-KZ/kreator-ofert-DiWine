"""
Billing service — InvoiceService (existing) + BillingService (new).

BillingService: plans, subscriptions, addons, usage tracking, Stripe.
InvoiceService: invoice CRUD, PDF generation.
"""

import io
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.billing.models import (
    Invoice, Subscription, BillingPlan, BillingAddon,
    TenantAddon, UsageRecord, BillingEvent,
)
from fasthub_core.users.models import Organization

logger = logging.getLogger("fasthub.billing")


class InvoiceService:
    """Service for invoice management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice_from_stripe(
        self, stripe_invoice_data: dict, organization_id: int
    ) -> Invoice:
        """
        Create invoice from Stripe invoice data
        """
        # Check if invoice already exists
        result = await self.db.execute(
            select(Invoice).where(Invoice.stripe_invoice_id == stripe_invoice_data["id"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        # Create new invoice
        invoice = Invoice(
            organization_id=organization_id,
            stripe_invoice_id=stripe_invoice_data["id"],
            stripe_customer_id=stripe_invoice_data.get("customer"),
            amount=stripe_invoice_data.get("amount_due", 0) / 100,
            currency=stripe_invoice_data.get("currency", "usd"),
            status=stripe_invoice_data.get("status", "draft"),
            invoice_number=stripe_invoice_data.get("number"),
            invoice_date=datetime.fromtimestamp(stripe_invoice_data["created"]),
            due_date=datetime.fromtimestamp(
                stripe_invoice_data.get("due_date", stripe_invoice_data["created"])
            ),
            paid_at=(
                datetime.fromtimestamp(stripe_invoice_data["status_transitions"]["paid_at"])
                if stripe_invoice_data.get("status_transitions", {}).get("paid_at")
                else None
            ),
            invoice_pdf_url=stripe_invoice_data.get("invoice_pdf"),
            hosted_invoice_url=stripe_invoice_data.get("hosted_invoice_url"),
        )

        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        result = await self.db.execute(select(Invoice).where(Invoice.id == invoice_id))
        return result.scalar_one_or_none()

    async def list_invoices_by_organization(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        """List all invoices for organization"""
        result = await self.db.execute(
            select(Invoice)
            .where(Invoice.organization_id == organization_id)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def generate_invoice_pdf(self, invoice_id: int) -> bytes:
        """
        Generate PDF for invoice
        Returns PDF as bytes
        """
        invoice = await self.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

        # Get organization details
        result = await self.db.execute(
            select(Organization).where(Organization.id == invoice.organization_id)
        )
        organization = result.scalar_one_or_none()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=30,
        )

        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        invoice_info = [
            ["Invoice Number:", invoice.invoice_number or f"INV-{invoice.id}"],
            ["Invoice Date:", invoice.invoice_date.strftime("%Y-%m-%d")],
            ["Due Date:", invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else "N/A"],
            ["Status:", invoice.status.upper()],
        ]

        invoice_table = Table(invoice_info, colWidths=[2 * inch, 3 * inch])
        invoice_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.5 * inch))

        elements.append(Paragraph("<b>Bill To:</b>", styles["Normal"]))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(organization.name, styles["Normal"]))
        elements.append(Spacer(1, 0.5 * inch))

        items_data = [
            ["Description", "Amount"],
            ["Subscription", f"${invoice.amount:.2f} {invoice.currency.upper()}"],
        ]

        items_table = Table(items_data, colWidths=[4 * inch, 2 * inch])
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(items_table)
        elements.append(Spacer(1, 0.5 * inch))

        total_data = [
            ["Total:", f"${invoice.amount:.2f} {invoice.currency.upper()}"],
        ]
        total_table = Table(total_data, colWidths=[4 * inch, 2 * inch])
        total_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        elements.append(total_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    async def mark_invoice_as_paid(
        self, invoice_id: int, paid_at: Optional[datetime] = None
    ) -> Invoice:
        """Mark invoice as paid"""
        invoice = await self.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

        invoice.status = "paid"
        invoice.paid_at = paid_at or datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice


# ============================================================================
# Resource name → model column mappings
# ============================================================================

RESOURCE_LIMIT_MAP = {
    "processes": "max_processes",
    "executions": "max_executions_month",
    "integrations": "max_integrations",
    "ai_operations": "max_ai_operations_month",
    "team_members": "max_team_members",
    "file_storage_mb": "max_file_storage_mb",
}

RESOURCE_USAGE_MAP = {
    "executions": "executions_count",
    "ai_operations": "ai_operations_count",
    "processes": "active_processes_count",
    "integrations": "active_integrations_count",
    "file_storage_mb": "storage_used_mb",
    "webhooks": "webhook_calls_count",
}


# ============================================================================
# BillingService — plans, subscriptions, addons, usage, Stripe
# ============================================================================

class BillingService:
    """Billing service for plans, subscriptions, usage, and limits."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === PLANS ===

    async def get_plan(self, slug: str) -> Optional[BillingPlan]:
        """Get plan by slug."""
        result = await self.db.execute(
            select(BillingPlan).where(BillingPlan.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_plans(self, visible_only: bool = True) -> List[BillingPlan]:
        """List all active plans."""
        query = select(BillingPlan).where(BillingPlan.is_active == True)
        if visible_only:
            query = query.where(BillingPlan.is_visible == True)
        query = query.order_by(BillingPlan.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_plan(self, **kwargs) -> BillingPlan:
        """Create a new billing plan."""
        plan = BillingPlan(**kwargs)
        self.db.add(plan)
        await self.db.flush()
        logger.info(f"Plan created: {plan.slug}")
        return plan

    async def update_plan(self, slug: str, **kwargs) -> Optional[BillingPlan]:
        """Update existing plan."""
        plan = await self.get_plan(slug)
        if not plan:
            return None
        for key, value in kwargs.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        plan.updated_at = datetime.utcnow()
        await self.db.flush()
        return plan

    async def delete_plan(self, slug: str) -> bool:
        """Soft-delete plan (set is_active=False)."""
        plan = await self.get_plan(slug)
        if not plan:
            return False
        plan.is_active = False
        await self.db.flush()
        return True

    # === LIMITS ===

    async def get_effective_limit(self, tenant_id: str, resource: str) -> int:
        """Get effective resource limit = plan base + sum(addon quantities)."""
        sub = await self.get_subscription(tenant_id)
        if not sub or not sub.get("plan"):
            return 0

        plan = sub["plan"]
        limit_col = RESOURCE_LIMIT_MAP.get(resource)
        if not limit_col:
            return 0

        base_limit = getattr(plan, limit_col, 0) or 0

        result = await self.db.execute(
            select(func.sum(BillingAddon.quantity * TenantAddon.quantity))
            .join(BillingAddon, TenantAddon.addon_id == BillingAddon.id)
            .where(
                TenantAddon.tenant_id == tenant_id,
                TenantAddon.is_active == True,
                BillingAddon.resource_type == resource,
            )
        )
        addon_total = result.scalar() or 0
        return base_limit + addon_total

    async def check_limit(self, tenant_id: str, resource: str) -> bool:
        """Check if tenant is within limit. True = OK, False = exceeded."""
        limit = await self.get_effective_limit(tenant_id, resource)
        if limit <= 0:
            return False
        current = await self.get_current_usage(tenant_id, resource)
        return current < limit

    async def get_usage_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get usage summary with limits for all resources."""
        period = datetime.utcnow().strftime("%Y-%m")
        result = await self.db.execute(
            select(UsageRecord).where(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.period == period,
            )
        )
        usage = result.scalar_one_or_none()

        summary = {}
        for resource, usage_col in RESOURCE_USAGE_MAP.items():
            current = getattr(usage, usage_col, 0) if usage else 0
            limit = await self.get_effective_limit(tenant_id, resource)
            summary[resource] = {
                "current": current, "limit": limit,
                "remaining": max(0, limit - current),
                "exceeded": current >= limit if limit > 0 else False,
            }
        return summary

    # === USAGE ===

    async def increment_usage(self, tenant_id: str, resource: str, amount: int = 1) -> None:
        """Increment usage counter for a resource."""
        usage_col = RESOURCE_USAGE_MAP.get(resource)
        if not usage_col:
            return

        period = datetime.utcnow().strftime("%Y-%m")
        result = await self.db.execute(
            select(UsageRecord).where(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.period == period,
            )
        )
        usage = result.scalar_one_or_none()

        if usage is None:
            usage = UsageRecord(tenant_id=tenant_id, period=period)
            self.db.add(usage)
            await self.db.flush()

        current_value = getattr(usage, usage_col, 0) or 0
        setattr(usage, usage_col, current_value + amount)
        usage.updated_at = datetime.utcnow()
        await self.db.flush()

    async def get_current_usage(self, tenant_id: str, resource: str) -> int:
        """Get current usage count for a resource in current period."""
        usage_col = RESOURCE_USAGE_MAP.get(resource)
        if not usage_col:
            return 0

        period = datetime.utcnow().strftime("%Y-%m")
        result = await self.db.execute(
            select(UsageRecord).where(
                UsageRecord.tenant_id == tenant_id,
                UsageRecord.period == period,
            )
        )
        usage = result.scalar_one_or_none()
        if usage is None:
            return 0
        return getattr(usage, usage_col, 0) or 0

    async def reset_monthly_usage(self) -> int:
        """Reset monthly counters (cron). Old records stay as history."""
        logger.info("Monthly usage reset triggered")
        return 0

    # === SUBSCRIPTIONS ===

    async def get_subscription(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get active subscription for tenant with plan details."""
        try:
            from uuid import UUID
            org_uuid = UUID(tenant_id)
            result = await self.db.execute(
                select(Subscription).where(
                    Subscription.organization_id == org_uuid
                ).order_by(Subscription.created_at.desc()).limit(1)
            )
        except (ValueError, AttributeError):
            return None

        sub = result.scalar_one_or_none()
        if not sub:
            return None

        plan = None
        if hasattr(sub, 'plan_id') and sub.plan_id:
            plan_result = await self.db.execute(
                select(BillingPlan).where(BillingPlan.id == sub.plan_id)
            )
            plan = plan_result.scalar_one_or_none()

        return {
            "subscription": sub, "plan": plan,
            "stripe_subscription_id": sub.stripe_subscription_id,
            "status": sub.status.value if sub.status else None,
        }

    async def create_subscription(self, **kwargs) -> Subscription:
        """Create new subscription."""
        sub = Subscription(**kwargs)
        self.db.add(sub)
        await self.db.flush()
        return sub

    async def update_subscription(self, subscription_id, **kwargs) -> Optional[Subscription]:
        """Update subscription fields."""
        from uuid import UUID
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == UUID(str(subscription_id)))
        )
        sub = result.scalar_one_or_none()
        if not sub:
            return None
        for key, value in kwargs.items():
            if hasattr(sub, key):
                setattr(sub, key, value)
        await self.db.flush()
        return sub

    async def cancel_subscription(self, tenant_id: str) -> bool:
        """Cancel subscription (set cancel_at_period_end=True)."""
        sub_data = await self.get_subscription(tenant_id)
        if not sub_data:
            return False
        sub = sub_data["subscription"]
        sub.cancel_at_period_end = True
        sub.canceled_at = datetime.utcnow()
        await self.db.flush()
        return True

    # === ADDONS ===

    async def get_available_addons(self, plan_slug: Optional[str] = None) -> List[BillingAddon]:
        """List available addons, optionally filtered by plan."""
        query = select(BillingAddon).where(BillingAddon.is_active == True)
        query = query.order_by(BillingAddon.sort_order)
        result = await self.db.execute(query)
        addons = list(result.scalars().all())

        if plan_slug:
            addons = [
                a for a in addons
                if a.available_for_plans is None
                or plan_slug in (a.available_for_plans or [])
            ]
        return addons

    async def purchase_addon(self, tenant_id: str, addon_id: int, quantity: int = 1) -> TenantAddon:
        """Purchase addon for tenant."""
        tenant_addon = TenantAddon(
            tenant_id=tenant_id, addon_id=addon_id,
            quantity=quantity, is_active=True,
        )
        self.db.add(tenant_addon)
        await self.db.flush()
        return tenant_addon

    async def remove_addon(self, tenant_addon_id: int) -> bool:
        """Deactivate tenant addon."""
        result = await self.db.execute(
            select(TenantAddon).where(TenantAddon.id == tenant_addon_id)
        )
        ta = result.scalar_one_or_none()
        if not ta:
            return False
        ta.is_active = False
        await self.db.flush()
        return True

    # === STRIPE ===

    async def create_checkout_session(
        self, tenant_id: str, price_id: str, success_url: str, cancel_url: str,
    ) -> Optional[Dict[str, Any]]:
        """Create Stripe Checkout Session."""
        try:
            import stripe
            from fasthub_core.config import get_settings
            stripe.api_key = get_settings().STRIPE_SECRET_KEY
            if not stripe.api_key:
                return None
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url, cancel_url=cancel_url,
                metadata={"tenant_id": tenant_id},
            )
            return {"session_id": session.id, "url": session.url}
        except Exception as e:
            logger.error(f"Stripe checkout failed: {e}")
            return None

    async def create_portal_session(
        self, customer_id: str, return_url: str,
    ) -> Optional[Dict[str, Any]]:
        """Create Stripe Customer Portal session."""
        try:
            import stripe
            from fasthub_core.config import get_settings
            stripe.api_key = get_settings().STRIPE_SECRET_KEY
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=return_url,
            )
            return {"url": session.url}
        except Exception as e:
            logger.error(f"Stripe portal failed: {e}")
            return None

    async def handle_stripe_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """Process Stripe webhook event."""
        try:
            import stripe
            from fasthub_core.config import get_settings
            settings = get_settings()
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            billing_event = BillingEvent(
                tenant_id=event.get("data", {}).get("object", {}).get("metadata", {}).get("tenant_id", "unknown"),
                event_type=event["type"],
                stripe_event_id=event["id"],
                data=event.get("data", {}),
            )
            self.db.add(billing_event)
            await self.db.flush()
            return {"event_type": event["type"], "event_id": event["id"]}
        except Exception as e:
            logger.error(f"Stripe webhook failed: {e}")
            return None

    # === SEED ===

    async def seed_billing_plans(self) -> int:
        """Seed default billing plans. Returns number created."""
        default_plans = [
            {"slug": "free", "name": "Free", "billing_mode": "fixed",
             "price_monthly": 0, "price_yearly": 0,
             "max_processes": 3, "max_executions_month": 100,
             "max_integrations": 2, "max_ai_operations_month": 10,
             "max_team_members": 1, "max_file_storage_mb": 100,
             "is_default": True, "sort_order": 0},
            {"slug": "starter", "name": "Starter", "billing_mode": "fixed",
             "price_monthly": 49, "price_yearly": 490,
             "max_processes": 10, "max_executions_month": 1000,
             "max_integrations": 10, "max_ai_operations_month": 100,
             "max_team_members": 5, "max_file_storage_mb": 1000,
             "sort_order": 1},
            {"slug": "pro", "name": "Pro", "billing_mode": "modular",
             "price_monthly": 149, "price_yearly": 1490,
             "max_processes": 50, "max_executions_month": 10000,
             "max_integrations": 50, "max_ai_operations_month": 1000,
             "max_team_members": 20, "max_file_storage_mb": 10000,
             "badge": "Popular", "color": "#4F46E5", "sort_order": 2},
            {"slug": "enterprise", "name": "Enterprise", "billing_mode": "modular",
             "price_monthly": 499, "price_yearly": 4990,
             "max_processes": 999, "max_executions_month": 999999,
             "max_integrations": 999, "max_ai_operations_month": 99999,
             "max_team_members": 999, "max_file_storage_mb": 100000,
             "sort_order": 3},
        ]
        created = 0
        for plan_data in default_plans:
            existing = await self.get_plan(plan_data["slug"])
            if existing is None:
                await self.create_plan(**plan_data)
                created += 1
        if created:
            logger.info(f"Seeded {created} billing plans")
        return created
