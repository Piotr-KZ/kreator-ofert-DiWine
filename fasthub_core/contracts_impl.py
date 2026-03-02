"""
Implementacja kontraktów — mapowanie interfejsów na realne funkcje.

Każda klasa tutaj łączy abstrakcyjny kontrakt z faktycznym kodem
w fasthub_core/. Aplikacje importują te implementacje.

Status implementacji:
- FastHubAuth          — w pełni zaimplementowany
- FastHubUser          — w pełni zaimplementowany
- FastHubPermission    — Advanced RBAC (role + granularne permissions)
- FastHubBilling       — częściowo (get_subscription gotowe, limity w v2.0)
- FastHubAudit         — w pełni zaimplementowany
- FastHubNotification  — w pełni zaimplementowany (in-app + email)
- FastHubDatabase      — w pełni zaimplementowany
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.contracts import (
    AuthContract,
    UserContract,
    PermissionContract,
    BillingContract,
    AuditContract,
    NotificationContract,
    EventBusContract,
    DatabaseContract,
)

# Importy faktycznych implementacji
from fasthub_core.auth.service import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)
from fasthub_core.auth.blacklist import blacklist_token as _blacklist_token, is_token_blacklisted as _is_token_blacklisted
from fasthub_core.db.session import get_db, get_engine
from fasthub_core.users.models import User, Organization, Member, MemberRole
from fasthub_core.audit.models import AuditLog
from fasthub_core.billing.models import Subscription


# ============================================================================
# Auth — w pełni zaimplementowany
# ============================================================================

class FastHubAuth(AuthContract):
    """Implementacja kontraktu auth oparta na fasthub_core.auth"""

    def hash_password(self, password: str) -> str:
        return get_password_hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    def create_access_token(self, user_id: str, organization_id: Optional[str] = None, extra_data: Optional[Dict] = None) -> str:
        data = {"sub": user_id}
        if organization_id:
            data["org"] = organization_id
        if extra_data:
            data.update(extra_data)
        return create_access_token(data)

    def create_refresh_token(self, user_id: str) -> str:
        return create_refresh_token({"sub": user_id})

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        # Najpierw próbujemy access token, potem refresh
        result = decode_access_token(token)
        if result is None:
            result = decode_refresh_token(token)
        return result

    async def blacklist_token(self, token: str, expires_at: datetime) -> bool:
        now = datetime.utcnow()
        expires_in = max(int((expires_at - now).total_seconds()), 0)
        if expires_in <= 0:
            return False
        await _blacklist_token(token, expires_in)
        return True

    async def is_token_blacklisted(self, token: str) -> bool:
        return await _is_token_blacklisted(token)


# ============================================================================
# User — w pełni zaimplementowany
# ============================================================================

class FastHubUser(UserContract):
    """Implementacja kontraktu user oparta na fasthub_core.users"""

    async def get_current_user(self, token: str, db: AsyncSession) -> Any:
        payload = decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        return result.scalar_one_or_none()

    async def get_user(self, user_id: str, db: AsyncSession) -> Optional[Any]:
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        return result.scalar_one_or_none()

    async def list_organization_users(self, organization_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(Member, User)
            .join(User, Member.user_id == User.id)
            .where(Member.organization_id == UUID(organization_id))
        )
        rows = result.all()

        users = []
        for member, user in rows:
            users.append({
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": member.role.value if member.role else None,
                "is_active": user.is_active,
            })
        return users

    async def get_user_role(self, user_id: str, organization_id: str, db: AsyncSession) -> Optional[str]:
        result = await db.execute(
            select(Member).where(
                Member.user_id == UUID(user_id),
                Member.organization_id == UUID(organization_id),
            )
        )
        member = result.scalar_one_or_none()
        if member and member.role:
            return member.role.value
        return None


# ============================================================================
# Permission — Advanced RBAC (v2.0)
# Używa RBACService z fasthub_core.rbac
# ============================================================================

class FastHubPermission(PermissionContract):
    """
    Implementacja uprawnień oparta na Advanced RBAC.
    Sprawdza uprawnienia przez RBACService (role -> permissions z bazy danych).
    """

    async def check_permission(self, user_id: str, organization_id: str, permission: str, db: AsyncSession) -> bool:
        from fasthub_core.rbac.service import RBACService
        rbac = RBACService(db)
        return await rbac.check_permission(
            user_id=UUID(user_id),
            organization_id=UUID(organization_id),
            permission=permission,
        )

    async def get_user_permissions(self, user_id: str, organization_id: str, db: AsyncSession) -> Set[str]:
        from fasthub_core.rbac.service import RBACService
        rbac = RBACService(db)
        return await rbac.get_user_permissions(
            user_id=UUID(user_id),
            organization_id=UUID(organization_id),
        )

    async def assign_role(self, user_id: str, role_id: str, organization_id: str, db: AsyncSession) -> None:
        from fasthub_core.rbac.service import RBACService
        rbac = RBACService(db)
        await rbac.assign_role(
            user_id=UUID(user_id),
            role_id=UUID(role_id),
            organization_id=UUID(organization_id),
        )

    async def create_custom_role(self, organization_id: str, name: str, permissions: List[str], db: AsyncSession) -> Any:
        from fasthub_core.rbac.service import RBACService
        rbac = RBACService(db)
        role = await rbac.create_custom_role(
            organization_id=UUID(organization_id),
            name=name,
            description="",
            permission_names=permissions,
        )
        return {"id": str(role.id), "name": role.name}

    async def register_app_permissions(self, permissions: Dict[str, List[tuple]], db: AsyncSession) -> None:
        from fasthub_core.rbac.service import RBACService
        rbac = RBACService(db)
        await rbac.register_app_permissions(permissions)


# ============================================================================
# Billing — częściowo zaimplementowany
# get_subscription: gotowe
# check_limit, record_usage: planowane v2.0
# ============================================================================

class FastHubBilling(BillingContract):
    """
    Implementacja kontraktu billing.
    Subskrypcje przez Stripe — dane z modelu Subscription.
    System limitów i zużycia planowany w v2.0.
    """

    async def get_subscription(self, organization_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        result = await db.execute(
            select(Subscription).where(
                Subscription.organization_id == UUID(organization_id)
            ).order_by(Subscription.created_at.desc()).limit(1)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            return None

        return {
            "stripe_subscription_id": sub.stripe_subscription_id,
            "stripe_price_id": sub.stripe_price_id,
            "status": sub.status.value if sub.status else None,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }

    async def check_limit(self, organization_id: str, resource: str, current_usage: int, db: AsyncSession) -> bool:
        raise NotImplementedError("Planowane w FastHub v2.0 — system limitów per plan")

    async def record_usage(self, organization_id: str, resource: str, amount: int, db: AsyncSession) -> None:
        raise NotImplementedError("Planowane w FastHub v2.0 — tracking zużycia zasobów")


# ============================================================================
# Audit — w pełni zaimplementowany (rozbudowany: before/after, IP, retention)
# ============================================================================

class FastHubAudit(AuditContract):
    """Implementacja kontraktu audit oparta na rozbudowanym AuditService"""

    async def log_action(
        self,
        user_id: str,
        organization_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None,
    ) -> None:
        if db is None:
            raise ValueError("db session is required")

        from fasthub_core.audit.service import AuditService
        audit = AuditService(db)
        await audit.log_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            organization_id=organization_id,
            changes_before=before,
            changes_after=after,
            extra_data=details,
        )

    async def get_audit_logs(
        self,
        organization_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = None,
    ) -> List[Dict[str, Any]]:
        if db is None:
            raise ValueError("db session is required")

        from fasthub_core.audit.service import AuditService
        audit = AuditService(db)
        result = await audit.get_logs(
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            page=1,
            per_page=limit,
        )

        return [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "changes_before": log.changes_before,
                "changes_after": log.changes_after,
                "summary": log.summary,
                "extra_data": log.extra_data,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in result.get("logs", [])
        ]


# ============================================================================
# Notification — w pełni zaimplementowany (in-app + email transport)
# ============================================================================

class FastHubNotification(NotificationContract):
    """
    Implementacja kontraktu notification oparta na NotificationService.
    In-app notifications + email (SMTP lub console mode).
    """

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        from fasthub_core.notifications.service import NotificationService
        # Wymaga db session z kontekstu — data może zawierać "db", "email", "link" itp.
        data = data or {}
        db = data.get("db")
        if db is None:
            raise ValueError("db session is required in data['db']")

        service = NotificationService(db)
        await service.send(
            user_id=UUID(user_id),
            type=notification_type,
            title=title,
            message=message,
            link=data.get("link"),
            email=data.get("email"),
            organization_id=UUID(data["organization_id"]) if data.get("organization_id") else None,
            triggered_by=UUID(data["triggered_by"]) if data.get("triggered_by") else None,
        )

    async def send_email(
        self,
        to_email: str,
        template: str,
        variables: Dict[str, Any],
    ) -> None:
        from fasthub_core.notifications.email_transport import create_email_transport
        transport = create_email_transport()
        body = variables.get("body", template)
        subject = variables.get("subject", f"[FastHub] {template}")
        await transport.send(to=to_email, subject=subject, body=body)


# ============================================================================
# EventBus — placeholder (planowany v2.1)
# ============================================================================

class FastHubEventBus(EventBusContract):
    """
    Implementacja Event Bus oparta na fasthub_core.events.bus.
    Singleton EventBus z wildcard matching + Redis pub/sub.
    """

    def __init__(self):
        from fasthub_core.events.bus import event_bus
        self._bus = event_bus

    async def emit(self, event_type: str, data: dict) -> None:
        await self._bus.emit(event_type, data)

    async def on(self, event_pattern: str, handler) -> None:
        self._bus.register(event_pattern, handler)

    async def off(self, event_pattern: str, handler) -> None:
        self._bus.unregister(event_pattern, handler)


# ============================================================================
# Database — w pełni zaimplementowany
# ============================================================================

class FastHubDatabase(DatabaseContract):
    """Implementacja kontraktu database oparta na fasthub_core.db"""

    async def get_db_session(self):
        return get_db()

    def get_engine(self):
        return get_engine()
