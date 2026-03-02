"""
Testy modułu Billing System (fasthub_core.billing).
"""

import pytest


def test_billing_models_import():
    from fasthub_core.billing.models import (
        BillingPlan, BillingAddon, TenantAddon,
        Subscription, UsageRecord, BillingEvent
    )
    assert BillingPlan.__tablename__ == "billing_plans"
    assert BillingAddon.__tablename__ == "billing_addons"
    assert UsageRecord.__tablename__ == "usage_records"
    assert TenantAddon.__tablename__ == "tenant_addons"
    assert BillingEvent.__tablename__ == "billing_events"


def test_billing_plan_has_required_fields():
    from fasthub_core.billing.models import BillingPlan
    import inspect
    source = inspect.getsource(BillingPlan)
    required = ["slug", "name", "billing_mode", "price_monthly", "price_yearly",
                 "stripe_price_monthly_id", "max_processes", "max_team_members",
                 "features", "is_active", "is_default"]
    for field in required:
        assert field in source, f"BillingPlan brakuje pola: {field}"


def test_billing_addon_has_resource_type():
    from fasthub_core.billing.models import BillingAddon
    import inspect
    source = inspect.getsource(BillingAddon)
    assert "resource_type" in source
    assert "quantity" in source
    assert "available_for_plans" in source


def test_billing_service_imports():
    from fasthub_core.billing.service import BillingService
    assert BillingService is not None


def test_billing_service_has_key_methods():
    from fasthub_core.billing.service import BillingService
    required_methods = [
        "get_plan", "list_plans", "check_limit",
        "get_effective_limit", "increment_usage",
        "get_subscription", "seed_billing_plans"
    ]
    for method in required_methods:
        assert hasattr(BillingService, method), f"BillingService brakuje: {method}"


def test_billing_middleware_imports():
    from fasthub_core.billing.middleware import enforce_limit, require_limit
    assert callable(enforce_limit)
    assert callable(require_limit)


def test_billing_api_router():
    from fasthub_core.billing.api import router
    assert router is not None
    # Sprawdź czy router ma endpointy
    routes = [r.path for r in router.routes]
    assert any("subscription" in r for r in routes)


def test_billing_modes():
    """Sprawdź czy billing wspiera oba tryby: fixed i modular"""
    from fasthub_core.billing.models import BillingPlan
    import inspect
    source = inspect.getsource(BillingPlan)
    assert "billing_mode" in source
    assert "fixed" in source
    assert "modular" in source


def test_no_autoflow_references_in_billing():
    import inspect
    from fasthub_core.billing import service, middleware
    for mod in [service, middleware]:
        source = inspect.getsource(mod)
        assert "DEFAULT_TENANT" not in source
        assert "from app." not in source


def test_existing_subscription_preserved():
    """Upewnij się że istniejący model Subscription z Briefu 0 nadal działa"""
    from fasthub_core.billing.models import Subscription, SubscriptionStatus
    assert Subscription.__tablename__ == "subscriptions"
    assert hasattr(Subscription, 'stripe_subscription_id')
    assert hasattr(Subscription, 'status')
    assert hasattr(Subscription, 'organization_id')


def test_existing_invoice_preserved():
    """Upewnij się że istniejący model Invoice z Briefu 0 nadal działa"""
    from fasthub_core.billing.models import Invoice, InvoiceStatus
    assert Invoice.__tablename__ == "invoices"
    assert hasattr(Invoice, 'invoice_number')
    assert hasattr(Invoice, 'amount')


def test_subscription_has_new_fields():
    """Subscription powinien mieć nowe pola z AutoFlow (plan_id, billing_interval)"""
    from fasthub_core.billing.models import Subscription
    assert hasattr(Subscription, 'plan_id')
    assert hasattr(Subscription, 'billing_interval')
    assert hasattr(Subscription, 'trial_end')
    assert hasattr(Subscription, 'stripe_customer_id')


def test_usage_record_fields():
    """UsageRecord powinien mieć wszystkie countery"""
    from fasthub_core.billing.models import UsageRecord
    assert hasattr(UsageRecord, 'executions_count')
    assert hasattr(UsageRecord, 'ai_operations_count')
    assert hasattr(UsageRecord, 'storage_used_mb')
    assert hasattr(UsageRecord, 'webhook_calls_count')


def test_invoice_service_still_works():
    """InvoiceService powinien nadal istnieć"""
    from fasthub_core.billing.service import InvoiceService
    assert InvoiceService is not None
