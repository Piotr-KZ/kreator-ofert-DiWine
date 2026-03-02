"""
Migration helper for fasthub_core.

Importuje WSZYSTKIE modele, żeby Alembic widział wszystkie tabele.

Użycie w Alembic env.py:
    from fasthub_core.db.migrations import get_metadata
    target_metadata = get_metadata()

Użycie do listowania modeli:
    from fasthub_core.db.migrations import get_all_models
    models = get_all_models()
"""

from fasthub_core.db.session import Base


def get_all_models():
    """
    Importuje i zwraca słownik wszystkich modeli fasthub_core.

    Kluczowe: sam import rejestruje modele w Base.metadata,
    więc Alembic autogenerate je wykryje.
    """
    from fasthub_core.users.models import User, Organization, Member, MemberRole
    from fasthub_core.auth.models import APIToken
    from fasthub_core.billing.models import (
        Subscription, SubscriptionStatus, Invoice, InvoiceStatus,
        BillingPlan, BillingAddon, TenantAddon, UsageRecord, BillingEvent,
    )
    from fasthub_core.audit.models import AuditLog
    from fasthub_core.notifications.models import Notification, NotificationPreference
    from fasthub_core.rbac.models import Permission, Role, RolePermission, UserRole

    return {
        "User": User,
        "Organization": Organization,
        "Member": Member,
        "MemberRole": MemberRole,
        "APIToken": APIToken,
        "Subscription": Subscription,
        "SubscriptionStatus": SubscriptionStatus,
        "Invoice": Invoice,
        "InvoiceStatus": InvoiceStatus,
        "BillingPlan": BillingPlan,
        "BillingAddon": BillingAddon,
        "TenantAddon": TenantAddon,
        "UsageRecord": UsageRecord,
        "BillingEvent": BillingEvent,
        "AuditLog": AuditLog,
        "Notification": Notification,
        "NotificationPreference": NotificationPreference,
        "Permission": Permission,
        "Role": Role,
        "RolePermission": RolePermission,
        "UserRole": UserRole,
    }


def get_metadata():
    """
    Zwraca Base.metadata z WSZYSTKIMI modelami zarejestrowanymi.

    Użycie w Alembic env.py:
        from fasthub_core.db.migrations import get_metadata
        target_metadata = get_metadata()
    """
    get_all_models()
    return Base.metadata


def get_sync_database_url(url: str) -> str:
    """
    Konwertuje async URL na sync (dla Alembic migracji).
    postgresql+asyncpg:// → postgresql://
    """
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    return url
