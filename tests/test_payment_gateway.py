"""
Testy Payment Gateway — kontrakt, registry, Stripe, webhook handler, shared clients.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ============================================================================
# PAYMENT GATEWAY CONTRACT
# ============================================================================

class TestPaymentGatewayContract:

    def test_contract_is_abstract(self):
        from fasthub_core.billing.payment_gateway import PaymentGateway
        with pytest.raises(TypeError):
            PaymentGateway()

    def test_payment_status_enum(self):
        from fasthub_core.billing.payment_gateway import PaymentStatus
        assert PaymentStatus.completed.value == "completed"
        assert PaymentStatus.pending.value == "pending"
        assert PaymentStatus.failed.value == "failed"
        assert PaymentStatus.canceled.value == "canceled"
        assert PaymentStatus.refunded.value == "refunded"
        assert PaymentStatus.processing.value == "processing"

    def test_payment_method_dataclass(self):
        from fasthub_core.billing.payment_gateway import PaymentMethod
        method = PaymentMethod(id="blik", name="BLIK", gateway_id="payu")
        assert method.id == "blik"
        assert method.name == "BLIK"
        assert method.gateway_id == "payu"
        assert method.icon == ""

    def test_payment_result_success(self):
        from fasthub_core.billing.payment_gateway import PaymentResult
        result = PaymentResult(success=True, payment_id="pi_123", payment_url="https://pay.com")
        assert result.success
        assert result.payment_id == "pi_123"

    def test_payment_result_failure(self):
        from fasthub_core.billing.payment_gateway import PaymentResult
        result = PaymentResult(success=False, error="Card declined")
        assert not result.success
        assert result.error == "Card declined"

    def test_webhook_result(self):
        from fasthub_core.billing.payment_gateway import WebhookResult, PaymentStatus
        result = WebhookResult(status="processed", event_type="checkout", payment_status=PaymentStatus.completed)
        assert result.status == "processed"
        assert result.payment_status == PaymentStatus.completed


# ============================================================================
# PAYMENT GATEWAY REGISTRY
# ============================================================================

class TestPaymentGatewayRegistry:

    def test_create_registry(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        registry = PaymentGatewayRegistry()
        assert registry.get_active_gateways() == []

    def test_register_configured_gateway(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway

        registry = PaymentGatewayRegistry()
        gw = StripeGateway(api_key="sk_test_xxx", webhook_secret="whsec_xxx")
        registry.register(gw)
        assert len(registry.get_active_gateways()) == 1
        assert registry.get_gateway("stripe") is gw

    def test_skip_unconfigured_gateway(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway

        registry = PaymentGatewayRegistry()
        gw = StripeGateway(api_key=None)
        registry.register(gw)
        assert len(registry.get_active_gateways()) == 0

    def test_get_available_methods(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway

        registry = PaymentGatewayRegistry()
        gw = StripeGateway(api_key="sk_test_xxx", webhook_secret="whsec_xxx")
        registry.register(gw)
        methods = registry.get_available_methods()
        assert len(methods) >= 1
        method_ids = [m.id for m in methods]
        assert "card" in method_ids

    def test_get_methods_with_gateways(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway

        registry = PaymentGatewayRegistry()
        gw = StripeGateway(api_key="sk_test_xxx", webhook_secret="whsec_xxx")
        registry.register(gw)
        results = registry.get_methods_with_gateways()
        assert len(results) >= 1
        assert "stripe" in results[0]["gateways"]

    def test_get_gateway_returns_none_for_unknown(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        registry = PaymentGatewayRegistry()
        assert registry.get_gateway("nonexistent") is None

    @pytest.mark.asyncio
    async def test_create_payment_unknown_gateway(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        registry = PaymentGatewayRegistry()
        result = await registry.create_payment(
            "nonexistent", amount=100, currency="PLN",
            description="Test", return_url="http://x",
        )
        assert not result.success

    @pytest.mark.asyncio
    async def test_handle_webhook_unknown_gateway(self):
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        registry = PaymentGatewayRegistry()
        result = await registry.handle_webhook("nonexistent", b"", {})
        assert result.status == "ignored"

    def test_method_deduplication(self):
        """Jesli dwie bramki maja ta sama metode, pokaz raz."""
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway

        registry = PaymentGatewayRegistry()
        gw1 = StripeGateway(api_key="sk_test_1")
        gw2 = StripeGateway(api_key="sk_test_2")
        # Trick: change gateway_id for gw2
        gw2.__class__ = type('Stripe2', (StripeGateway,), {'gateway_id': property(lambda s: 'stripe2'), 'display_name': property(lambda s: 'Stripe2')})
        registry.register(gw1)
        registry.register(gw2)
        methods = registry.get_available_methods()
        card_count = sum(1 for m in methods if m.id == "card")
        assert card_count == 1  # Deduplicated


# ============================================================================
# STRIPE GATEWAY
# ============================================================================

class TestStripeGateway:

    def test_gateway_id(self):
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway
        gw = StripeGateway(api_key="sk_test_xxx")
        assert gw.gateway_id == "stripe"
        assert gw.display_name == "Stripe"

    def test_is_configured_with_key(self):
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway
        gw = StripeGateway(api_key="sk_test_xxx")
        assert gw.is_configured()

    def test_not_configured_without_key(self):
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway
        gw = StripeGateway(api_key=None)
        assert not gw.is_configured()

    def test_payment_methods(self):
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway
        gw = StripeGateway(api_key="sk_test_xxx")
        methods = gw.get_payment_methods()
        assert len(methods) >= 2
        ids = [m.id for m in methods]
        assert "card" in ids
        assert "blik" in ids

    def test_implements_contract(self):
        from fasthub_core.billing.payment_gateway import PaymentGateway
        from fasthub_core.billing.gateways.stripe_gateway import StripeGateway
        assert issubclass(StripeGateway, PaymentGateway)


# ============================================================================
# STRIPE WEBHOOK HANDLER
# ============================================================================

class TestStripeWebhookHandler:

    def test_class_exists(self):
        from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
        assert StripeWebhookHandler is not None

    def test_hook_points_exist(self):
        from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
        handler = StripeWebhookHandler(db=MagicMock())
        assert hasattr(handler, "on_checkout_completed")
        assert hasattr(handler, "on_subscription_canceled")
        assert hasattr(handler, "on_payment_failed")
        assert hasattr(handler, "on_payment_succeeded")

    def test_hooks_default_none(self):
        from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
        handler = StripeWebhookHandler(db=MagicMock())
        assert handler.on_checkout_completed is None
        assert handler.on_subscription_canceled is None
        assert handler.on_payment_failed is None
        assert handler.on_payment_succeeded is None

    def test_hooks_settable(self):
        from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
        handler = StripeWebhookHandler(db=MagicMock())
        mock_hook = AsyncMock()
        handler.on_checkout_completed = mock_hook
        assert handler.on_checkout_completed is mock_hook

    def test_extract_tenant_id(self):
        from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
        handler = StripeWebhookHandler(db=MagicMock())
        assert handler._extract_tenant_id({"metadata": {"tenant_id": "org-123"}}) == "org-123"
        assert handler._extract_tenant_id({}) == "unknown"
        assert handler._extract_tenant_id({"metadata": {}}) == "unknown"

    def test_all_handlers_exist(self):
        from fasthub_core.billing.stripe_webhooks import StripeWebhookHandler
        handler = StripeWebhookHandler(db=MagicMock())
        assert hasattr(handler, "_handle_checkout_completed")
        assert hasattr(handler, "_handle_subscription_updated")
        assert hasattr(handler, "_handle_subscription_deleted")
        assert hasattr(handler, "_handle_payment_failed")
        assert hasattr(handler, "_handle_payment_succeeded")
        assert callable(handler.process)


# ============================================================================
# BILLING SERVICE — DELEGACJA
# ============================================================================

class TestBillingServiceDelegation:

    def test_has_webhook_method(self):
        from fasthub_core.billing.service import BillingService
        assert hasattr(BillingService, "handle_stripe_webhook")

    def test_has_checkout_method(self):
        from fasthub_core.billing.service import BillingService
        assert hasattr(BillingService, "create_checkout_session")

    def test_checkout_accepts_new_params(self):
        import inspect
        from fasthub_core.billing.service import BillingService
        sig = inspect.signature(BillingService.create_checkout_session)
        params = list(sig.parameters.keys())
        assert "addon_slug" in params
        assert "billing_interval" in params
        assert "plan_slug" in params
        assert "quantity" in params


# ============================================================================
# SHARED HTTP CLIENTS
# ============================================================================

class TestBaseHTTPClient:

    def test_create(self):
        from fasthub_core.clients.base_client import BaseHTTPClient
        client = BaseHTTPClient(base_url="https://example.com")
        assert client.base_url == "https://example.com"

    def test_strips_trailing_slash(self):
        from fasthub_core.clients.base_client import BaseHTTPClient
        client = BaseHTTPClient(base_url="https://example.com/")
        assert client.base_url == "https://example.com"

    def test_default_headers(self):
        from fasthub_core.clients.base_client import BaseHTTPClient
        client = BaseHTTPClient(
            base_url="https://example.com",
            default_headers={"Authorization": "Bearer xxx"},
        )
        assert "Authorization" in client.default_headers

    def test_has_crud_methods(self):
        from fasthub_core.clients.base_client import BaseHTTPClient
        client = BaseHTTPClient(base_url="https://example.com")
        assert callable(client.get)
        assert callable(client.post)
        assert callable(client.put)
        assert callable(client.delete)

    def test_custom_timeout(self):
        from fasthub_core.clients.base_client import BaseHTTPClient
        client = BaseHTTPClient(base_url="https://example.com", timeout=60.0)
        assert client.timeout == 60.0


class TestFakturowniaClient:

    def test_create(self):
        from fasthub_core.clients.fakturownia_client import FakturowniaClient
        client = FakturowniaClient(account="testfirma", api_token="abc123")
        assert client.account == "testfirma"
        assert "testfirma.fakturownia.pl" in client.base_url

    def test_from_config_requires_env(self):
        from fasthub_core.clients.fakturownia_client import FakturowniaClient
        try:
            FakturowniaClient.from_config()
        except ValueError:
            pass  # Expected — brak env vars

    def test_invoice_methods(self):
        from fasthub_core.clients.fakturownia_client import FakturowniaClient
        client = FakturowniaClient(account="test", api_token="xxx")
        assert callable(client.create_invoice)
        assert callable(client.get_invoice)
        assert callable(client.list_invoices)
        assert callable(client.send_invoice_by_email)

    def test_with_token(self):
        from fasthub_core.clients.fakturownia_client import FakturowniaClient
        client = FakturowniaClient(account="test", api_token="my_token")
        params = client._with_token({"page": 1})
        assert params["api_token"] == "my_token"
        assert params["page"] == 1


class TestStripeClientClass:

    def test_class_exists(self):
        from fasthub_core.clients.stripe_client import StripeClient
        assert StripeClient is not None

    def test_has_methods(self):
        from fasthub_core.clients.stripe_client import StripeClient
        assert hasattr(StripeClient, "create_checkout_session")
        assert hasattr(StripeClient, "create_portal_session")
        assert hasattr(StripeClient, "construct_webhook_event")
        assert hasattr(StripeClient, "create_customer")


# ============================================================================
# SUBSCRIPTION STATUS
# ============================================================================

class TestSubscriptionStatus:

    def test_all_stripe_statuses(self):
        from fasthub_core.billing.models import SubscriptionStatus
        assert hasattr(SubscriptionStatus, "active")
        assert hasattr(SubscriptionStatus, "canceled")
        assert hasattr(SubscriptionStatus, "past_due")
        assert hasattr(SubscriptionStatus, "trialing")

    def test_billing_event_unique(self):
        from fasthub_core.billing.models import BillingEvent
        col = BillingEvent.__table__.columns["stripe_event_id"]
        assert col.unique is True


# ============================================================================
# EXPORTS
# ============================================================================

class TestExports:

    def test_billing_exports(self):
        from fasthub_core.billing import (
            StripeWebhookHandler, PaymentGateway, PaymentGatewayRegistry,
            PaymentStatus, PaymentResult, StripeGateway,
            get_payment_registry, WebhookResult, PaymentMethod,
        )
        assert StripeWebhookHandler is not None
        assert PaymentGateway is not None
        assert PaymentGatewayRegistry is not None
        assert StripeGateway is not None

    def test_clients_exports(self):
        from fasthub_core.clients import BaseHTTPClient, FakturowniaClient, StripeClient
        assert BaseHTTPClient is not None
        assert FakturowniaClient is not None
        assert StripeClient is not None

    def test_gateways_init(self):
        from fasthub_core.billing.gateways import StripeGateway
        assert StripeGateway is not None
