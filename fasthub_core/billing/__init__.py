"""
Billing package — models, service, middleware, API, payment gateways.
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
from fasthub_core.billing.payment_gateway import (
    PaymentGateway, PaymentMethod, PaymentResult, PaymentStatus, WebhookResult,
)
from fasthub_core.billing.payment_registry import (
    PaymentGatewayRegistry, get_payment_registry,
)
from fasthub_core.billing.recurring_manager import RecurringManager
from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
from fasthub_core.billing.invoice_router import get_invoice_hook

__all__ = [
    "Subscription", "SubscriptionStatus", "Invoice", "InvoiceStatus",
    "BillingPlan", "BillingAddon", "TenantAddon", "UsageRecord", "BillingEvent",
    "BillingService", "InvoiceService",
    "SubscriptionChecker", "require_active_subscription",
    "check_feature", "get_plan_features", "require_feature",
    "PaymentGateway", "PaymentMethod", "PaymentResult", "PaymentStatus", "WebhookResult",
    "PaymentGatewayRegistry", "get_payment_registry",
    "RecurringManager",
    "KSeFXMLBuilder", "KSeFInvoiceHook", "get_invoice_hook",
]
