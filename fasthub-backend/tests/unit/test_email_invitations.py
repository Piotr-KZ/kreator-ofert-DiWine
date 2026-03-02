"""
Tests for Brief 19 — Email Templates, Invitations, SendGrid, Invoice Hook.
~30 tests.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


# ============================================================================
# TemplateEngine tests
# ============================================================================

class TestTemplateEngine:

    def test_render_welcome_html(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, txt = engine.render("welcome", {
            "user_name": "Jan",
            "org_name": "Firma",
            "dashboard_url": "https://app.test/dashboard",
        })
        assert "Jan" in html
        assert "Firma" in html
        assert "https://app.test/dashboard" in html
        assert "<html" in html  # HTML template extends base

    def test_render_welcome_txt(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        _, txt = engine.render("welcome", {
            "user_name": "Jan",
            "dashboard_url": "https://app.test/dashboard",
        })
        assert "Jan" in txt
        assert "https://app.test/dashboard" in txt

    def test_render_verify_email(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("verify_email", {
            "user_name": "Anna",
            "verify_url": "https://app.test/verify/abc",
        })
        assert "Anna" in html
        assert "verify/abc" in html

    def test_render_password_reset(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("password_reset", {
            "user_name": "Piotr",
            "reset_url": "https://app.test/reset/xyz",
        })
        assert "Piotr" in html
        assert "reset/xyz" in html

    def test_render_invitation(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("invitation", {
            "inviter_name": "Jan",
            "org_name": "Budimex",
            "role_name": "admin",
            "accept_url": "https://app.test/accept/token123",
        })
        assert "Jan" in html
        assert "Budimex" in html
        assert "admin" in html

    def test_render_payment_success(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("payment_success", {
            "user_name": "Jan",
            "plan_name": "Pro",
            "amount": "199.00",
            "currency": "PLN",
        })
        assert "Pro" in html
        assert "199.00" in html

    def test_render_payment_failed(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("payment_failed", {
            "user_name": "Jan",
            "plan_name": "Pro",
            "amount": "199.00",
            "retry_url": "https://app.test/billing",
        })
        assert "Problem" in html
        assert "billing" in html

    def test_render_account_deletion(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("account_deletion", {
            "user_name": "Jan",
            "execute_date": "16.03.2026",
            "cancel_url": "https://app.test/cancel/abc",
        })
        assert "16.03.2026" in html
        assert "cancel/abc" in html

    def test_brand_injection(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, _ = engine.render("welcome", {
            "user_name": "Test",
            "dashboard_url": "#",
        })
        # Default brand: FastHub
        assert "FastHub" in html

    def test_missing_template_returns_empty(self):
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine()
        html, txt = engine.render("nonexistent_template", {})
        assert html == ""
        assert txt == ""

    def test_app_override_directory(self):
        """Test that app_template_dir with invalid path falls back to defaults."""
        from fasthub_core.email.template_engine import TemplateEngine
        engine = TemplateEngine(app_template_dir="/nonexistent/path")
        html, _ = engine.render("welcome", {
            "user_name": "Test",
            "dashboard_url": "#",
        })
        assert "Test" in html  # Uses default template


# ============================================================================
# send_templated_email tests
# ============================================================================

class TestSendTemplatedEmail:

    @pytest.mark.asyncio
    async def test_send_renders_and_sends(self):
        with patch("fasthub_core.notifications.email_transport.create_email_transport") as mock_factory:
            mock_transport = AsyncMock()
            mock_transport.send.return_value = True
            mock_factory.return_value = mock_transport

            from fasthub_core.email.send import send_templated_email
            result = await send_templated_email(
                "welcome",
                to="jan@test.pl",
                subject="Witaj!",
                context={"user_name": "Jan", "dashboard_url": "#"},
            )

            assert result is True
            mock_transport.send.assert_called_once()
            call_kwargs = mock_transport.send.call_args
            assert "jan@test.pl" in str(call_kwargs)

    @pytest.mark.asyncio
    async def test_send_missing_template_returns_false(self):
        from fasthub_core.email.send import send_templated_email
        result = await send_templated_email(
            "nonexistent",
            to="jan@test.pl",
            context={},
        )
        assert result is False


# ============================================================================
# SendGrid transport tests
# ============================================================================

class TestSendGridTransport:

    def test_init(self):
        from fasthub_core.notifications.sendgrid_transport import SendGridTransport
        t = SendGridTransport(api_key="SG.test", from_email="test@test.pl")
        assert t.api_key == "SG.test"
        assert t.from_email == "test@test.pl"

    @pytest.mark.asyncio
    async def test_send_success(self):
        from fasthub_core.notifications.sendgrid_transport import SendGridTransport

        with patch("httpx.AsyncClient") as MockClient:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_resp
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client_instance

            t = SendGridTransport(api_key="SG.test")
            result = await t.send("jan@test.pl", "Subject", "<h1>Hi</h1>")
            assert result is True

    @pytest.mark.asyncio
    async def test_send_failure(self):
        from fasthub_core.notifications.sendgrid_transport import SendGridTransport

        with patch("httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.side_effect = Exception("API error")
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client_instance

            t = SendGridTransport(api_key="SG.test")
            result = await t.send("jan@test.pl", "Subject", "Body")
            assert result is False


# ============================================================================
# Email transport factory tests
# ============================================================================

class TestEmailTransportFactory:

    def test_factory_console_default(self):
        from fasthub_core.notifications.email_transport import ConsoleTransport
        with patch("fasthub_core.config.get_settings") as mock:
            s = MagicMock()
            s.EMAIL_BACKEND = None
            s.SMTP_HOST = None
            s.SENDGRID_API_KEY = None
            mock.return_value = s

            from fasthub_core.notifications.email_transport import create_email_transport
            transport = create_email_transport()
            assert isinstance(transport, ConsoleTransport)

    def test_factory_sendgrid_explicit(self):
        with patch("fasthub_core.config.get_settings") as mock:
            s = MagicMock()
            s.EMAIL_BACKEND = "sendgrid"
            s.SENDGRID_API_KEY = "SG.test"
            s.SENDGRID_FROM_EMAIL = "noreply@test.pl"
            mock.return_value = s

            from fasthub_core.notifications.email_transport import create_email_transport
            transport = create_email_transport()
            from fasthub_core.notifications.sendgrid_transport import SendGridTransport
            assert isinstance(transport, SendGridTransport)

    def test_factory_smtp_explicit(self):
        from fasthub_core.notifications.email_transport import SMTPTransport
        with patch("fasthub_core.config.get_settings") as mock:
            s = MagicMock()
            s.EMAIL_BACKEND = "smtp"
            s.SMTP_HOST = "smtp.test.com"
            s.SMTP_PORT = 587
            s.SMTP_USERNAME = "user"
            s.SMTP_PASSWORD = "pass"
            s.SMTP_USE_TLS = True
            s.SMTP_FROM_EMAIL = "noreply@test.pl"
            mock.return_value = s

            from fasthub_core.notifications.email_transport import create_email_transport
            transport = create_email_transport()
            assert isinstance(transport, SMTPTransport)


# ============================================================================
# Invitation model tests
# ============================================================================

class TestInvitationModel:

    def test_model_creation(self):
        from fasthub_core.invitations.models import Invitation, InvitationStatus
        inv = Invitation(
            email="jan@test.pl",
            token="abc123",
            organization_id=uuid4(),
            role="admin",
            invited_by=uuid4(),
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        assert inv.email == "jan@test.pl"
        assert inv.status is None or inv.status == InvitationStatus.pending

    def test_model_tablename(self):
        from fasthub_core.invitations.models import Invitation
        assert Invitation.__tablename__ == "invitations"

    def test_status_enum_values(self):
        from fasthub_core.invitations.models import InvitationStatus
        assert InvitationStatus.pending.value == "pending"
        assert InvitationStatus.accepted.value == "accepted"
        assert InvitationStatus.expired.value == "expired"
        assert InvitationStatus.canceled.value == "canceled"


# ============================================================================
# InvitationService tests
# ============================================================================

class TestInvitationService:

    @pytest.mark.asyncio
    async def test_create_invitation(self):
        from fasthub_core.invitations.service import InvitationService
        from fasthub_core.invitations.models import InvitationStatus

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        mock_settings = MagicMock(
            INVITATION_EXPIRE_DAYS=7,
            INVITATION_MAX_PENDING=50,
            FRONTEND_URL="https://app.test",
            EMAIL_TEMPLATE_DIR=None,
        )

        with patch("fasthub_core.config.get_settings", return_value=mock_settings), \
             patch("fasthub_core.notifications.email_transport.create_email_transport") as mock_factory:
            mock_transport = AsyncMock()
            mock_transport.send.return_value = True
            mock_factory.return_value = mock_transport

            svc = InvitationService(mock_db)
            inv = await svc.create_invitation(
                email="new@test.pl",
                organization_id=uuid4(),
                role="viewer",
                invited_by=uuid4(),
            )

            assert inv.email == "new@test.pl"
            assert inv.role == "viewer"
            assert inv.token  # token generated
            mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_invitation(self):
        from fasthub_core.invitations.service import InvitationService
        from fasthub_core.invitations.models import Invitation, InvitationStatus

        pending = Invitation(
            id=uuid4(),
            email="test@test.pl",
            token="abc",
            organization_id=uuid4(),
            role="viewer",
            invited_by=uuid4(),
            status=InvitationStatus.pending,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = pending
        mock_db.execute.return_value = mock_result

        svc = InvitationService(mock_db)
        result = await svc.cancel_invitation(pending.id)

        assert result is True
        assert pending.status == InvitationStatus.canceled

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_returns_false(self):
        from fasthub_core.invitations.service import InvitationService

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        svc = InvitationService(mock_db)
        result = await svc.cancel_invitation(uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        from fasthub_core.invitations.service import InvitationService

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_db.execute.return_value = mock_result

        svc = InvitationService(mock_db)
        count = await svc.cleanup_expired()
        assert count == 3


# ============================================================================
# AutoInvoiceHook tests
# ============================================================================

class TestAutoInvoiceHook:

    @pytest.mark.asyncio
    async def test_skip_when_not_configured(self):
        from fasthub_core.billing.invoice_hook import AutoInvoiceHook

        mock_db = AsyncMock()

        with patch("fasthub_core.config.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                FAKTUROWNIA_API_TOKEN=None,
                FAKTUROWNIA_ACCOUNT=None,
            )

            hook = AutoInvoiceHook(mock_db)
            result = await hook.handle({"tenant_id": str(uuid4())})
            assert result is None

    @pytest.mark.asyncio
    async def test_skip_when_no_tenant(self):
        from fasthub_core.billing.invoice_hook import AutoInvoiceHook

        mock_db = AsyncMock()

        with patch("fasthub_core.config.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                FAKTUROWNIA_API_TOKEN="token",
                FAKTUROWNIA_ACCOUNT="account",
            )

            hook = AutoInvoiceHook(mock_db)
            result = await hook.handle({})  # no tenant_id
            assert result is None


# ============================================================================
# Config tests
# ============================================================================

class TestBrief19Config:

    def test_email_config_defaults(self):
        with patch.dict("os.environ", {"SECRET_KEY": "test"}):
            from fasthub_core.config import Settings
            s = Settings(SECRET_KEY="test")
            assert s.EMAIL_BRAND_COLOR == "#4F46E5"
            assert s.EMAIL_COMPANY_NAME == "FastHub"
            assert s.INVITATION_EXPIRE_DAYS == 7
            assert s.INVITATION_MAX_PENDING == 50
            assert s.EMAIL_BACKEND is None
            assert s.EMAIL_TEMPLATE_DIR is None
