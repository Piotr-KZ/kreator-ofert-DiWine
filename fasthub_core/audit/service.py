"""
Rozbudowany AuditService — logowanie zmian z before/after, IP, filtrowanie, retention.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, desc, and_
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta

from fasthub_core.audit.models import AuditLog


# Pola wrażliwe — nigdy nie logujemy ich w snapshot
SENSITIVE_FIELDS = {
    "hashed_password", "password", "token", "secret",
    "magic_link_token", "token_hash",
}


class AuditService:
    """Serwis audytu — logowanie i wyszukiwanie zmian"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === LOGOWANIE ===

    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        organization_id: Optional[str] = None,
        changes_before: Optional[Dict[str, Any]] = None,
        changes_after: Optional[Dict[str, Any]] = None,
        summary: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        impersonated_by: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Zapisz akcję w audit trail.

        Przykłady użycia:

        # Prosty log (bez before/after):
        await audit.log_action(
            action="login",
            resource_type="user",
            user_id=str(user.id),
            ip_address=request.client.host,
        )

        # Log ze zmianami:
        await audit.log_action(
            action="update",
            resource_type="subscription",
            resource_id=str(sub.id),
            user_id=str(user.id),
            organization_id=str(org.id),
            changes_before={"plan": "pro", "seats": 10},
            changes_after={"plan": "enterprise", "seats": 50},
            summary="Zmieniono plan z Pro na Enterprise",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
        """
        # Auto-generuj summary jeśli nie podano
        if not summary and changes_before and changes_after:
            summary = self._generate_summary(changes_before, changes_after)

        log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            organization_id=organization_id,
            changes_before=changes_before,
            changes_after=changes_after,
            summary=summary,
            ip_address=ip_address,
            user_agent=user_agent,
            impersonated_by=impersonated_by,
            extra_data=extra_data,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    def _generate_summary(self, before: dict, after: dict) -> str:
        """
        Auto-generuje czytelny opis zmian.
        {"plan": "pro"} -> {"plan": "enterprise"}
        = "Zmieniono plan: pro -> enterprise"
        """
        changes = []
        all_keys = set(list(before.keys()) + list(after.keys()))
        for key in sorted(all_keys):
            old_val = before.get(key)
            new_val = after.get(key)
            if old_val != new_val:
                if old_val is None:
                    changes.append(f"Dodano {key}: {new_val}")
                elif new_val is None:
                    changes.append(f"Usunięto {key} (było: {old_val})")
                else:
                    changes.append(f"Zmieniono {key}: {old_val} → {new_val}")
        return "; ".join(changes) if changes else "Brak zmian"

    # === HELPER: automatyczne logowanie zmian w modelu ===

    async def log_model_change(
        self,
        action: str,
        model_instance,
        changed_fields: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        organization_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """
        Automatycznie loguje zmianę w modelu SQLAlchemy.

        Użycie:
        # Przed zmianą — zapisz snapshot
        before = AuditService.snapshot(subscription)

        # Zrób zmianę
        subscription.plan = "enterprise"
        subscription.seats = 50

        # Po zmianie — loguj
        await audit.log_model_change(
            action="update",
            model_instance=subscription,
            user_id=str(user.id),
            organization_id=str(org.id),
        )
        """
        resource_type = model_instance.__class__.__name__.lower()
        resource_id = str(getattr(model_instance, 'id', None))

        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(model_instance)

        before = {}
        after = {}

        for attr in inspector.attrs:
            if changed_fields and attr.key not in changed_fields:
                continue
            if attr.key.startswith('_') or attr.key in SENSITIVE_FIELDS:
                continue
            history = attr.history
            if history.has_changes():
                before[attr.key] = history.deleted[0] if history.deleted else None
                after[attr.key] = history.added[0] if history.added else None

        if not before and not after:
            return None  # Nic się nie zmieniło

        return await self.log_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            organization_id=organization_id,
            changes_before=before,
            changes_after=after,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def snapshot(model_instance) -> Dict[str, Any]:
        """
        Zrób snapshot aktualnego stanu modelu.
        Użyj PRZED zmianą żeby mieć "before".

        before = AuditService.snapshot(user)
        user.email = "nowy@email.pl"
        after = AuditService.snapshot(user)
        """
        from sqlalchemy import inspect as sa_inspect
        result = {}
        inspector = sa_inspect(model_instance)
        for attr in inspector.mapper.column_attrs:
            if attr.key in SENSITIVE_FIELDS:
                continue
            value = getattr(model_instance, attr.key)
            # Konwertuj UUID i datetime na string (JSON-serializable)
            if hasattr(value, 'hex'):  # UUID
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[attr.key] = value
        return result

    # === WYSZUKIWANIE ===

    async def get_logs(
        self,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """
        Wyszukaj logi z filtrami.

        Przykłady:
        # Wszystkie zmiany w organizacji z ostatnich 7 dni
        logs = await audit.get_logs(
            organization_id=str(org.id),
            date_from=datetime.utcnow() - timedelta(days=7),
        )

        # Kto zmieniał konkretną subskrypcję
        logs = await audit.get_logs(
            resource_type="subscription",
            resource_id=str(sub.id),
        )
        """
        query = select(AuditLog)
        conditions = []

        if organization_id:
            conditions.append(AuditLog.organization_id == organization_id)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if resource_id:
            conditions.append(AuditLog.resource_id == resource_id)
        if action:
            conditions.append(AuditLog.action == action)
        if date_from:
            conditions.append(AuditLog.created_at >= date_from)
        if date_to:
            conditions.append(AuditLog.created_at <= date_to)
        if search:
            conditions.append(
                AuditLog.summary.ilike(f"%{search}%") |
                AuditLog.ip_address.ilike(f"%{search}%") |
                AuditLog.user_email.ilike(f"%{search}%")
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # Paginacja + sortowanie
        query = query.order_by(desc(AuditLog.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return {
            "logs": logs,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_resource_history(
        self, resource_type: str, resource_id: str
    ) -> List[AuditLog]:
        """
        Historia zmian jednego zasobu (np. jednej subskrypcji).
        Przydatne: "pokaż mi historię zmian tego procesu"
        """
        query = (
            select(AuditLog)
            .where(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(desc(AuditLog.created_at))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # === RETENTION ===

    async def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """
        Usuwa logi starsze niż retention_days.
        Domyślnie: 90 dni. Minimum: 7 dni.

        Wywoływane przez scheduler (cron) raz dziennie.
        Zwraca liczbę usuniętych wpisów.
        """
        if retention_days < 7:
            retention_days = 7

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        result = await self.db.execute(
            delete(AuditLog).where(AuditLog.created_at < cutoff_date)
        )
        await self.db.commit()
        return result.rowcount

    async def get_stats(self, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """Statystyki audit logu"""
        query = select(func.count(AuditLog.id))
        if organization_id:
            query = query.where(AuditLog.organization_id == organization_id)
        total = (await self.db.execute(query)).scalar() or 0

        # Najstarszy wpis
        oldest_query = select(func.min(AuditLog.created_at))
        if organization_id:
            oldest_query = oldest_query.where(AuditLog.organization_id == organization_id)
        oldest = (await self.db.execute(oldest_query)).scalar()

        # Akcje ostatnie 24h
        last_24h_query = select(func.count(AuditLog.id)).where(
            AuditLog.created_at >= datetime.utcnow() - timedelta(hours=24)
        )
        if organization_id:
            last_24h_query = last_24h_query.where(AuditLog.organization_id == organization_id)
        last_24h = (await self.db.execute(last_24h_query)).scalar() or 0

        return {
            "total_entries": total,
            "oldest_entry": oldest.isoformat() if oldest else None,
            "entries_last_24h": last_24h,
        }
