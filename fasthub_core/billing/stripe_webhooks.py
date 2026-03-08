"""
Stripe Webhook Handler — szczegolowa obsluga webhookow Stripe z hook points.

Event types:
1. checkout.session.completed — kupno planu lub addona
2. customer.subscription.updated — sync statusu
3. customer.subscription.created — sync statusu
4. customer.subscription.deleted — anulowanie subskrypcji
5. invoice.payment_failed — nieudana platnosc
6. invoice.payment_succeeded — udana platnosc

Hook points (aplikacja moze nadpisac):
    - on_checkout_completed(db, tenant_id, result)
    - on_subscription_canceled(db, tenant_id, info)
    - on_payment_failed(db, tenant_id, invoice_data)
    - on_payment_succeeded(db, tenant_id, invoice_data)

Bezpieczenstwo:
    - Weryfikacja podpisu (stripe.Webhook.construct_event)
    - Deduplikacja eventow (stripe_event_id UNIQUE)
    - Idempotentnosc (ten sam event 2x -> skip)
"""

import logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.billing.models import (
    BillingEvent, BillingPlan, Subscription, SubscriptionStatus,
    BillingAddon, TenantAddon,
)

logger = logging.getLogger(__name__)

WebhookHook = Callable[..., Coroutine[Any, Any, None]]


class StripeWebhookHandler:
    """
    Obsluga webhookow Stripe z hook points dla aplikacji.

    Podstawowe uzycie:
        handler = StripeWebhookHandler(db)
        result = await handler.process(payload, sig_header)

    Z hookami:
        handler = StripeWebhookHandler(db)
        handler.on_checkout_completed = my_checkout_hook
        result = await handler.process(payload, sig_header)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

        # Hook points
        self.on_checkout_completed: Optional[WebhookHook] = None
        self.on_subscription_canceled: Optional[WebhookHook] = None
        self.on_payment_failed: Optional[WebhookHook] = None
        self.on_payment_succeeded: Optional[WebhookHook] = None

    async def process(
        self, payload: bytes, sig_header: str
    ) -> Dict[str, Any]:
        """
        Przetwoz webhook od Stripe.

        1. Zweryfikuj podpis
        2. Sprawdz deduplikacje
        3. Route do handlera
        4. Wywolaj hook
        5. Zapisz BillingEvent
        """
        import stripe
        from fasthub_core.config import get_settings
        settings = get_settings()

        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            raise ValueError("Stripe webhook secret not configured")

        # 1. Weryfikacja podpisu
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            logger.warning("Stripe webhook: invalid signature")
            raise ValueError("Invalid webhook signature")

        event_type = event["type"]
        event_id = event["id"]
        data = event["data"]["object"]

        logger.info(f"[STRIPE] Webhook received: {event_type} (id={event_id})")

        # 2. Deduplikacja
        existing = await self.db.execute(
            select(BillingEvent).where(BillingEvent.stripe_event_id == event_id)
        )
        if existing.scalar_one_or_none():
            logger.info(f"[STRIPE] Duplicate event skipped: {event_id}")
            return {"status": "duplicate", "event_type": event_type, "event_id": event_id}

        # 3. Route do handlera
        result = {"status": "processed", "event_type": event_type, "event_id": event_id}

        handler_map = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.created": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_failed": self._handle_payment_failed,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
        }

        handler = handler_map.get(event_type)
        if handler:
            handler_result = await handler(data)
            result.update(handler_result)
        else:
            logger.info(f"[STRIPE] Unhandled event type: {event_type}")
            result["status"] = "ignored"

        # 4. Audit trail
        tenant_id = self._extract_tenant_id(data)
        billing_event = BillingEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            stripe_event_id=event_id,
            data={
                "object_id": data.get("id"),
                "status": data.get("status"),
                "result": result,
            },
        )
        self.db.add(billing_event)
        await self.db.commit()

        logger.info(f"[STRIPE] Event processed: {event_type} -> {result.get('status')}")
        return result

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    async def _handle_checkout_completed(self, session: dict) -> Dict[str, Any]:
        """checkout.session.completed — klient kupil plan lub addon."""
        tenant_id = self._extract_tenant_id(session)
        if not tenant_id:
            return {"warning": "no tenant_id in metadata"}

        addon_slug = session.get("metadata", {}).get("addon_slug")

        if addon_slug:
            result = await self._process_addon_purchase(tenant_id, session)
        else:
            result = await self._process_plan_purchase(tenant_id, session)

        if self.on_checkout_completed:
            try:
                await self.on_checkout_completed(self.db, tenant_id, result)
            except Exception as e:
                logger.error(f"on_checkout_completed hook error: {e}")

        return result

    async def _process_plan_purchase(self, tenant_id: str, session: dict) -> Dict[str, Any]:
        """Klient kupil/zmienil plan."""
        plan_slug = session.get("metadata", {}).get("plan_slug")

        plan = None
        if plan_slug:
            result = await self.db.execute(
                select(BillingPlan).where(BillingPlan.slug == plan_slug)
            )
            plan = result.scalar_one_or_none()

        if not plan:
            result = await self.db.execute(
                select(BillingPlan).where(BillingPlan.is_default == True)
            )
            plan = result.scalar_one_or_none()

        if not plan:
            return {"error": "plan not found", "plan_slug": plan_slug}

        # Update lub create subscription
        sub_result = await self.db.execute(
            select(Subscription).where(Subscription.organization_id == tenant_id)
        )
        sub = sub_result.scalar_one_or_none()

        billing_interval = session.get("metadata", {}).get("billing_interval", "monthly")

        if sub:
            sub.plan_id = plan.id
            sub.status = SubscriptionStatus.active
            sub.stripe_subscription_id = session.get("subscription") or sub.stripe_subscription_id
            sub.stripe_customer_id = session.get("customer") or sub.stripe_customer_id
            sub.billing_interval = billing_interval
            sub.current_period_start = datetime.utcnow()
            sub.updated_at = datetime.utcnow()
        else:
            # Nowa subskrypcja — wymaga stripe_subscription_id i stripe_price_id
            sub = Subscription(
                organization_id=tenant_id,
                plan_id=plan.id,
                status=SubscriptionStatus.active,
                stripe_subscription_id=session.get("subscription") or f"checkout_{session.get('id', 'unknown')}",
                stripe_customer_id=session.get("customer", ""),
                stripe_price_id=session.get("metadata", {}).get("price_id", "checkout"),
                billing_interval=billing_interval,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow(),
            )
            self.db.add(sub)

        await self.db.flush()
        logger.info(f"[STRIPE] Plan purchased: tenant={tenant_id}, plan={plan.slug}")
        return {"tenant_id": tenant_id, "plan": plan.slug, "action": "plan_purchased"}

    async def _process_addon_purchase(self, tenant_id: str, session: dict) -> Dict[str, Any]:
        """Klient kupil addon."""
        addon_slug = session.get("metadata", {}).get("addon_slug")
        quantity = int(session.get("metadata", {}).get("quantity", "1"))

        result = await self.db.execute(
            select(BillingAddon).where(BillingAddon.slug == addon_slug)
        )
        addon = result.scalar_one_or_none()

        if not addon:
            return {"warning": f"addon not found: {addon_slug}"}

        tenant_addon = TenantAddon(
            tenant_id=tenant_id,
            addon_id=addon.id,
            quantity=quantity,
            is_active=True,
            stripe_subscription_item_id=session.get("subscription"),
        )
        self.db.add(tenant_addon)
        await self.db.flush()

        logger.info(f"[STRIPE] Addon purchased: tenant={tenant_id}, addon={addon_slug}, qty={quantity}")
        return {"tenant_id": tenant_id, "addon": addon_slug, "quantity": quantity, "action": "addon_purchased"}

    async def _handle_subscription_updated(self, stripe_sub: dict) -> Dict[str, Any]:
        """customer.subscription.updated/created — sync statusu."""
        stripe_sub_id = stripe_sub.get("id")

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()

        if not sub:
            logger.warning(f"[STRIPE] Subscription not found: {stripe_sub_id}")
            return {"warning": f"subscription {stripe_sub_id} not found in DB"}

        new_status = stripe_sub.get("status")
        if new_status and hasattr(SubscriptionStatus, new_status):
            sub.status = SubscriptionStatus(new_status)

        period_start = stripe_sub.get("current_period_start")
        period_end = stripe_sub.get("current_period_end")
        if period_start:
            sub.current_period_start = datetime.utcfromtimestamp(period_start)
        if period_end:
            sub.current_period_end = datetime.utcfromtimestamp(period_end)

        canceled_at = stripe_sub.get("canceled_at")
        if canceled_at:
            sub.canceled_at = datetime.utcfromtimestamp(canceled_at)

        sub.updated_at = datetime.utcnow()
        await self.db.flush()

        logger.info(f"[STRIPE] Subscription updated: {stripe_sub_id} -> status={sub.status}")
        return {
            "subscription_id": stripe_sub_id,
            "status": sub.status.value if hasattr(sub.status, 'value') else str(sub.status),
            "action": "subscription_updated",
        }

    async def _handle_subscription_deleted(self, stripe_sub: dict) -> Dict[str, Any]:
        """customer.subscription.deleted — anulowanie subskrypcji."""
        stripe_sub_id = stripe_sub.get("id")

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()

        if not sub:
            return {"warning": f"subscription {stripe_sub_id} not found"}

        tenant_id = str(sub.organization_id)
        old_plan_id = sub.plan_id

        # Downgrade do free plan
        free_plan_result = await self.db.execute(
            select(BillingPlan).where(BillingPlan.is_default == True)
        )
        free_plan = free_plan_result.scalar_one_or_none()

        sub.status = SubscriptionStatus.canceled
        sub.canceled_at = datetime.utcnow()
        if free_plan:
            sub.plan_id = free_plan.id

        # Deaktywuj addony
        addons_result = await self.db.execute(
            select(TenantAddon).where(
                TenantAddon.tenant_id == tenant_id,
                TenantAddon.is_active == True,
            )
        )
        deactivated_addons = 0
        for addon in addons_result.scalars().all():
            addon.is_active = False
            deactivated_addons += 1

        await self.db.flush()

        logger.info(f"[STRIPE] Subscription canceled: tenant={tenant_id}, {deactivated_addons} addons deactivated")

        if self.on_subscription_canceled:
            try:
                await self.on_subscription_canceled(
                    self.db, tenant_id, {"old_plan_id": old_plan_id}
                )
            except Exception as e:
                logger.error(f"on_subscription_canceled hook error: {e}")

        return {
            "tenant_id": tenant_id,
            "action": "subscription_canceled",
            "downgraded_to": free_plan.slug if free_plan else "none",
            "addons_deactivated": deactivated_addons,
        }

    async def _handle_payment_failed(self, invoice: dict) -> Dict[str, Any]:
        """invoice.payment_failed — nieudana platnosc."""
        stripe_sub_id = invoice.get("subscription")
        if not stripe_sub_id:
            return {"warning": "no subscription in invoice"}

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()

        if not sub:
            return {"warning": f"subscription {stripe_sub_id} not found"}

        sub.status = SubscriptionStatus.past_due
        sub.updated_at = datetime.utcnow()
        await self.db.flush()

        tenant_id = str(sub.organization_id)
        logger.warning(f"[STRIPE] Payment failed: tenant={tenant_id}, sub={stripe_sub_id}")

        if self.on_payment_failed:
            try:
                await self.on_payment_failed(
                    self.db, tenant_id, {
                        "subscription_id": stripe_sub_id,
                        "amount_due": invoice.get("amount_due"),
                        "attempt_count": invoice.get("attempt_count"),
                        "next_attempt": invoice.get("next_payment_attempt"),
                    }
                )
            except Exception as e:
                logger.error(f"on_payment_failed hook error: {e}")

        return {"tenant_id": tenant_id, "action": "payment_failed", "status": "past_due"}

    async def _handle_payment_succeeded(self, invoice: dict) -> Dict[str, Any]:
        """invoice.payment_succeeded — przywraca active jesli byl past_due."""
        stripe_sub_id = invoice.get("subscription")
        if not stripe_sub_id:
            return {"status": "ignored", "reason": "no subscription"}

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        sub = result.scalar_one_or_none()

        tenant_id = str(sub.organization_id) if sub else "unknown"

        if sub and sub.status == SubscriptionStatus.past_due:
            sub.status = SubscriptionStatus.active
            sub.updated_at = datetime.utcnow()
            await self.db.flush()
            logger.info(f"[STRIPE] Payment succeeded, restored active: tenant={tenant_id}")

        if self.on_payment_succeeded:
            try:
                await self.on_payment_succeeded(
                    self.db, tenant_id, {
                        "invoice_id": invoice.get("id"),
                        "amount_paid": invoice.get("amount_paid"),
                        "currency": invoice.get("currency"),
                        "customer_email": invoice.get("customer_email"),
                        "invoice_pdf": invoice.get("invoice_pdf"),
                    }
                )
            except Exception as e:
                logger.error(f"on_payment_succeeded hook error: {e}")

        return {"tenant_id": tenant_id, "action": "payment_succeeded"}

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _extract_tenant_id(self, data: dict) -> str:
        """Wyciagnij tenant_id z metadata Stripe."""
        metadata = data.get("metadata", {})
        return metadata.get("tenant_id", "unknown")
