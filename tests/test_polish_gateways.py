"""
Testy Brief 20: Polskie bramki platnicze (PayU, Tpay, P24, PayPal) + RecurringManager.

~44 testy:
- PayU Gateway: 8
- Tpay Gateway: 8
- P24 Gateway: 8
- PayPal Gateway: 8
- HTTP Clients: 4
- RecurringManager: 8
- Registry integration: 4
"""

import hashlib
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta


# ============================================================================
# PayU Gateway Tests (8)
# ============================================================================

class TestPayUGateway:

    def test_gateway_class_exists(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        assert PayUGateway is not None

    def test_gateway_id(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        gw = PayUGateway()
        assert gw.gateway_id == "payu"

    def test_display_name(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        gw = PayUGateway()
        assert gw.display_name == "PayU"

    def test_implements_payment_gateway(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        from fasthub_core.billing.payment_gateway import PaymentGateway
        assert issubclass(PayUGateway, PaymentGateway)

    def test_is_configured_without_keys(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        gw = PayUGateway()
        assert gw.is_configured() is False

    def test_get_payment_methods(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        gw = PayUGateway()
        methods = gw.get_payment_methods()
        method_ids = [m.id for m in methods]
        assert "blik" in method_ids
        assert "card" in method_ids
        assert "transfer" in method_ids
        assert "google_pay" in method_ids
        assert "apple_pay" in method_ids

    @pytest.mark.asyncio
    async def test_create_payment_mock(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        gw = PayUGateway()
        gw._pos_id = "123456"
        gw._md5_key = "abc123"
        gw._client_id = "123456"
        gw._client_secret = "xyz789"

        mock_response = {
            "redirectUri": "https://payu.com/pay/123",
            "orderId": "ORDER-123",
            "status": {"statusCode": "SUCCESS"},
        }

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = AsyncMock()
            client_instance.create_order = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await gw.create_payment(
                amount=19900, currency="PLN",
                description="Plan Pro", return_url="https://app.test/success",
                metadata={"notify_url": "https://app.test/webhook", "buyer_email": "test@test.pl"},
            )
            assert result.success is True
            assert result.payment_id == "ORDER-123"
            assert result.payment_url == "https://payu.com/pay/123"
            assert result.gateway_id == "payu"

    @pytest.mark.asyncio
    async def test_handle_webhook_mock(self):
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        from fasthub_core.billing.payment_gateway import PaymentStatus
        gw = PayUGateway()
        gw._pos_id = "123456"
        gw._md5_key = "testkey"
        gw._client_id = "123456"
        gw._client_secret = "xyz789"

        payload_dict = {
            "order": {
                "orderId": "ORDER-123",
                "status": "COMPLETED",
            },
            "properties": [
                {"name": "tenant_id", "value": "org-abc"},
            ],
        }
        payload = json.dumps(payload_dict).encode()

        # Compute valid signature
        concat = payload.decode() + "testkey"
        sig = hashlib.md5(concat.encode()).hexdigest()
        headers = {"openpayu-signature": f"signature={sig};algorithm=MD5"}

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = MagicMock()
            client_instance.verify_notification = MagicMock(return_value=True)
            mock_client.return_value = client_instance

            result = await gw.handle_webhook(payload, headers)
            assert result.status == "processed"
            assert result.payment_status == PaymentStatus.completed
            assert result.payment_id == "ORDER-123"


# ============================================================================
# Tpay Gateway Tests (8)
# ============================================================================

class TestTpayGateway:

    def test_gateway_class_exists(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        assert TpayGateway is not None

    def test_gateway_id(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        gw = TpayGateway()
        assert gw.gateway_id == "tpay"

    def test_display_name(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        gw = TpayGateway()
        assert gw.display_name == "Tpay"

    def test_implements_payment_gateway(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        from fasthub_core.billing.payment_gateway import PaymentGateway
        assert issubclass(TpayGateway, PaymentGateway)

    def test_is_configured_without_keys(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        gw = TpayGateway()
        assert gw.is_configured() is False

    def test_get_payment_methods(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        gw = TpayGateway()
        methods = gw.get_payment_methods()
        method_ids = [m.id for m in methods]
        assert "blik" in method_ids
        assert "card" in method_ids
        assert "transfer" in method_ids

    @pytest.mark.asyncio
    async def test_create_payment_mock(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        gw = TpayGateway()
        gw._client_id = "test_id"
        gw._client_secret = "test_secret"
        gw._security_code = "test_code"

        mock_response = {
            "transactionId": "TXN-456",
            "transactionPaymentUrl": "https://tpay.com/pay/456",
        }

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = AsyncMock()
            client_instance.create_transaction = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await gw.create_payment(
                amount=19900, currency="PLN",
                description="Plan Pro", return_url="https://app.test/success",
                metadata={"notify_url": "https://app.test/webhook", "buyer_email": "test@test.pl"},
            )
            assert result.success is True
            assert result.payment_id == "TXN-456"
            assert result.payment_url == "https://tpay.com/pay/456"
            assert result.gateway_id == "tpay"

    @pytest.mark.asyncio
    async def test_handle_webhook_mock(self):
        from fasthub_core.billing.gateways.tpay_gateway import TpayGateway
        from fasthub_core.billing.payment_gateway import PaymentStatus
        gw = TpayGateway()
        gw._client_id = "test_id"
        gw._client_secret = "test_secret"
        gw._security_code = "test_code"

        payload_dict = {
            "tr_id": "TXN-456",
            "tr_status": "TRUE",
            "tr_amount": "199.00",
            "tr_crc": "org-abc",
            "md5sum": "computed_hash",
        }
        payload = json.dumps(payload_dict).encode()

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = MagicMock()
            client_instance.verify_callback = MagicMock(return_value=True)
            mock_client.return_value = client_instance

            result = await gw.handle_webhook(payload, {})
            assert result.status == "processed"
            assert result.payment_status == PaymentStatus.completed
            assert result.payment_id == "TXN-456"
            assert result.tenant_id == "org-abc"


# ============================================================================
# P24 Gateway Tests (8)
# ============================================================================

class TestP24Gateway:

    def test_gateway_class_exists(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        assert P24Gateway is not None

    def test_gateway_id(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        gw = P24Gateway()
        assert gw.gateway_id == "p24"

    def test_display_name(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        gw = P24Gateway()
        assert gw.display_name == "Przelewy24"

    def test_implements_payment_gateway(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        from fasthub_core.billing.payment_gateway import PaymentGateway
        assert issubclass(P24Gateway, PaymentGateway)

    def test_is_configured_without_keys(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        gw = P24Gateway()
        assert gw.is_configured() is False

    def test_get_payment_methods(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        gw = P24Gateway()
        methods = gw.get_payment_methods()
        method_ids = [m.id for m in methods]
        assert "blik" in method_ids
        assert "card" in method_ids
        assert "transfer" in method_ids

    @pytest.mark.asyncio
    async def test_create_payment_mock(self):
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        gw = P24Gateway()
        gw._merchant_id = "123456"
        gw._pos_id = "123456"
        gw._crc_key = "testcrc"

        mock_response = {"data": {"token": "TOKEN-789"}}

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = AsyncMock()
            client_instance.register_transaction = AsyncMock(return_value=mock_response)
            client_instance.get_payment_url = MagicMock(return_value="https://p24.pl/trnRequest/TOKEN-789")
            mock_client.return_value = client_instance

            result = await gw.create_payment(
                amount=19900, currency="PLN",
                description="Plan Pro", return_url="https://app.test/success",
                metadata={
                    "notify_url": "https://app.test/webhook",
                    "buyer_email": "test@test.pl",
                    "session_id": "SESSION-001",
                },
            )
            assert result.success is True
            assert result.payment_url == "https://p24.pl/trnRequest/TOKEN-789"
            assert result.gateway_id == "p24"

    @pytest.mark.asyncio
    async def test_handle_webhook_with_verify(self):
        """P24 MUST call verify_transaction after callback."""
        from fasthub_core.billing.gateways.p24_gateway import P24Gateway
        from fasthub_core.billing.payment_gateway import PaymentStatus
        gw = P24Gateway()
        gw._merchant_id = "123456"
        gw._pos_id = "123456"
        gw._crc_key = "testcrc"

        payload_dict = {
            "sessionId": "SESSION-001",
            "orderId": 999,
            "amount": 19900,
            "currency": "PLN",
            "sign": "computed_hash",
            "statement": "org-abc",
        }
        payload = json.dumps(payload_dict).encode()

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = AsyncMock()
            client_instance.verify_callback = MagicMock(return_value=True)
            client_instance.verify_transaction = AsyncMock(return_value={"data": {"status": "success"}})
            mock_client.return_value = client_instance

            result = await gw.handle_webhook(payload, {})
            assert result.status == "processed"
            assert result.payment_status == PaymentStatus.completed
            assert result.event_type == "p24.transaction.verified"
            # verify_transaction MUST have been called
            client_instance.verify_transaction.assert_called_once()


# ============================================================================
# PayPal Gateway Tests (8)
# ============================================================================

class TestPayPalGateway:

    def test_gateway_class_exists(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        assert PayPalGateway is not None

    def test_gateway_id(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        gw = PayPalGateway()
        assert gw.gateway_id == "paypal"

    def test_display_name(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        gw = PayPalGateway()
        assert gw.display_name == "PayPal"

    def test_implements_payment_gateway(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        from fasthub_core.billing.payment_gateway import PaymentGateway
        assert issubclass(PayPalGateway, PaymentGateway)

    def test_is_configured_without_keys(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        gw = PayPalGateway()
        assert gw.is_configured() is False

    def test_get_payment_methods(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        gw = PayPalGateway()
        methods = gw.get_payment_methods()
        method_ids = [m.id for m in methods]
        assert "paypal" in method_ids
        assert "card" in method_ids

    @pytest.mark.asyncio
    async def test_create_payment_mock(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        gw = PayPalGateway()
        gw._client_id = "test_id"
        gw._client_secret = "test_secret"

        mock_response = {
            "id": "PAYPAL-ORDER-123",
            "links": [
                {"rel": "approve", "href": "https://paypal.com/approve/123"},
                {"rel": "self", "href": "https://api.paypal.com/v2/checkout/orders/123"},
            ],
        }

        with patch.object(gw, "_get_client") as mock_client:
            client_instance = AsyncMock()
            client_instance.create_order = AsyncMock(return_value=mock_response)
            mock_client.return_value = client_instance

            result = await gw.create_payment(
                amount=19900, currency="PLN",
                description="Plan Pro", return_url="https://app.test/success",
            )
            assert result.success is True
            assert result.payment_id == "PAYPAL-ORDER-123"
            assert result.payment_url == "https://paypal.com/approve/123"
            assert result.gateway_id == "paypal"

    @pytest.mark.asyncio
    async def test_handle_webhook_mock(self):
        from fasthub_core.billing.gateways.paypal_gateway import PayPalGateway
        from fasthub_core.billing.payment_gateway import PaymentStatus
        gw = PayPalGateway()

        payload_dict = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAPTURE-123",
                "custom_id": "org-abc",
            },
        }
        payload = json.dumps(payload_dict).encode()

        result = await gw.handle_webhook(payload, {})
        assert result.status == "processed"
        assert result.payment_status == PaymentStatus.completed
        assert result.event_type == "PAYMENT.CAPTURE.COMPLETED"


# ============================================================================
# HTTP Clients Tests (4)
# ============================================================================

class TestHTTPClients:

    def test_payu_client_exists(self):
        from fasthub_core.clients.payu_client import PayUClient
        client = PayUClient(
            pos_id="123", md5_key="abc", client_id="123", client_secret="xyz"
        )
        assert client.base_url == "https://secure.snd.payu.com"

    def test_tpay_client_exists(self):
        from fasthub_core.clients.tpay_client import TpayClient
        client = TpayClient(
            client_id="test", client_secret="test", security_code="test"
        )
        assert client.base_url == "https://openapi.sandbox.tpay.com"

    def test_p24_client_exists(self):
        from fasthub_core.clients.p24_client import P24Client
        client = P24Client(
            merchant_id="123", pos_id="123", crc_key="abc"
        )
        assert client.base_url == "https://sandbox.przelewy24.pl"

    def test_paypal_client_exists(self):
        from fasthub_core.clients.paypal_client import PayPalClient
        client = PayPalClient(
            client_id="test", client_secret="test"
        )
        assert client.base_url == "https://api-m.sandbox.paypal.com"


# ============================================================================
# RecurringManager Tests (8)
# ============================================================================

class TestRecurringManager:

    def test_recurring_manager_exists(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        assert RecurringManager is not None

    def test_native_gateways_excluded(self):
        from fasthub_core.billing.recurring_manager import NATIVE_SUBSCRIPTION_GATEWAYS
        assert "stripe" in NATIVE_SUBSCRIPTION_GATEWAYS
        assert "paypal" in NATIVE_SUBSCRIPTION_GATEWAYS
        assert "payu" not in NATIVE_SUBSCRIPTION_GATEWAYS
        assert "tpay" not in NATIVE_SUBSCRIPTION_GATEWAYS

    def test_parse_reminder_days(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        result = RecurringManager._parse_reminder_days("1,3,7")
        assert result == [1, 3, 7]

    def test_parse_reminder_days_invalid(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        result = RecurringManager._parse_reminder_days("invalid")
        assert result == [1, 3, 7]

    @pytest.mark.asyncio
    async def test_process_renewals_empty(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        db = AsyncMock()

        manager = RecurringManager(db)

        mock_settings = MagicMock()
        mock_settings.RECURRING_GRACE_DAYS = 14
        mock_settings.RECURRING_REMINDER_DAYS = "1,3,7"

        with patch("fasthub_core.config.get_settings", return_value=mock_settings), \
             patch.object(manager, "_get_due_subscriptions", return_value=[]):
            results = await manager.process_renewals()
            assert results["processed"] == 0
            assert results["errors"] == 0

    @pytest.mark.asyncio
    async def test_handle_renewal_paid(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        db = AsyncMock()

        manager = RecurringManager(db)

        sub = MagicMock()
        sub.billing_interval = "monthly"
        sub.current_period_end = datetime(2026, 3, 1)
        sub.renewal_failures = 2

        await manager.handle_renewal_paid(sub)

        expected_end = datetime(2026, 3, 1) + timedelta(days=30)
        assert sub.current_period_end == expected_end
        assert sub.status == "active"
        assert sub.renewal_failures == 0

    @pytest.mark.asyncio
    async def test_handle_renewal_paid_yearly(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        db = AsyncMock()

        manager = RecurringManager(db)

        sub = MagicMock()
        sub.billing_interval = "yearly"
        sub.current_period_end = datetime(2026, 3, 1)
        sub.renewal_failures = 0

        await manager.handle_renewal_paid(sub)

        expected_end = datetime(2026, 3, 1) + timedelta(days=365)
        assert sub.current_period_end == expected_end

    @pytest.mark.asyncio
    async def test_create_renewal_payment_skips_stripe(self):
        from fasthub_core.billing.recurring_manager import RecurringManager
        db = AsyncMock()
        manager = RecurringManager(db)

        sub = MagicMock()
        sub.gateway_id = "stripe"

        result = await manager.create_renewal_payment(sub)
        assert result is None


# ============================================================================
# Registry Integration Tests (4)
# ============================================================================

class TestRegistryIntegration:

    def test_registry_from_config_no_keys(self):
        """Without API keys, no gateways should be registered."""
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        registry = PaymentGatewayRegistry()
        from fasthub_core.billing.gateways.payu_gateway import PayUGateway
        registry.register(PayUGateway())  # no keys -> skip
        assert len(registry.get_active_gateways()) == 0

    def test_registry_dedup_methods(self):
        """BLIK should appear only once even from multiple gateways."""
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.payment_gateway import PaymentMethod

        registry = PaymentGatewayRegistry()

        # Mock two configured gateways with overlapping BLIK
        gw1 = MagicMock()
        gw1.gateway_id = "payu"
        gw1.display_name = "PayU"
        gw1.is_configured.return_value = True
        gw1.get_payment_methods.return_value = [
            PaymentMethod(id="blik", name="BLIK", gateway_id="payu"),
            PaymentMethod(id="card", name="Karta", gateway_id="payu"),
        ]

        gw2 = MagicMock()
        gw2.gateway_id = "tpay"
        gw2.display_name = "Tpay"
        gw2.is_configured.return_value = True
        gw2.get_payment_methods.return_value = [
            PaymentMethod(id="blik", name="BLIK", gateway_id="tpay"),
            PaymentMethod(id="transfer", name="Przelew", gateway_id="tpay"),
        ]

        registry.register(gw1)
        registry.register(gw2)

        methods = registry.get_available_methods()
        blik_count = sum(1 for m in methods if m.id == "blik")
        assert blik_count == 1
        assert len(methods) == 3  # blik, card, transfer

    def test_registry_webhook_routing(self):
        """Webhook should be routed to correct gateway."""
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry

        registry = PaymentGatewayRegistry()

        gw1 = MagicMock()
        gw1.gateway_id = "payu"
        gw1.display_name = "PayU"
        gw1.is_configured.return_value = True
        registry.register(gw1)

        assert registry.get_gateway("payu") is gw1
        assert registry.get_gateway("tpay") is None

    def test_registry_methods_with_gateways(self):
        """get_methods_with_gateways should show which gateways support each method."""
        from fasthub_core.billing.payment_registry import PaymentGatewayRegistry
        from fasthub_core.billing.payment_gateway import PaymentMethod

        registry = PaymentGatewayRegistry()

        gw1 = MagicMock()
        gw1.gateway_id = "payu"
        gw1.display_name = "PayU"
        gw1.is_configured.return_value = True
        gw1.get_payment_methods.return_value = [
            PaymentMethod(id="blik", name="BLIK", gateway_id="payu"),
        ]

        gw2 = MagicMock()
        gw2.gateway_id = "tpay"
        gw2.display_name = "Tpay"
        gw2.is_configured.return_value = True
        gw2.get_payment_methods.return_value = [
            PaymentMethod(id="blik", name="BLIK", gateway_id="tpay"),
        ]

        registry.register(gw1)
        registry.register(gw2)

        methods_with_gw = registry.get_methods_with_gateways()
        assert len(methods_with_gw) == 1
        assert "payu" in methods_with_gw[0]["gateways"]
        assert "tpay" in methods_with_gw[0]["gateways"]


# ============================================================================
# Config Tests (2)
# ============================================================================

class TestConfig:

    def test_payu_config_fields(self):
        from fasthub_core.config import Settings
        import inspect
        source = inspect.getsource(Settings)
        for field in ["PAYU_POS_ID", "PAYU_MD5_KEY", "PAYU_CLIENT_ID", "PAYU_CLIENT_SECRET", "PAYU_SANDBOX"]:
            assert field in source, f"Missing config: {field}"

    def test_recurring_config_fields(self):
        from fasthub_core.config import Settings
        import inspect
        source = inspect.getsource(Settings)
        assert "RECURRING_GRACE_DAYS" in source
        assert "RECURRING_REMINDER_DAYS" in source


# ============================================================================
# Subscription Model Tests (2)
# ============================================================================

class TestSubscriptionModel:

    def test_subscription_has_gateway_fields(self):
        from fasthub_core.billing.models import Subscription
        import inspect
        source = inspect.getsource(Subscription)
        for field in ["gateway_id", "amount", "currency", "gateway_customer_id",
                       "gateway_payment_token", "last_renewal_attempt",
                       "renewal_failures", "grace_period_end"]:
            assert field in source, f"Subscription missing field: {field}"

    def test_subscription_status_enum(self):
        from fasthub_core.billing.models import SubscriptionStatus
        assert SubscriptionStatus.active == "active"
        assert SubscriptionStatus.past_due == "past_due"
        assert SubscriptionStatus.canceled == "canceled"
