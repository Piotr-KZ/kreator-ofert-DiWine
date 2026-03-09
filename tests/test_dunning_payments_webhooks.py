"""Testy Dunning + Payments + Webhook Config (Brief 27)."""

import os
import sys
import json
import hmac
import hashlib
import secrets
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

# Add fasthub-backend to path
_backend_dir = os.path.join(os.path.dirname(__file__), "..", "fasthub-backend")
if os.path.isdir(_backend_dir) and _backend_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_backend_dir))

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-brief27")


# =========================================================================
# PART A: DUNNING MODELS + SERVICE
# =========================================================================

# === IMPORTS ===

def test_dunning_models_import():
    """Dunning models musza byc importowalne."""
    from fasthub_core.billing.dunning_models import DunningPath, DunningStep, DunningEvent, DunningActionType
    assert DunningPath is not None
    assert DunningStep is not None
    assert DunningEvent is not None
    assert DunningActionType is not None


def test_dunning_service_import():
    """DunningService musi byc importowalny."""
    from fasthub_core.billing.dunning_service import DunningService, DEFAULT_DUNNING_STEPS
    assert DunningService is not None
    assert len(DEFAULT_DUNNING_STEPS) == 16


def test_dunning_endpoints_import():
    """Endpointy dunning musza byc importowalne."""
    from app.api.v1.endpoints.dunning import router
    assert router is not None


# === DUNNING MODEL FIELDS ===

def test_dunning_path_model_has_required_fields():
    """DunningPath model ma wymagane pola."""
    from fasthub_core.billing.dunning_models import DunningPath
    columns = {c.name for c in DunningPath.__table__.columns}
    assert "name" in columns
    assert "description" in columns
    assert "is_default" in columns
    assert "is_active" in columns
    assert "applicable_plans" in columns


def test_dunning_step_model_has_required_fields():
    """DunningStep model ma wymagane pola."""
    from fasthub_core.billing.dunning_models import DunningStep
    columns = {c.name for c in DunningStep.__table__.columns}
    assert "path_id" in columns
    assert "day_offset" in columns
    assert "action_type" in columns
    assert "email_template_id" in columns
    assert "email_subject" in columns
    assert "is_active" in columns
    assert "description" in columns


def test_dunning_event_model_has_required_fields():
    """DunningEvent model ma wymagane pola."""
    from fasthub_core.billing.dunning_models import DunningEvent
    columns = {c.name for c in DunningEvent.__table__.columns}
    assert "subscription_id" in columns
    assert "organization_id" in columns
    assert "step_id" in columns
    assert "day_offset" in columns
    assert "action_type" in columns
    assert "status" in columns
    assert "details" in columns
    assert "executed_at" in columns


# === ACTION TYPES ===

def test_dunning_action_types():
    """Wszystkie wymagane action types istnieja."""
    from fasthub_core.billing.dunning_models import DunningActionType
    expected = [
        "email_reminder", "email_warning", "email_final",
        "retry_payment", "restrict_access", "block_access",
        "downgrade_free", "cancel_subscription", "disable_sites",
        "notify_admin", "webhook",
    ]
    for action in expected:
        assert hasattr(DunningActionType, action.upper()), f"Missing action: {action}"


# === DEFAULT DUNNING STEPS ===

def test_default_dunning_steps_day_offsets():
    """Domyslne kroki maja poprawne day_offsets."""
    from fasthub_core.billing.dunning_service import DEFAULT_DUNNING_STEPS
    offsets = sorted(set(s["day_offset"] for s in DEFAULT_DUNNING_STEPS))
    assert offsets == [0, 1, 3, 7, 10, 14, 21, 30, 45]


def test_default_dunning_steps_day_0():
    """Dzien 0: retry_payment + email_reminder."""
    from fasthub_core.billing.dunning_service import DEFAULT_DUNNING_STEPS
    day0 = [s for s in DEFAULT_DUNNING_STEPS if s["day_offset"] == 0]
    actions = [s["action_type"] for s in day0]
    assert "retry_payment" in actions
    assert "email_reminder" in actions


def test_default_dunning_steps_day_3():
    """Dzien 3: email_warning + notify_admin."""
    from fasthub_core.billing.dunning_service import DEFAULT_DUNNING_STEPS
    day3 = [s for s in DEFAULT_DUNNING_STEPS if s["day_offset"] == 3]
    actions = [s["action_type"] for s in day3]
    assert "email_warning" in actions
    assert "notify_admin" in actions


def test_default_dunning_steps_day_10():
    """Dzien 10: restrict_access."""
    from fasthub_core.billing.dunning_service import DEFAULT_DUNNING_STEPS
    day10 = [s for s in DEFAULT_DUNNING_STEPS if s["day_offset"] == 10]
    actions = [s["action_type"] for s in day10]
    assert "restrict_access" in actions


def test_default_dunning_steps_day_14():
    """Dzien 14: disable_sites."""
    from fasthub_core.billing.dunning_service import DEFAULT_DUNNING_STEPS
    day14 = [s for s in DEFAULT_DUNNING_STEPS if s["day_offset"] == 14]
    actions = [s["action_type"] for s in day14]
    assert "disable_sites" in actions


def test_default_dunning_steps_day_45():
    """Dzien 45: downgrade + cancel + email_final."""
    from fasthub_core.billing.dunning_service import DEFAULT_DUNNING_STEPS
    day45 = [s for s in DEFAULT_DUNNING_STEPS if s["day_offset"] == 45]
    actions = [s["action_type"] for s in day45]
    assert "downgrade_free" in actions
    assert "cancel_subscription" in actions
    assert "email_final" in actions


# =========================================================================
# PART B: PAYMENT MODEL
# =========================================================================

def test_payment_model_import():
    """Payment model musi byc importowalny."""
    from fasthub_core.billing.payment_models import Payment
    assert Payment is not None


def test_payment_model_has_required_fields():
    """Payment model ma wymagane pola."""
    from fasthub_core.billing.payment_models import Payment
    columns = {c.name for c in Payment.__table__.columns}
    assert "organization_id" in columns
    assert "subscription_id" in columns
    assert "amount" in columns
    assert "currency" in columns
    assert "gateway_id" in columns
    assert "gateway_payment_id" in columns
    assert "payment_method" in columns
    assert "payment_method_details" in columns
    assert "status" in columns
    assert "description" in columns
    assert "completed_at" in columns
    assert "failed_at" in columns
    assert "refunded_at" in columns
    assert "invoice_id" in columns


def test_payments_endpoint_import():
    """Endpointy payments musza byc importowalne."""
    from app.api.v1.endpoints.payments import router
    assert router is not None


# =========================================================================
# PART C: WEBHOOK CONFIG
# =========================================================================

def test_webhook_endpoint_model_import():
    """WebhookEndpoint model musi byc importowalny."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint, WebhookDelivery
    assert WebhookEndpoint is not None
    assert WebhookDelivery is not None


def test_webhook_endpoint_model_has_required_fields():
    """WebhookEndpoint model ma wymagane pola."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint
    columns = {c.name for c in WebhookEndpoint.__table__.columns}
    assert "organization_id" in columns
    assert "url" in columns
    assert "secret" in columns
    assert "events" in columns
    assert "is_active" in columns
    assert "last_triggered_at" in columns
    assert "last_status_code" in columns
    assert "consecutive_failures" in columns
    assert "description" in columns


def test_webhook_delivery_model_has_required_fields():
    """WebhookDelivery model ma wymagane pola."""
    from fasthub_core.integrations.webhook_config import WebhookDelivery
    columns = {c.name for c in WebhookDelivery.__table__.columns}
    assert "endpoint_id" in columns
    assert "event_type" in columns
    assert "payload" in columns
    assert "status_code" in columns
    assert "response_body" in columns
    assert "response_time_ms" in columns
    assert "success" in columns
    assert "error" in columns
    assert "attempt" in columns


def test_webhook_event_types():
    """Lista dostepnych event types."""
    from fasthub_core.integrations.webhook_config import WEBHOOK_EVENT_TYPES
    assert "form_submission" in WEBHOOK_EVENT_TYPES
    assert "payment_completed" in WEBHOOK_EVENT_TYPES
    assert "payment_failed" in WEBHOOK_EVENT_TYPES
    assert "subscription_canceled" in WEBHOOK_EVENT_TYPES
    assert "member_invited" in WEBHOOK_EVENT_TYPES
    assert "site_published" in WEBHOOK_EVENT_TYPES
    assert "invoice_issued" in WEBHOOK_EVENT_TYPES
    assert len(WEBHOOK_EVENT_TYPES) == 13


def test_webhook_config_endpoint_import():
    """Endpointy webhook config musza byc importowalne."""
    from app.api.v1.endpoints.webhook_config import router
    assert router is not None


# =========================================================================
# WEBHOOK DISPATCHER
# =========================================================================

def test_webhook_dispatcher_import():
    """WebhookDispatcher musi byc importowalny."""
    from fasthub_core.integrations.webhook_dispatcher import WebhookDispatcher, dispatch_webhook
    assert WebhookDispatcher is not None
    assert callable(dispatch_webhook)


def test_hmac_signature():
    """Poprawny HMAC-SHA256 w sygnaturze."""
    from fasthub_core.integrations.webhook_dispatcher import WebhookDispatcher

    dispatcher = WebhookDispatcher()
    payload = '{"event": "test", "data": {"foo": "bar"}}'
    secret = "my-secret-key-123"

    signature = dispatcher._sign_payload(payload, secret)

    # Verify manually
    expected = hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    assert signature == expected


def test_hmac_signature_different_secrets():
    """Rozne sekrety daja rozne sygnatury."""
    from fasthub_core.integrations.webhook_dispatcher import WebhookDispatcher

    dispatcher = WebhookDispatcher()
    payload = '{"event": "test"}'

    sig1 = dispatcher._sign_payload(payload, "secret-1")
    sig2 = dispatcher._sign_payload(payload, "secret-2")
    assert sig1 != sig2


def test_hmac_signature_deterministic():
    """Ten sam payload + secret daje te sama sygnature."""
    from fasthub_core.integrations.webhook_dispatcher import WebhookDispatcher

    dispatcher = WebhookDispatcher()
    payload = '{"event": "test"}'
    secret = "my-secret"

    sig1 = dispatcher._sign_payload(payload, secret)
    sig2 = dispatcher._sign_payload(payload, secret)
    assert sig1 == sig2


# =========================================================================
# ALEMBIC MIGRATION
# =========================================================================

def test_migration_file_exists():
    """Plik migracji Brief 27 istnieje."""
    migration_dir = os.path.join(
        os.path.dirname(__file__), "..", "fasthub-backend", "alembic", "versions"
    )
    files = os.listdir(migration_dir)
    brief27_files = [f for f in files if "brief27" in f]
    assert len(brief27_files) == 1


# =========================================================================
# RECURRING MANAGER INTEGRATION
# =========================================================================

def test_recurring_manager_has_dunning_integration():
    """RecurringManager deleguje do DunningService."""
    import inspect
    from fasthub_core.billing.recurring_manager import RecurringManager
    source = inspect.getsource(RecurringManager._handle_subscription_renewal)
    assert "DunningService" in source
    assert "process_overdue_subscription" in source


# =========================================================================
# API ROUTER WIRING
# =========================================================================

def test_api_router_has_dunning():
    """api.py importuje dunning router."""
    api_path = os.path.join(
        os.path.dirname(__file__), "..", "fasthub-backend", "app", "api", "v1", "api.py"
    )
    with open(api_path) as f:
        content = f.read()
    assert "dunning" in content
    assert "payments" in content
    assert "webhook_config" in content
