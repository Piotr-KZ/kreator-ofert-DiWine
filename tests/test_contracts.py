"""
Testy kontraktu — weryfikacja że fasthub_core dostarcza to co obiecuje.
Uruchom: python -m pytest tests/test_contracts.py -v
"""


# ============================================================================
# Testy kontraktów (interfejsów) — czy klasy istnieją i mają wymagane metody
# ============================================================================

def test_auth_contract_imports():
    """AuthContract musi być importowalny i mieć wymagane metody"""
    from fasthub_core.contracts import AuthContract
    required_methods = [
        'hash_password', 'verify_password',
        'create_access_token', 'create_refresh_token',
        'decode_token', 'blacklist_token', 'is_token_blacklisted'
    ]
    for method in required_methods:
        assert hasattr(AuthContract, method), f"Brak metody: {method}"


def test_user_contract_imports():
    """UserContract musi mieć wymagane metody"""
    from fasthub_core.contracts import UserContract
    required_methods = [
        'get_current_user', 'get_user',
        'list_organization_users', 'get_user_role'
    ]
    for method in required_methods:
        assert hasattr(UserContract, method), f"Brak metody: {method}"


def test_permission_contract_imports():
    """PermissionContract musi mieć wymagane metody"""
    from fasthub_core.contracts import PermissionContract
    assert hasattr(PermissionContract, 'check_permission')
    assert hasattr(PermissionContract, 'get_user_permissions')


def test_billing_contract_imports():
    """BillingContract musi mieć wymagane metody"""
    from fasthub_core.contracts import BillingContract
    required = ['get_subscription', 'check_limit', 'record_usage']
    for method in required:
        assert hasattr(BillingContract, method), f"Brak: {method}"


def test_audit_contract_imports():
    """AuditContract musi mieć wymagane metody"""
    from fasthub_core.contracts import AuditContract
    assert hasattr(AuditContract, 'log_action')
    assert hasattr(AuditContract, 'get_audit_logs')


def test_notification_contract_imports():
    """NotificationContract musi mieć wymagane metody"""
    from fasthub_core.contracts import NotificationContract
    assert hasattr(NotificationContract, 'send_notification')
    assert hasattr(NotificationContract, 'send_email')


def test_database_contract_imports():
    """DatabaseContract musi mieć wymagane metody"""
    from fasthub_core.contracts import DatabaseContract
    assert hasattr(DatabaseContract, 'get_db_session')
    assert hasattr(DatabaseContract, 'get_engine')


def test_version_exists():
    """Wersja pakietu musi istnieć"""
    from fasthub_core import __version__
    assert __version__ == "2.0.0-alpha"


# ============================================================================
# Testy implementacji — czy faktyczny kod działa
# ============================================================================

def test_actual_auth_functions():
    """Sprawdź że faktyczne funkcje auth istnieją i działają"""
    from fasthub_core.auth.service import get_password_hash, verify_password
    # Test hash
    hashed = get_password_hash("TestPassword123")
    assert hashed is not None
    assert hashed != "TestPassword123"
    # Test verify
    assert verify_password("TestPassword123", hashed) == True
    assert verify_password("WrongPassword", hashed) == False


def test_actual_models_exist():
    """Sprawdź że modele User, Organization, Member istnieją"""
    from fasthub_core.users.models import User, Organization, Member
    assert hasattr(User, 'email')
    assert hasattr(User, 'id')
    assert hasattr(Organization, 'name')
    assert hasattr(Organization, 'slug')
    assert hasattr(Member, 'user_id')
    assert hasattr(Member, 'organization_id')
    assert hasattr(Member, 'role')


def test_billing_models_exist():
    """Sprawdź że modele Subscription, Invoice istnieją"""
    from fasthub_core.billing.models import Subscription, Invoice
    assert hasattr(Subscription, 'stripe_subscription_id')
    assert hasattr(Subscription, 'status')
    assert hasattr(Invoice, 'invoice_number')
    assert hasattr(Invoice, 'amount')


def test_audit_model_exists():
    """Sprawdź że model AuditLog istnieje"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'action')
    assert hasattr(AuditLog, 'resource_type')
    assert hasattr(AuditLog, 'user_id')


def test_fasthub_auth_implementation():
    """Sprawdź że implementacja FastHubAuth działa"""
    from fasthub_core.contracts_impl import FastHubAuth

    auth = FastHubAuth()
    hashed = auth.hash_password("SecurePass1")
    assert auth.verify_password("SecurePass1", hashed) == True
    assert auth.verify_password("BadPassword", hashed) == False


def test_fasthub_permission_uses_rbac():
    """FastHubPermission musi używać RBACService (Advanced RBAC)"""
    from fasthub_core.contracts_impl import FastHubPermission
    from fasthub_core.rbac.defaults import CORE_PERMISSIONS, SYSTEM_ROLES

    # PermissionContract teraz deleguje do RBACService
    assert FastHubPermission is not None
    # Domyślne role muszą istnieć
    assert "owner" in SYSTEM_ROLES
    assert "admin" in SYSTEM_ROLES
    assert "member" in SYSTEM_ROLES
    # Core permissions muszą zawierać kluczowe kategorie
    assert "team" in CORE_PERMISSIONS
    assert "billing" in CORE_PERMISSIONS


def test_notification_requires_db():
    """NotificationContract wymaga db session w data['db']"""
    import pytest
    from fasthub_core.contracts_impl import FastHubNotification

    notif = FastHubNotification()
    with pytest.raises(ValueError, match="db session is required"):
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            notif.send_notification("user-1", "info", "Test", "Test message")
        )


def test_billing_limit_not_implemented():
    """check_limit powinien rzucać NotImplementedError"""
    import pytest
    from fasthub_core.contracts_impl import FastHubBilling

    billing = FastHubBilling()
    with pytest.raises(NotImplementedError):
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            billing.check_limit("org-1", "processes", 10, None)
        )


def test_all_contracts_importable_from_init():
    """Wszystkie kontrakty muszą być dostępne z fasthub_core"""
    from fasthub_core import (
        AuthContract, UserContract, PermissionContract,
        BillingContract, AuditContract, NotificationContract,
        DatabaseContract
    )
    # Jeśli import się udał — test przechodzi
    assert AuthContract is not None
    assert UserContract is not None
    assert PermissionContract is not None
    assert BillingContract is not None
    assert AuditContract is not None
    assert NotificationContract is not None
    assert DatabaseContract is not None
