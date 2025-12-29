"""
Subscription service
Business logic for subscription operations (matching Firebase use cases)
"""

from datetime import datetime
from typing import Any, Dict, Optional

import stripe
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.services.email_service import EmailService
from app.services.organization_repository import OrganizationRepository
from app.services.stripe_service import StripeService


class SubscriptionService:
    """Service for subscription management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.stripe_service = StripeService()
        self.org_repo = OrganizationRepository(db)
        self.email_service = EmailService()

    async def get_subscription_by_organization(
        self, organization_id: int
    ) -> Optional[Subscription]:
        """Get active subscription for organization"""
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .where(Subscription.status == SubscriptionStatus.active)
        )
        return result.scalar_one_or_none()

    async def create_subscription_for_user(
        self,
        user: User,
        price_id: str,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None,
    ) -> Subscription:
        """
        Create subscription for user's organization
        Firebase equivalent: CreateSubscriptionForUserUseCase
        """
        if not user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User has no organization"
            )

        org = await self.org_repo.get_by_id(user.organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
            )

        # Check if organization already has subscription
        existing = await self.get_subscription_by_organization(org.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization already has an active subscription",
            )

        # Create or get Stripe customer
        if not org.stripe_customer_id:
            customer = await self.stripe_service.create_customer(
                email=user.email, name=org.name, metadata={"organization_id": str(org.id)}
            )
            org.stripe_customer_id = customer.id
            await self.org_repo.update(org)

        # Create Stripe subscription
        stripe_subscription = await self.stripe_service.create_subscription(
            customer_id=org.stripe_customer_id,
            price_id=price_id,
            payment_method_id=payment_method_id,
            trial_days=trial_days,
        )

        # Create local subscription record
        subscription = Subscription(
            organization_id=org.id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_price_id=price_id,
            status=SubscriptionStatus[stripe_subscription.status],
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
            cancel_at_period_end=stripe_subscription.cancel_at_period_end,
        )

        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def change_subscription_plan(
        self, organization_id: int, new_price_id: str, current_user: User
    ) -> Subscription:
        """
        Change subscription plan
        Firebase equivalent: ChangeSubscriptionPlanUseCase
        """
        # Check permissions
        org = await self.org_repo.get_by_id(organization_id)
        if not org or org.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owner can change subscription",
            )

        # Get current subscription
        subscription = await self.get_subscription_by_organization(organization_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
            )

        # Update Stripe subscription
        stripe_subscription = await self.stripe_service.update_subscription(
            subscription.stripe_subscription_id,
            items=[
                {
                    "id": stripe_subscription.items.data[0].id,
                    "price": new_price_id,
                }
            ],
            proration_behavior="create_prorations",
        )

        # Update local record
        subscription.stripe_price_id = new_price_id
        subscription.status = SubscriptionStatus[stripe_subscription.status]
        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def cancel_subscription(
        self, organization_id: int, at_period_end: bool, current_user: User
    ) -> Subscription:
        """Cancel subscription"""
        # Check permissions
        org = await self.org_repo.get_by_id(organization_id)
        if not org or org.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owner can cancel subscription",
            )

        # Get current subscription
        subscription = await self.get_subscription_by_organization(organization_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
            )

        # Cancel Stripe subscription
        await self.stripe_service.cancel_subscription(
            subscription.stripe_subscription_id, at_period_end=at_period_end
        )

        # Update local record
        subscription.cancel_at_period_end = at_period_end
        if not at_period_end:
            subscription.status = SubscriptionStatus.canceled
            subscription.canceled_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def create_billing_portal_session(
        self, organization_id: int, return_url: str, current_user: User
    ) -> Dict[str, str]:
        """
        Create Stripe billing portal session
        Firebase equivalent: CreateBillingCustomerPortalUseCase
        """
        # Check permissions
        if current_user.organization_id != organization_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        org = await self.org_repo.get_by_id(organization_id)
        if not org or not org.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization has no Stripe customer",
            )

        # Create portal session
        session = await self.stripe_service.create_billing_portal_session(
            customer_id=org.stripe_customer_id, return_url=return_url
        )

        return {"url": session.url}

    async def handle_subscription_updated(self, stripe_subscription: stripe.Subscription) -> None:
        """
        Handle subscription updated webhook
        Firebase equivalent: HandleSubscriptionStatusUpdateUseCase
        """
        # Find local subscription
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription.id
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            # Subscription not found, might be new
            return

        # Update local record
        subscription.status = SubscriptionStatus[stripe_subscription.status]
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription.current_period_start
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end
        )
        subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end

        if stripe_subscription.canceled_at:
            subscription.canceled_at = datetime.fromtimestamp(stripe_subscription.canceled_at)

        await self.db.commit()

    async def handle_subscription_deleted(self, stripe_subscription: stripe.Subscription) -> None:
        """Handle subscription deleted webhook"""
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription.id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.canceled
            subscription.canceled_at = datetime.utcnow()
            await self.db.commit()

    async def handle_customer_updated(self, stripe_customer: stripe.Customer) -> None:
        """
        Handle customer updated webhook
        Firebase equivalent: HandleCustomerUpdateUseCase
        """
        # Find organization by Stripe customer ID
        result = await self.db.execute(
            select(Organization).where(Organization.stripe_customer_id == stripe_customer.id)
        )
        org = result.scalar_one_or_none()

        if org:
            # Update organization data if needed
            if stripe_customer.email and org.name != stripe_customer.name:
                org.name = stripe_customer.name or org.name
                await self.db.commit()

    async def handle_failed_payment(self, stripe_invoice: stripe.Invoice) -> None:
        """
        Handle failed payment webhook
        Firebase equivalent: HandleFailedPaymentUseCase
        """
        if not stripe_invoice.subscription:
            return

        # Find subscription
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == str(stripe_invoice.subscription)
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return

        # Update subscription status to past_due
        subscription.status = SubscriptionStatus.past_due
        await self.db.commit()

        # Send notification email to organization owner about failed payment
        organization = await self.org_repo.get_by_id(subscription.organization_id)
        if organization and organization.owner:
            await self.email_service.send_payment_failed_email(
                to_email=organization.owner.email,
                amount=stripe_invoice.amount_due / 100,  # Convert cents to dollars
                currency=stripe_invoice.currency,
                retry_date=None,  # Stripe handles retry automatically
            )

        # TODO: Publish business event for analytics

    async def handle_subscription_cycle(self, stripe_invoice: stripe.Invoice) -> None:
        """
        Handle successful subscription payment (cycle)
        Firebase equivalent: HandleSubscriptionCycleUseCase
        """
        if not stripe_invoice.subscription:
            return

        # Find subscription
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == str(stripe_invoice.subscription)
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return

        # Update subscription with new period
        if stripe_invoice.lines and stripe_invoice.lines.data:
            line = stripe_invoice.lines.data[0]
            if line.period:
                subscription.current_period_start = datetime.fromtimestamp(line.period.start)
                subscription.current_period_end = datetime.fromtimestamp(line.period.end)

        # Ensure status is active after successful payment
        subscription.status = SubscriptionStatus.active
        await self.db.commit()

        # Create invoice record
        from app.services.invoice_service import InvoiceService

        invoice_service = InvoiceService(self.db)

        # Create invoice from Stripe data
        stripe_invoice_dict = {
            "id": stripe_invoice.id,
            "customer": stripe_invoice.customer,
            "amount_due": stripe_invoice.amount_due,
            "currency": stripe_invoice.currency,
            "status": stripe_invoice.status,
            "number": stripe_invoice.number,
            "created": stripe_invoice.created,
            "due_date": stripe_invoice.due_date,
            "status_transitions": stripe_invoice.status_transitions,
            "invoice_pdf": stripe_invoice.invoice_pdf,
            "hosted_invoice_url": stripe_invoice.hosted_invoice_url,
        }

        invoice = await invoice_service.create_invoice_from_stripe(
            stripe_invoice_data=stripe_invoice_dict, organization_id=subscription.organization_id
        )

        # Send invoice email to organization owner
        organization = await self.org_repo.get_by_id(subscription.organization_id)
        if organization and organization.owner:
            await self.email_service.send_invoice_email(
                to_email=organization.owner.email,
                invoice_number=stripe_invoice.number or "N/A",
                amount=stripe_invoice.amount_due / 100,  # Convert cents to dollars
                currency=stripe_invoice.currency,
                invoice_pdf_url=stripe_invoice.invoice_pdf or stripe_invoice.hosted_invoice_url,
            )

        # TODO: Publish business event for analytics

    async def check_subscription_invoice(self, organization_id: int) -> Dict[str, Any]:
        """
        Check subscription invoice status
        Firebase equivalent: CheckSubscriptionInvoiceUseCase
        """
        subscription = await self.get_subscription_by_organization(organization_id)

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found"
            )

        # Get latest invoice from Stripe
        stripe_subscription = await self.stripe_service.get_subscription(
            subscription.stripe_subscription_id
        )

        latest_invoice_id = stripe_subscription.latest_invoice
        if not latest_invoice_id:
            return {"status": "no_invoice"}

        # Get invoice details
        invoice_id = (
            latest_invoice_id if isinstance(latest_invoice_id, str) else latest_invoice_id.id
        )
        stripe_invoice = stripe.Invoice.retrieve(invoice_id)

        return {
            "invoice_id": stripe_invoice.id,
            "status": stripe_invoice.status,
            "amount_due": stripe_invoice.amount_due / 100,  # Convert cents to dollars
            "currency": stripe_invoice.currency,
            "period_start": datetime.fromtimestamp(stripe_invoice.period_start),
            "period_end": datetime.fromtimestamp(stripe_invoice.period_end),
            "hosted_invoice_url": stripe_invoice.hosted_invoice_url,
            "invoice_pdf": stripe_invoice.invoice_pdf,
        }
