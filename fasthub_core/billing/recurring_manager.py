"""
RecurringManager — serce polskich subskrypcji.

Polskie bramki (PayU, Tpay, P24) NIE maja natywnych subskrypcji.
RecurringManager uruchamiany jako cron job:
- Co godzine: sprawdz subskrypcje do odnowienia
- Generuj platnosci
- Obsluz grace period
- Downgrade jesli nie zaplacono

NIE dotyczy Stripe i PayPal (maja natywne subskrypcje).
DOTYCZY: PayU, Tpay, P24, iMoje, CashBill (przyszlosc).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fasthub_core.billing.payment_gateway import PaymentResult

logger = logging.getLogger(__name__)

# Bramki z natywnymi subskrypcjami — pomijane przez RecurringManager
NATIVE_SUBSCRIPTION_GATEWAYS = {"stripe", "paypal"}


class RecurringManager:
    """
    Zarzadza cyklem subskrypcji dla bramek BEZ natywnych subskrypcji.

    Uruchamiany jako cron job (co godzine):
    1. Znajdz subskrypcje do odnowienia
    2. Generuj platnosci
    3. Obsluz grace period
    4. Downgrade jesli nie zaplacono
    """

    def __init__(self, db):
        self.db = db

    async def process_renewals(self) -> Dict[str, Any]:
        """
        Glowna metoda — wywolywana co godzine przez cron.

        1. Znajdz subskrypcje gdzie:
           - status = active lub past_due
           - gateway_id NOT IN (stripe, paypal)
           - current_period_end < now

        2. Dla kazdej: stworz platnosc lub obsluz grace period
        """
        from fasthub_core.config import get_settings
        settings = get_settings()
        grace_days = getattr(settings, "RECURRING_GRACE_DAYS", 14)
        reminder_days = self._parse_reminder_days(
            getattr(settings, "RECURRING_REMINDER_DAYS", "1,3,7")
        )

        now = datetime.utcnow()
        subscriptions = await self._get_due_subscriptions(now)

        results = {
            "processed": 0,
            "renewed": 0,
            "reminders_sent": 0,
            "past_due": 0,
            "canceled": 0,
            "skipped": 0,
            "errors": 0,
        }

        for sub in subscriptions:
            try:
                days_overdue = (now - sub.current_period_end).days

                if days_overdue <= 0:
                    results["skipped"] += 1
                    continue

                result = await self._handle_subscription_renewal(
                    sub, days_overdue, grace_days, reminder_days
                )
                results["processed"] += 1

                if result == "renewed":
                    results["renewed"] += 1
                elif result == "reminder":
                    results["reminders_sent"] += 1
                elif result == "past_due":
                    results["past_due"] += 1
                elif result == "canceled":
                    results["canceled"] += 1

            except Exception as e:
                logger.error(f"RecurringManager error for subscription {sub.id}: {e}")
                results["errors"] += 1

        logger.info(f"RecurringManager: {results}")
        return results

    async def _handle_subscription_renewal(
        self, subscription, days_overdue: int, grace_days: int, reminder_days: List[int],
    ) -> str:
        """Handle a single subscription renewal — delegates to DunningService."""
        # Delegate to DunningService for configurable dunning path
        try:
            from fasthub_core.billing.dunning_service import DunningService
            dunning = DunningService(self.db)
            await dunning.process_overdue_subscription(subscription, days_overdue)
        except Exception as e:
            logger.error(f"DunningService error for sub {subscription.id}: {e}")

        # Keep original status tracking logic
        if days_overdue <= 3:
            payment_result = await self.create_renewal_payment(subscription)
            if payment_result and payment_result.success:
                logger.info(f"Renewal payment created for sub {subscription.id}")
            return "renewed"

        elif days_overdue <= grace_days:
            await self._mark_past_due(subscription)
            return "past_due"

        else:
            await self._cancel_and_downgrade(subscription)
            return "canceled"

    async def create_renewal_payment(self, subscription) -> Optional[PaymentResult]:
        """Create renewal payment via the subscription's gateway."""
        from fasthub_core.billing.payment_registry import get_payment_registry
        from fasthub_core.config import get_settings

        gateway_id = getattr(subscription, "gateway_id", None)
        if not gateway_id or gateway_id in NATIVE_SUBSCRIPTION_GATEWAYS:
            return None

        amount = getattr(subscription, "amount", None)
        currency = getattr(subscription, "currency", "PLN")
        if not amount:
            return None

        settings = get_settings()
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

        registry = get_payment_registry()
        result = await registry.create_payment(
            gateway_id=gateway_id,
            amount=amount,
            currency=currency,
            description=f"Odnowienie subskrypcji",
            return_url=f"{frontend_url}/billing/renewal-success",
            metadata={
                "tenant_id": str(subscription.organization_id),
                "renewal": True,
                "subscription_id": str(subscription.id),
            },
        )

        # Track attempt
        subscription.last_renewal_attempt = datetime.utcnow()
        if not result.success:
            subscription.renewal_failures = (subscription.renewal_failures or 0) + 1
        await self.db.flush()

        return result

    async def handle_renewal_paid(self, subscription) -> None:
        """After payment — extend period by month/year."""
        interval = getattr(subscription, "billing_interval", "monthly")
        if interval == "yearly":
            subscription.current_period_end += timedelta(days=365)
        else:
            subscription.current_period_end += timedelta(days=30)

        subscription.status = "active"
        subscription.renewal_failures = 0
        subscription.grace_period_end = None
        subscription.last_renewal_attempt = None
        await self.db.flush()

        logger.info(
            f"Subscription {subscription.id} renewed until {subscription.current_period_end}"
        )

    async def _get_due_subscriptions(self, now: datetime) -> list:
        """Find subscriptions that need renewal."""
        from sqlalchemy import select
        from fasthub_core.billing.models import Subscription, SubscriptionStatus

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.status.in_([
                    SubscriptionStatus.active,
                    SubscriptionStatus.past_due,
                ]),
                Subscription.current_period_end < now,
                Subscription.gateway_id.isnot(None),
                Subscription.gateway_id.notin_(list(NATIVE_SUBSCRIPTION_GATEWAYS)),
            )
        )
        return list(result.scalars().all())

    async def _mark_past_due(self, subscription) -> None:
        """Mark subscription as past_due."""
        from fasthub_core.billing.models import SubscriptionStatus
        subscription.status = SubscriptionStatus.past_due
        if not subscription.grace_period_end:
            from fasthub_core.config import get_settings
            grace_days = getattr(get_settings(), "RECURRING_GRACE_DAYS", 14)
            subscription.grace_period_end = (
                subscription.current_period_end + timedelta(days=grace_days)
            )
        await self.db.flush()

    async def _cancel_and_downgrade(self, subscription) -> None:
        """Cancel subscription and downgrade to free plan."""
        from sqlalchemy import select
        from fasthub_core.billing.models import SubscriptionStatus, BillingPlan

        subscription.status = SubscriptionStatus.canceled
        subscription.canceled_at = datetime.utcnow()

        # Find free plan for downgrade
        result = await self.db.execute(
            select(BillingPlan).where(BillingPlan.is_default == True)
        )
        free_plan = result.scalar_one_or_none()
        if free_plan:
            subscription.plan_id = free_plan.id

        await self.db.flush()

        tenant_id = str(subscription.organization_id)
        logger.warning(
            f"Subscription {subscription.id} canceled (grace period expired), "
            f"tenant {tenant_id} downgraded to free"
        )

        await self._send_cancellation_notice(subscription)

    async def _send_reminder(self, subscription, days_overdue: int) -> None:
        """Send payment reminder email."""
        try:
            from fasthub_core.email.engine import send_templated_email
            await send_templated_email(
                template_name="payment_reminder",
                to_email=await self._get_billing_email(subscription),
                context={
                    "days_overdue": days_overdue,
                    "amount": (subscription.amount or 0) / 100,
                    "currency": subscription.currency or "PLN",
                },
            )
        except Exception as e:
            logger.debug(f"Could not send reminder: {e}")

    async def _send_warning(self, subscription, days_overdue: int, grace_days: int) -> None:
        """Send past_due warning email."""
        try:
            from fasthub_core.email.engine import send_templated_email
            await send_templated_email(
                template_name="payment_failed",
                to_email=await self._get_billing_email(subscription),
                context={
                    "days_overdue": days_overdue,
                    "days_remaining": grace_days - days_overdue,
                    "amount": (subscription.amount or 0) / 100,
                    "currency": subscription.currency or "PLN",
                },
            )
        except Exception as e:
            logger.debug(f"Could not send warning: {e}")

    async def _send_cancellation_notice(self, subscription) -> None:
        """Send subscription cancelled email."""
        try:
            from fasthub_core.email.engine import send_templated_email
            await send_templated_email(
                template_name="subscription_canceled",
                to_email=await self._get_billing_email(subscription),
                context={
                    "reason": "Brak platnosci po uplywie grace period",
                },
            )
        except Exception as e:
            logger.debug(f"Could not send cancellation notice: {e}")

    async def _get_billing_email(self, subscription) -> str:
        """Get billing email for subscription's organization."""
        try:
            from sqlalchemy import select
            from fasthub_core.users.models import Organization
            result = await self.db.execute(
                select(Organization).where(
                    Organization.id == subscription.organization_id
                )
            )
            org = result.scalar_one_or_none()
            if org and hasattr(org, "email"):
                return org.email
        except Exception:
            pass
        return ""

    @staticmethod
    def _parse_reminder_days(days_str: str) -> List[int]:
        """Parse comma-separated reminder days string."""
        try:
            return [int(d.strip()) for d in days_str.split(",") if d.strip()]
        except (ValueError, AttributeError):
            return [1, 3, 7]
