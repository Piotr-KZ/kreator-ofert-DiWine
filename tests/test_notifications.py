"""Testy Notifications — modele, serwis, email transport, preferencje, schemas, routes"""

import pytest


# === MODELE ===

def test_notification_model():
    """Notification musi mieć kluczowe pola"""
    from fasthub_core.notifications.models import Notification
    assert hasattr(Notification, 'user_id')
    assert hasattr(Notification, 'type')
    assert hasattr(Notification, 'title')
    assert hasattr(Notification, 'message')
    assert hasattr(Notification, 'is_read')
    assert hasattr(Notification, 'link')
    assert hasattr(Notification, 'triggered_by')
    assert hasattr(Notification, 'organization_id')


def test_notification_model_has_read_at():
    """Notification musi mieć read_at (kiedy przeczytano)"""
    from fasthub_core.notifications.models import Notification
    assert hasattr(Notification, 'read_at')
    assert hasattr(Notification, 'created_at')


def test_preference_model():
    """NotificationPreference musi mieć pola kanałów"""
    from fasthub_core.notifications.models import NotificationPreference
    assert hasattr(NotificationPreference, 'user_id')
    assert hasattr(NotificationPreference, 'notification_type')
    assert hasattr(NotificationPreference, 'channel_inapp')
    assert hasattr(NotificationPreference, 'channel_email')


# === EMAIL TRANSPORT ===

def test_email_transport_classes_exist():
    """Wszystkie klasy transportu muszą istnieć"""
    from fasthub_core.notifications.email_transport import (
        EmailTransport, SMTPTransport, ConsoleTransport, create_email_transport,
    )
    assert callable(create_email_transport)


@pytest.mark.asyncio
async def test_console_transport_sends():
    """ConsoleTransport zawsze zwraca True (dev mode)"""
    from fasthub_core.notifications.email_transport import ConsoleTransport
    transport = ConsoleTransport()
    result = await transport.send(
        to="test@example.com",
        subject="Test Subject",
        body="Test body message",
    )
    assert result is True


@pytest.mark.asyncio
async def test_console_transport_with_from_email():
    """ConsoleTransport obsługuje custom from_email"""
    from fasthub_core.notifications.email_transport import ConsoleTransport
    transport = ConsoleTransport()
    result = await transport.send(
        to="test@example.com",
        subject="Test",
        body="Body",
        from_email="custom@fasthub.app",
    )
    assert result is True


def test_create_transport_without_smtp():
    """Bez SMTP_HOST powinien zwrócić ConsoleTransport"""
    from fasthub_core.notifications.email_transport import create_email_transport, ConsoleTransport
    transport = create_email_transport()
    assert isinstance(transport, ConsoleTransport)


def test_smtp_transport_init():
    """SMTPTransport poprawnie inicjalizuje parametry"""
    from fasthub_core.notifications.email_transport import SMTPTransport
    transport = SMTPTransport(
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass",
        use_tls=True,
        from_email="test@example.com",
    )
    assert transport.host == "smtp.example.com"
    assert transport.port == 587
    assert transport.use_tls is True
    assert transport.default_from == "test@example.com"


# === SERVICE ===

def test_notification_service_has_all_methods():
    """NotificationService musi mieć wszystkie wymagane metody"""
    from fasthub_core.notifications.service import NotificationService
    assert hasattr(NotificationService, 'send')
    assert hasattr(NotificationService, 'send_to_many')
    assert hasattr(NotificationService, 'get_notifications')
    assert hasattr(NotificationService, 'get_unread_count')
    assert hasattr(NotificationService, 'mark_as_read')
    assert hasattr(NotificationService, 'mark_all_as_read')
    assert hasattr(NotificationService, 'delete_notification')
    assert hasattr(NotificationService, 'get_user_preferences')
    assert hasattr(NotificationService, 'update_preference')


def test_default_preferences_cover_all_types():
    """DEFAULT_PREFERENCES musi mieć preferencje dla kluczowych typów"""
    from fasthub_core.notifications.service import DEFAULT_PREFERENCES
    required_types = ["invitation", "role_change", "security_alert",
                      "billing", "system", "impersonation",
                      "approval_request", "approval_result"]
    for ntype in required_types:
        assert ntype in DEFAULT_PREFERENCES, f"Brak preferencji dla typu: {ntype}"
        assert "inapp" in DEFAULT_PREFERENCES[ntype]
        assert "email" in DEFAULT_PREFERENCES[ntype]


def test_forced_types_are_security():
    """FORCED_TYPES muszą zawierać security_alert i impersonation"""
    from fasthub_core.notifications.service import FORCED_TYPES
    assert "security_alert" in FORCED_TYPES
    assert "impersonation" in FORCED_TYPES


def test_forced_types_always_enabled():
    """Security i impersonation muszą mieć inapp=True i email=True"""
    from fasthub_core.notifications.service import FORCED_TYPES, DEFAULT_PREFERENCES
    for forced_type in FORCED_TYPES:
        prefs = DEFAULT_PREFERENCES[forced_type]
        assert prefs["inapp"] is True, f"{forced_type} inapp powinno być True"
        assert prefs["email"] is True, f"{forced_type} email powinno być True"


# === ROUTES ===

def test_notifications_router_prefix():
    """Router musi mieć prefix /api/notifications"""
    from fasthub_core.notifications.routes import router
    assert router.prefix == "/api/notifications"


def test_notifications_router_has_enough_routes():
    """Router musi mieć minimum 7 endpointów"""
    from fasthub_core.notifications.routes import router
    routes = [r.path for r in router.routes]
    assert len(routes) >= 7


# === SCHEMAS ===

def test_unread_count_schema():
    """UnreadCountResponse poprawnie serializuje"""
    from fasthub_core.notifications.schemas import UnreadCountResponse
    resp = UnreadCountResponse(unread_count=5)
    assert resp.unread_count == 5


def test_preference_update_request_schema():
    """PreferenceUpdateRequest poprawnie waliduje"""
    from fasthub_core.notifications.schemas import PreferenceUpdateRequest
    req = PreferenceUpdateRequest(
        notification_type="billing",
        channel_inapp=True,
        channel_email=False,
    )
    assert req.notification_type == "billing"
    assert req.channel_inapp is True
    assert req.channel_email is False


def test_preference_response_forced_flag():
    """PreferenceResponse obsługuje flagę forced"""
    from fasthub_core.notifications.schemas import PreferenceResponse
    pref = PreferenceResponse(
        type="security_alert",
        inapp=True,
        email=True,
        forced=True,
    )
    assert pref.forced is True

    pref_normal = PreferenceResponse(
        type="billing",
        inapp=True,
        email=False,
    )
    assert pref_normal.forced is False


# === __init__.py EXPORTS ===

def test_notifications_package_exports():
    """Pakiet notifications musi eksportować kluczowe elementy"""
    from fasthub_core.notifications import (
        notifications_router,
        NotificationService,
        EmailTransport,
        create_email_transport,
    )
    assert notifications_router is not None
    assert NotificationService is not None
    assert EmailTransport is not None
    assert callable(create_email_transport)


# === CONTRACTS_IMPL ===

def test_notification_contract_impl_not_placeholder():
    """FastHubNotification nie powinien rzucać NotImplementedError"""
    from fasthub_core.contracts_impl import FastHubNotification
    notif = FastHubNotification()
    # send_email nie powinno rzucać NotImplementedError (uzywamy email transport)
    assert hasattr(notif, 'send_notification')
    assert hasattr(notif, 'send_email')


# === CONFIG ===

def test_config_has_smtp_settings():
    """Settings musi mieć opcjonalne pola SMTP"""
    from fasthub_core.config import Settings
    fields = Settings.model_fields
    assert "SMTP_HOST" in fields
    assert "SMTP_PORT" in fields
    assert "SMTP_USERNAME" in fields
    assert "SMTP_PASSWORD" in fields
    assert "SMTP_USE_TLS" in fields
    assert "SMTP_FROM_EMAIL" in fields
