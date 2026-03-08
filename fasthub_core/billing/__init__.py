"""
Billing package — models, service, middleware, API.
"""

from fasthub_core.billing.models import (
    Subscription, SubscriptionStatus, Invoice, InvoiceStatus,
    BillingPlan, BillingAddon, TenantAddon, UsageRecord, BillingEvent,
)
from fasthub_core.billing.service import BillingService, InvoiceService
from fasthub_core.billing.subscription_check import (
    SubscriptionChecker,
    require_active_subscription,
)
from fasthub_core.billing.feature_flags import (
    check_feature,
    get_plan_features,
    require_feature,
)
from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentStatus,
    PaymentMethod, PaymentResult, WebhookResult,
)
from fasthub_core.billing.payment_registry import PaymentGatewayRegistry, get_payment_registry
from fasthub_core.billing.gateways.stripe_gateway import StripeGateway

__all__ = [
    "Subscription", "SubscriptionStatus", "Invoice", "InvoiceStatus",
    "BillingPlan", "BillingAddon", "TenantAddon", "UsageRecord", "BillingEvent",
    "BillingService", "InvoiceService",
    "SubscriptionChecker", "require_active_subscription",
    "check_feature", "get_plan_features", "require_feature",
    # Brief 16
    "StripeWebhookHandler",
    "PaymentGateway", "PaymentGatewayRegistry", "PaymentStatus",
    "PaymentMethod", "PaymentResult", "WebhookResult",
    "get_payment_registry", "StripeGateway",
]
