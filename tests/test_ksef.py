"""
Testy Brief 21: KSeF (Krajowy System e-Faktur).

~27 testow:
- KSeFClient: 10
- KSeFXMLBuilder: 8
- KSeFInvoiceHook: 4
- Invoice Router: 3
- Exports: 2
"""

import base64
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ============================================================================
# KSeFClient Tests (10)
# ============================================================================

class TestKSeFClient:

    def test_client_class_exists(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        assert KSeFClient is not None

    def test_inherits_base_http_client(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        from fasthub_core.clients.base_client import BaseHTTPClient
        assert issubclass(KSeFClient, BaseHTTPClient)

    def test_env_urls_mapping(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        assert "prod" in KSeFClient.ENV_URLS
        assert "demo" in KSeFClient.ENV_URLS
        assert "test" in KSeFClient.ENV_URLS
        assert "ksef.mf.gov.pl" in KSeFClient.ENV_URLS["prod"]
        assert "ksef-demo" in KSeFClient.ENV_URLS["demo"]
        assert "ksef-test" in KSeFClient.ENV_URLS["test"]

    def test_init_test_environment(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="1234567890", auth_token="test-token", environment="test")
        assert client.base_url == "https://ksef-test.mf.gov.pl/api/v2"
        assert client.nip == "1234567890"
        assert client.environment == "test"

    def test_init_prod_environment(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="123-456-78-90", auth_token="token", environment="prod")
        assert client.base_url == "https://ksef.mf.gov.pl/api/v2"
        assert client.nip == "1234567890"  # stripped dashes

    def test_is_configured_with_token(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="1234567890", auth_token="test-token")
        assert client.is_configured() is True

    def test_is_configured_without_token(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="1234567890")
        assert client.is_configured() is False

    def test_is_configured_with_certificate(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="1234567890", auth_method="certificate",
                            certificate_base64="cert-data")
        assert client.is_configured() is True

    def test_session_headers_without_token(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="1234567890", auth_token="test")
        assert "Authorization" not in client.default_headers
        assert client.default_headers["Content-Type"] == "application/json"

    def test_session_headers_with_token(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        client = KSeFClient(nip="1234567890", auth_token="test")
        client._access_token = "jwt-token-abc"
        client._update_session_token()
        assert client.default_headers["Authorization"] == "Bearer jwt-token-abc"


# ============================================================================
# KSeFXMLBuilder Tests (8)
# ============================================================================

class TestKSeFXMLBuilder:

    def test_builder_class_exists(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        assert KSeFXMLBuilder is not None

    def test_build_single_position(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        builder = KSeFXMLBuilder()
        result = builder.build(
            seller_nip="1234567890",
            seller_name="Firma Test",
            buyer_nip="9876543210",
            buyer_name="Klient Test",
            issue_date="2026-03-02",
            sale_date="2026-03-02",
            positions=[
                {"name": "Plan Pro", "quantity": 1, "unit": "szt",
                 "price_net": 100.0, "vat_rate": 23},
            ],
        )
        assert "invoice_xml" in result
        assert "invoice_xml_base64" in result
        assert "summary" in result
        assert result["summary"]["total_net"] == 100.0
        assert result["summary"]["total_vat"] == 23.0
        assert result["summary"]["total_gross"] == 123.0
        assert result["summary"]["positions_count"] == 1

    def test_build_multiple_positions(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        builder = KSeFXMLBuilder()
        result = builder.build(
            seller_nip="1234567890",
            seller_name="Firma",
            buyer_nip="9876543210",
            buyer_name="Klient",
            issue_date="2026-03-02",
            sale_date="2026-03-02",
            positions=[
                {"name": "Plan Pro", "quantity": 1, "unit": "szt",
                 "price_net": 100.0, "vat_rate": 23},
                {"name": "Addon AI", "quantity": 2, "unit": "szt",
                 "price_net": 50.0, "vat_rate": 23},
            ],
        )
        # 100 + 2*50 = 200 net, 46 VAT
        assert result["summary"]["total_net"] == 200.0
        assert result["summary"]["total_vat"] == 46.0
        assert result["summary"]["total_gross"] == 246.0
        assert result["summary"]["positions_count"] == 2

    def test_build_vat_zero(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        builder = KSeFXMLBuilder()
        result = builder.build(
            seller_nip="1234567890",
            seller_name="Firma",
            buyer_nip="9876543210",
            buyer_name="Klient",
            issue_date="2026-03-02",
            sale_date="2026-03-02",
            positions=[
                {"name": "Export", "quantity": 1, "unit": "szt",
                 "price_net": 500.0, "vat_rate": 0},
            ],
        )
        assert result["summary"]["total_vat"] == 0
        assert result["summary"]["total_gross"] == 500.0

    def test_build_optional_fields(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        builder = KSeFXMLBuilder()
        result = builder.build(
            seller_nip="1234567890",
            seller_name="Firma",
            buyer_nip="9876543210",
            buyer_name="Klient",
            issue_date="2026-03-02",
            sale_date="2026-03-02",
            positions=[{"name": "Test", "quantity": 1, "unit": "szt",
                         "price_net": 10.0, "vat_rate": 23}],
            payment_method="przelew",
            payment_deadline="2026-03-16",
            bank_account="PL12345678901234567890123456",
            notes="Uwaga testowa",
            system_info="TestSystem",
        )
        xml = result["invoice_xml"]
        assert "przelew" in xml
        assert "2026-03-16" in xml
        assert "PL12345678901234567890123456" in xml
        assert "Uwaga testowa" in xml
        assert "TestSystem" in xml

    def test_base64_encoding(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        builder = KSeFXMLBuilder()
        result = builder.build(
            seller_nip="1234567890",
            seller_name="Test",
            buyer_nip="9876543210",
            buyer_name="Test",
            issue_date="2026-03-02",
            sale_date="2026-03-02",
            positions=[{"name": "X", "quantity": 1, "unit": "szt",
                         "price_net": 10.0, "vat_rate": 23}],
        )
        decoded = base64.b64decode(result["invoice_xml_base64"]).decode("utf-8")
        assert decoded == result["invoice_xml"]

    def test_validate_nip_correct(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        # 5252344078 to poprawny NIP (PKP)
        assert KSeFXMLBuilder.validate_nip("5252344078") is True

    def test_validate_nip_incorrect(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        assert KSeFXMLBuilder.validate_nip("1234567890") is False
        assert KSeFXMLBuilder.validate_nip("123") is False
        assert KSeFXMLBuilder.validate_nip("abcdefghij") is False

    def test_validate_nip_with_dashes(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        assert KSeFXMLBuilder.validate_nip("525-234-40-78") is True

    def test_validate_positions_valid(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        errors = KSeFXMLBuilder.validate_positions([
            {"name": "Plan Pro", "quantity": 1, "price_net": 199.0, "vat_rate": 23},
        ])
        assert errors == []

    def test_validate_positions_errors(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        errors = KSeFXMLBuilder.validate_positions([
            {"name": "", "quantity": 1, "price_net": 199.0, "vat_rate": 23},
            {"name": "Test", "quantity": 0, "price_net": 0, "vat_rate": 99},
        ])
        assert len(errors) >= 3  # brak nazwy, cena 0, ilosc 0, stawka VAT


# ============================================================================
# KSeFInvoiceHook Tests (4)
# ============================================================================

class TestKSeFInvoiceHook:

    def test_hook_class_exists(self):
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        assert KSeFInvoiceHook is not None

    @pytest.mark.asyncio
    async def test_handle_skip_no_config(self):
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        db = AsyncMock()
        hook = KSeFInvoiceHook(db)

        mock_settings = MagicMock()
        mock_settings.KSEF_NIP = None
        mock_settings.KSEF_AUTH_TOKEN = None

        with patch("fasthub_core.config.get_settings", return_value=mock_settings):
            result = await hook.handle({"tenant_id": "org-123", "amount": 19900})
            assert result is None

    @pytest.mark.asyncio
    async def test_handle_skip_no_nip(self):
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        db = AsyncMock()
        hook = KSeFInvoiceHook(db)

        mock_settings = MagicMock()
        mock_settings.KSEF_NIP = "1234567890"
        mock_settings.KSEF_AUTH_TOKEN = "test-token"
        mock_settings.APP_NAME = "FastHub"

        org = MagicMock()
        org.nip = None
        org.name = "Test Org"

        with patch("fasthub_core.config.get_settings", return_value=mock_settings), \
             patch.object(hook, "_get_organization", return_value=org):
            result = await hook.handle({"tenant_id": "org-123", "amount": 19900})
            assert result is None

    @pytest.mark.asyncio
    async def test_handle_happy_path(self):
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        db = AsyncMock()
        hook = KSeFInvoiceHook(db)

        mock_settings = MagicMock()
        mock_settings.KSEF_NIP = "1234567890"
        mock_settings.KSEF_AUTH_TOKEN = "test-token"
        mock_settings.KSEF_ENVIRONMENT = "test"
        mock_settings.KSEF_AUTH_METHOD = "token"
        mock_settings.KSEF_CERTIFICATE_BASE64 = ""
        mock_settings.KSEF_PRIVATE_KEY_BASE64 = ""
        mock_settings.INVOICE_SELLER_NAME = "FastHub Sp. z o.o."
        mock_settings.INVOICE_BANK_ACCOUNT = "PL12345"
        mock_settings.APP_NAME = "FastHub"

        org = MagicMock()
        org.nip = "9876543210"
        org.name = "Klient Test"

        mock_client = AsyncMock()
        mock_client.validate_invoice = AsyncMock(return_value={})
        mock_client.open_session = AsyncMock(return_value={"referenceNumber": "REF-001"})
        mock_client.send_invoice = AsyncMock(return_value={"elementReferenceNumber": "KSEF-12345"})
        mock_client.close_session = AsyncMock(return_value={})
        mock_client.get_upo = AsyncMock(return_value={"upo": "data"})

        with patch("fasthub_core.config.get_settings", return_value=mock_settings), \
             patch.object(hook, "_get_organization", return_value=org), \
             patch("fasthub_core.clients.ksef_client.KSeFClient.from_config", return_value=mock_client):

            result = await hook.handle({
                "tenant_id": "org-123",
                "amount": 24600,
                "plan_name": "Plan Pro",
                "currency": "PLN",
            })

            assert result is not None
            assert result["ksef_number"] == "KSEF-12345"
            assert result["reference_number"] == "REF-001"
            mock_client.open_session.assert_called_once()
            mock_client.send_invoice.assert_called_once()
            mock_client.close_session.assert_called_once()


# ============================================================================
# Invoice Router Tests (3)
# ============================================================================

class TestInvoiceRouter:

    def test_get_invoice_hook_none(self):
        from fasthub_core.billing.invoice_router import get_invoice_hook
        mock_settings = MagicMock()
        mock_settings.INVOICE_BACKEND = "none"

        with patch("fasthub_core.config.get_settings", return_value=mock_settings):
            hook = get_invoice_hook(db=MagicMock())
            assert hook is None

    def test_get_invoice_hook_ksef(self):
        from fasthub_core.billing.invoice_router import get_invoice_hook
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        mock_settings = MagicMock()
        mock_settings.INVOICE_BACKEND = "ksef"

        with patch("fasthub_core.config.get_settings", return_value=mock_settings):
            hook = get_invoice_hook(db=MagicMock())
            assert isinstance(hook, KSeFInvoiceHook)

    def test_get_invoice_hook_fakturownia(self):
        from fasthub_core.billing.invoice_router import get_invoice_hook
        from fasthub_core.billing.invoice_hook import AutoInvoiceHook
        mock_settings = MagicMock()
        mock_settings.INVOICE_BACKEND = "fakturownia"

        with patch("fasthub_core.config.get_settings", return_value=mock_settings):
            hook = get_invoice_hook(db=MagicMock())
            assert isinstance(hook, AutoInvoiceHook)


# ============================================================================
# Config Tests (2)
# ============================================================================

class TestKSeFConfig:

    def test_ksef_config_fields(self):
        from fasthub_core.config import Settings
        import inspect
        source = inspect.getsource(Settings)
        for field in ["KSEF_NIP", "KSEF_AUTH_TOKEN", "KSEF_ENVIRONMENT",
                       "KSEF_AUTH_METHOD", "INVOICE_BACKEND"]:
            assert field in source, f"Missing config: {field}"

    def test_invoice_backend_config(self):
        from fasthub_core.config import Settings
        import inspect
        source = inspect.getsource(Settings)
        assert "INVOICE_SELLER_NAME" in source
        assert "INVOICE_BANK_ACCOUNT" in source


# ============================================================================
# Exports Tests (2)
# ============================================================================

class TestExports:

    def test_ksef_client_importable(self):
        from fasthub_core.clients.ksef_client import KSeFClient
        from fasthub_core.clients import KSeFClient as KC2
        assert KSeFClient is KC2

    def test_ksef_billing_importable(self):
        from fasthub_core.billing.ksef_xml import KSeFXMLBuilder
        from fasthub_core.billing.ksef_hook import KSeFInvoiceHook
        from fasthub_core.billing.invoice_router import get_invoice_hook
        from fasthub_core.billing import KSeFXMLBuilder as B1, KSeFInvoiceHook as B2, get_invoice_hook as B3
        assert B1 is KSeFXMLBuilder
        assert B2 is KSeFInvoiceHook
        assert B3 is get_invoice_hook
