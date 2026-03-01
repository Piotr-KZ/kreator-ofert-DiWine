"""
Serwis powiadomien — centralne miejsce wysylki.

Kazde powiadomienie przechodzi przez:
1. Sprawdz preferencje usera (czy chce ten typ?)
2. Jesli channel_inapp=True -> zapisz w bazie (model Notification)
3. Jesli channel_email=True -> wyslij email (EmailTransport)

Uzycie:
    notif = NotificationService(db)
    await notif.send(
        user_id=user.id,
        type="invitation",
        title="Zaproszenie do organizacji",
        message="Jan Kowalski zaprosil Cie do Budimex Sp. z o.o.",
        link="/invitations",
        email=user.email,
    )
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete as sql_delete
from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.notifications.email_transport import EmailTransport, create_email_transport
from fasthub_core.notifications.models import Notification, NotificationPreference

logger = logging.getLogger(__name__)


# Domyslne preferencje (jesli user nie ustawil swoich)
DEFAULT_PREFERENCES = {
    "invitation":       {"inapp": True,  "email": True},
    "role_change":      {"inapp": True,  "email": True},
    "security_alert":   {"inapp": True,  "email": True},
    "billing":          {"inapp": True,  "email": True},
    "system":           {"inapp": True,  "email": False},
    "impersonation":    {"inapp": True,  "email": True},
    "approval_request": {"inapp": True,  "email": True},
    "approval_result":  {"inapp": True,  "email": False},
}

# Typy ktorych NIE MOZNA wylaczyc (bezpieczenstwo)
FORCED_TYPES = {"security_alert", "impersonation"}


class NotificationService:
    """Centralny serwis powiadomien"""

    def __init__(self, db: AsyncSession, email_transport: Optional[EmailTransport] = None):
        self.db = db
        self._email_transport = email_transport

    @property
    def email_transport(self) -> EmailTransport:
        if self._email_transport is None:
            self._email_transport = create_email_transport()
        return self._email_transport

    # === WYSYLKA ===

    async def send(
        self,
        user_id: UUID,
        type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[UUID] = None,
        triggered_by: Optional[UUID] = None,
    ) -> Dict[str, bool]:
        """
        Wyslij powiadomienie.

        Zwraca: {"inapp": True/False, "email": True/False}
        """
        result = {"inapp": False, "email": False}

        # Pobierz preferencje
        prefs = await self._get_preferences(user_id, type)

        # In-app
        if prefs["inapp"]:
            notif = Notification(
                user_id=user_id,
                organization_id=organization_id,
                type=type,
                title=title,
                message=message,
                link=link,
                triggered_by=triggered_by,
            )
            self.db.add(notif)
            await self.db.flush()
            result["inapp"] = True

        # Email
        if prefs["email"] and email:
            success = await self.email_transport.send(
                to=email,
                subject=f"[FastHub] {title}",
                body=message,
            )
            result["email"] = success

        return result

    async def send_to_many(
        self,
        user_ids: List[UUID],
        type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        emails: Optional[Dict[UUID, str]] = None,
        organization_id: Optional[UUID] = None,
        triggered_by: Optional[UUID] = None,
    ) -> int:
        """
        Wyslij powiadomienie do wielu userow.
        emails: {user_id: email_address}
        Zwraca liczbe wyslanych powiadomien in-app.
        """
        count = 0
        for uid in user_ids:
            user_email = emails.get(uid) if emails else None
            r = await self.send(
                user_id=uid,
                type=type,
                title=title,
                message=message,
                link=link,
                email=user_email,
                organization_id=organization_id,
                triggered_by=triggered_by,
            )
            if r["inapp"]:
                count += 1
        return count

    # === ODCZYT ===

    async def get_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """Pobierz powiadomienia usera"""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginacja
        query = query.order_by(desc(Notification.created_at))
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return {
            "notifications": notifications,
            "total": total,
            "unread_count": await self.get_unread_count(user_id),
            "page": page,
            "per_page": per_page,
        }

    async def get_unread_count(self, user_id: UUID) -> int:
        """Liczba nieprzeczytanych powiadomien"""
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Oznacz powiadomienie jako przeczytane"""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Oznacz WSZYSTKIE powiadomienia usera jako przeczytane"""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        return result.rowcount

    async def delete_notification(self, notification_id: UUID, user_id: UUID) -> bool:
        """Usun powiadomienie"""
        result = await self.db.execute(
            sql_delete(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        return result.rowcount > 0

    # === PREFERENCJE ===

    async def _get_preferences(self, user_id: UUID, notification_type: str) -> Dict[str, bool]:
        """Pobierz preferencje usera dla danego typu"""
        # Security types — zawsze wlaczone
        if notification_type in FORCED_TYPES:
            return {"inapp": True, "email": True}

        # Sprawdz preferencje w bazie
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type,
            )
        )
        pref = result.scalar_one_or_none()

        if pref:
            return {"inapp": pref.channel_inapp, "email": pref.channel_email}

        # Domyslne preferencje
        defaults = DEFAULT_PREFERENCES.get(notification_type, {"inapp": True, "email": False})
        return defaults

    async def get_user_preferences(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Pobierz wszystkie preferencje usera (z domyslnymi)"""
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        saved = {p.notification_type: p for p in result.scalars().all()}

        all_prefs = []
        for ntype, defaults in DEFAULT_PREFERENCES.items():
            if ntype in saved:
                pref = saved[ntype]
                all_prefs.append({
                    "type": ntype,
                    "inapp": pref.channel_inapp,
                    "email": pref.channel_email,
                    "forced": ntype in FORCED_TYPES,
                })
            else:
                all_prefs.append({
                    "type": ntype,
                    "inapp": defaults["inapp"],
                    "email": defaults["email"],
                    "forced": ntype in FORCED_TYPES,
                })

        return all_prefs

    async def update_preference(
        self,
        user_id: UUID,
        notification_type: str,
        channel_inapp: Optional[bool] = None,
        channel_email: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Zaktualizuj preferencje usera"""
        # Security types — nie mozna wylaczyc
        if notification_type in FORCED_TYPES:
            return {"inapp": True, "email": True, "forced": True}

        # Znajdz lub utworz
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.notification_type == notification_type,
            )
        )
        pref = result.scalar_one_or_none()

        if not pref:
            defaults = DEFAULT_PREFERENCES.get(notification_type, {"inapp": True, "email": False})
            pref = NotificationPreference(
                user_id=user_id,
                notification_type=notification_type,
                channel_inapp=defaults["inapp"],
                channel_email=defaults["email"],
            )
            self.db.add(pref)

        if channel_inapp is not None:
            pref.channel_inapp = channel_inapp
        if channel_email is not None:
            pref.channel_email = channel_email

        await self.db.flush()
        return {"inapp": pref.channel_inapp, "email": pref.channel_email}
