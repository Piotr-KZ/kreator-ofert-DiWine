"""
Logika biznesowa Super Admin.
Wszystkie operacje wymagają is_superadmin=True.
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.auth.service import create_access_token
from fasthub_core.audit.models import AuditLog
from fasthub_core.billing.models import Subscription
from fasthub_core.users.models import Member, Organization, User


class AdminService:
    """Serwis Super Admin — operacje na wszystkich organizacjach i userach"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_organizations(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        """
        Lista WSZYSTKICH organizacji z metrykami.
        search: filtruj po nazwie lub slug
        """
        query = select(Organization)

        if search:
            query = query.where(
                Organization.name.ilike(f"%{search}%")
                | Organization.slug.ilike(f"%{search}%")
            )

        # Sortowanie
        order_column = getattr(Organization, sort_by, Organization.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)

        # Liczba wyników
        total_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(total_query)).scalar()

        # Paginacja
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        organizations = result.scalars().all()

        # Dodaj statystyki per organizacja
        org_stats = []
        for org in organizations:
            members_count = await self._count_members(org.id)
            org_stats.append({
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "owner_email": await self._get_owner_email(org.owner_id),
                "members_count": members_count,
                "created_at": org.created_at,
                "subscription_plan": await self._get_plan(org.id),
                "subscription_status": await self._get_subscription_status(org.id),
                "last_activity": None,  # TODO: dodać po rozbudowie audit trail
            })

        return {
            "organizations": org_stats,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_organization_detail(self, org_id: UUID):
        """Szczegóły organizacji z listą członków"""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()
        if not org:
            return None

        # Pobierz członków
        members_result = await self.db.execute(
            select(Member).where(Member.organization_id == org_id)
        )
        members = members_result.scalars().all()

        member_details = []
        for member in members:
            user_result = await self.db.execute(
                select(User).where(User.id == member.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                member_details.append({
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": member.role.value if member.role else None,
                    "joined_at": member.joined_at,
                })

        return {
            "organization": org,
            "members": member_details,
            "members_count": len(member_details),
        }

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ):
        """Lista WSZYSTKICH użytkowników w systemie"""
        query = select(User)

        if search:
            query = query.where(
                User.email.ilike(f"%{search}%")
                | User.full_name.ilike(f"%{search}%")
            )

        query = query.order_by(desc(User.created_at))

        # Liczba wyników
        total_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(total_query)).scalar()

        # Paginacja
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        users = result.scalars().all()

        # Dodaj informacje o organizacjach per user
        user_details = []
        for user in users:
            memberships = await self._get_user_memberships(user.id)
            user_details.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superadmin": getattr(user, 'is_superadmin', False),
                "created_at": user.created_at,
                "organizations": memberships,
            })

        return {
            "users": user_details,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def impersonate_user(self, admin_user, target_user_id: str, reason: str):
        """
        Tworzy tymczasowy token do zalogowania się jako inny user.
        LOGUJE KAŻDE UŻYCIE W AUDIT TRAIL (bezpieczeństwo).
        """
        result = await self.db.execute(
            select(User).where(User.id == UUID(target_user_id))
        )
        target_user = result.scalar_one_or_none()
        if not target_user:
            return None

        # Utwórz token z krótszym czasem życia (30 min)
        token = create_access_token(
            data={
                "sub": str(target_user.id),
                "impersonated_by": str(admin_user.id),
                "impersonation": True,
            },
            expires_delta=timedelta(minutes=30),
        )

        # OBOWIĄZKOWO loguj w audit trail
        audit_log = AuditLog(
            user_id=admin_user.id,
            user_email=admin_user.email,
            action="impersonate",
            resource_type="user",
            resource_id=str(target_user.id),
            impersonated_by=admin_user.id,
            extra_data={
                "reason": reason,
                "target_email": target_user.email,
                "admin_email": admin_user.email,
            },
        )
        self.db.add(audit_log)
        await self.db.flush()

        return {
            "access_token": token,
            "token_type": "bearer",
            "impersonated_user_id": target_user.id,
            "impersonated_user_email": target_user.email,
            "expires_in_minutes": 30,
        }

    async def get_system_stats(self):
        """Globalne statystyki systemu"""
        total_orgs = (await self.db.execute(
            select(func.count(Organization.id))
        )).scalar() or 0

        total_users = (await self.db.execute(
            select(func.count(User.id))
        )).scalar() or 0

        active_subs = (await self.db.execute(
            select(func.count(Subscription.id)).where(Subscription.status == "active")
        )).scalar() or 0

        return {
            "total_organizations": total_orgs,
            "total_users": total_users,
            "active_users_last_30_days": total_users,  # TODO: wymaga pola last_login
            "total_subscriptions_active": active_subs,
            "organizations_by_plan": {},  # TODO: po pełnej integracji billing
        }

    # ---- Helpery ----

    async def _count_members(self, org_id):
        result = await self.db.execute(
            select(func.count(Member.id)).where(Member.organization_id == org_id)
        )
        return result.scalar() or 0

    async def _get_owner_email(self, owner_id):
        if not owner_id:
            return "brak"
        result = await self.db.execute(select(User).where(User.id == owner_id))
        user = result.scalar_one_or_none()
        return user.email if user else "brak"

    async def _get_plan(self, org_id):
        result = await self.db.execute(
            select(Subscription).where(Subscription.organization_id == org_id)
            .order_by(desc(Subscription.created_at)).limit(1)
        )
        sub = result.scalar_one_or_none()
        if sub:
            return sub.stripe_price_id
        return "free"

    async def _get_subscription_status(self, org_id):
        result = await self.db.execute(
            select(Subscription).where(Subscription.organization_id == org_id)
            .order_by(desc(Subscription.created_at)).limit(1)
        )
        sub = result.scalar_one_or_none()
        if sub and sub.status:
            return sub.status.value
        return "none"

    async def _get_user_memberships(self, user_id):
        result = await self.db.execute(
            select(Member, Organization)
            .join(Organization, Member.organization_id == Organization.id)
            .where(Member.user_id == user_id)
        )
        rows = result.all()
        return [
            {
                "org_name": org.name,
                "role": member.role.value if member.role else None,
                "joined_at": str(member.joined_at) if member.joined_at else None,
            }
            for member, org in rows
        ]
