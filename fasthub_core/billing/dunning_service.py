"""
DunningService — zarzadza sciezka windykacyjna.

Wywolywany przez RecurringManager (cron co godzine):
1. Znajdz subskrypcje z zalegla platnoscia
2. Oblicz ile dni po terminie
3. Sprawdz jakie kroki powinny byc wykonane (a nie byly jeszcze)
4. Wykonaj kroki
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fasthub_core.billing.dunning_models import (
    DunningActionType,
    DunningEvent,
    DunningPath,
    DunningStep,
)

logger = logging.getLogger(__name__)

DEFAULT_DUNNING_STEPS = [
    {"day_offset": 0, "action_type": "retry_payment", "description": "Automatyczna proba pobrania platnosci"},
    {"day_offset": 0, "action_type": "email_reminder", "description": "Email: Termin platnosci dzis", "email_template_id": "payment_due"},
    {"day_offset": 1, "action_type": "retry_payment", "description": "Druga proba pobrania platnosci"},
    {"day_offset": 3, "action_type": "email_warning", "description": "Email: Platnosc zalegla 3 dni", "email_template_id": "payment_overdue"},
    {"day_offset": 3, "action_type": "notify_admin", "description": "Powiadom admina organizacji"},
    {"day_offset": 7, "action_type": "retry_payment", "description": "Trzecia proba pobrania platnosci"},
    {"day_offset": 7, "action_type": "email_warning", "description": "Email: Ostrzezenie — dostep zostanie ograniczony", "email_template_id": "payment_warning"},
    {"day_offset": 10, "action_type": "restrict_access", "description": "Ograniczenie dostepu do read-only"},
    {"day_offset": 10, "action_type": "email_warning", "description": "Email: Dostep ograniczony", "email_template_id": "access_restricted"},
    {"day_offset": 14, "action_type": "disable_sites", "description": "Wylaczenie opublikowanych stron"},
    {"day_offset": 14, "action_type": "email_final", "description": "Email: Strony wylaczone, zaplac aby przywrocic", "email_template_id": "sites_disabled"},
    {"day_offset": 21, "action_type": "block_access", "description": "Zablokowanie dostepu (tylko billing dostepny)"},
    {"day_offset": 30, "action_type": "email_final", "description": "Email: Ostateczne ostrzezenie — subskrypcja zostanie anulowana", "email_template_id": "final_warning"},
    {"day_offset": 45, "action_type": "downgrade_free", "description": "Downgrade do planu Free"},
    {"day_offset": 45, "action_type": "cancel_subscription", "description": "Anulowanie subskrypcji"},
    {"day_offset": 45, "action_type": "email_final", "description": "Email: Subskrypcja anulowana", "email_template_id": "subscription_canceled"},
]


class DunningService:
    """Zarzadza sciezka windykacyjna."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === PROCESSING ===

    async def process_overdue_subscription(self, subscription, days_overdue: int):
        """Przetworz zalegla subskrypcje — wykonaj odpowiednie kroki dunning."""
        path = await self._get_dunning_path(subscription)
        if not path:
            return

        pending_steps = await self._get_pending_steps(
            path_id=path.id,
            subscription_id=subscription.id,
            max_day_offset=days_overdue,
        )

        for step in pending_steps:
            await self._execute_step(step, subscription)

    async def _get_dunning_path(self, subscription) -> Optional[DunningPath]:
        """Pobierz sciezke dunning dla subskrypcji (po planie lub domyslna)."""
        # Try plan-specific path first
        plan_id = getattr(subscription, "plan_id", None)
        if plan_id:
            from fasthub_core.billing.models import BillingPlan
            plan_result = await self.db.execute(
                select(BillingPlan).where(BillingPlan.id == plan_id)
            )
            plan = plan_result.scalar_one_or_none()
            if plan:
                result = await self.db.execute(
                    select(DunningPath)
                    .options(selectinload(DunningPath.steps))
                    .where(
                        DunningPath.is_active == True,
                        DunningPath.applicable_plans.isnot(None),
                    )
                )
                for path in result.scalars().all():
                    plans = path.applicable_plans or []
                    if plan.slug in plans:
                        return path

        # Fallback to default path
        result = await self.db.execute(
            select(DunningPath)
            .options(selectinload(DunningPath.steps))
            .where(DunningPath.is_default == True, DunningPath.is_active == True)
        )
        return result.scalar_one_or_none()

    async def _get_pending_steps(
        self, path_id: UUID, subscription_id: UUID, max_day_offset: int
    ) -> List[DunningStep]:
        """Pobierz kroki ktore powinny byc wykonane ale jeszcze nie byly."""
        # Get all active steps up to max_day_offset
        steps_result = await self.db.execute(
            select(DunningStep).where(
                DunningStep.path_id == path_id,
                DunningStep.is_active == True,
                DunningStep.day_offset <= max_day_offset,
            ).order_by(DunningStep.day_offset)
        )
        all_steps = list(steps_result.scalars().all())

        # Get already executed events
        events_result = await self.db.execute(
            select(DunningEvent.step_id).where(
                DunningEvent.subscription_id == subscription_id,
                DunningEvent.status == "executed",
            )
        )
        executed_step_ids = {row[0] for row in events_result.all()}

        return [s for s in all_steps if s.id not in executed_step_ids]

    async def _execute_step(self, step: DunningStep, subscription):
        """Wykonaj krok dunning i zapisz DunningEvent."""
        status = "executed"
        details = {}

        try:
            action = step.action_type
            if action in (
                DunningActionType.EMAIL_REMINDER,
                DunningActionType.EMAIL_WARNING,
                DunningActionType.EMAIL_FINAL,
            ):
                details = {"template": step.email_template_id or "generic"}
                # Email sending would be here — not blocking
                logger.info(f"Dunning email ({action}) for sub {subscription.id}")

            elif action == DunningActionType.RETRY_PAYMENT:
                details = {"action": "retry_payment"}
                logger.info(f"Dunning retry payment for sub {subscription.id}")

            elif action == DunningActionType.RESTRICT_ACCESS:
                details = {"action": "restrict_access"}
                logger.info(f"Dunning restrict access for sub {subscription.id}")

            elif action == DunningActionType.BLOCK_ACCESS:
                details = {"action": "block_access"}
                logger.info(f"Dunning block access for sub {subscription.id}")

            elif action == DunningActionType.DISABLE_SITES:
                details = {"action": "disable_sites"}
                logger.info(f"Dunning disable sites for sub {subscription.id}")

            elif action == DunningActionType.DOWNGRADE_FREE:
                details = {"action": "downgrade_free"}
                logger.info(f"Dunning downgrade to free for sub {subscription.id}")

            elif action == DunningActionType.CANCEL_SUBSCRIPTION:
                details = {"action": "cancel_subscription"}
                logger.info(f"Dunning cancel subscription {subscription.id}")

            elif action == DunningActionType.NOTIFY_ADMIN:
                details = {"action": "notify_admin"}
                logger.info(f"Dunning notify admin for sub {subscription.id}")

            elif action == DunningActionType.WEBHOOK:
                details = {"action": "webhook"}
                logger.info(f"Dunning webhook for sub {subscription.id}")

        except Exception as e:
            status = "failed"
            details["error"] = str(e)
            logger.error(f"Dunning step {step.id} failed: {e}")

        # Record event
        event = DunningEvent(
            subscription_id=subscription.id,
            organization_id=subscription.organization_id,
            step_id=step.id,
            day_offset=step.day_offset,
            action_type=step.action_type,
            status=status,
            details=details,
            executed_at=datetime.utcnow(),
        )
        self.db.add(event)
        await self.db.flush()

    # === CRUD ===

    async def list_paths(self) -> List[DunningPath]:
        """Lista wszystkich sciezek dunning."""
        result = await self.db.execute(
            select(DunningPath)
            .options(selectinload(DunningPath.steps))
            .order_by(DunningPath.created_at)
        )
        return list(result.scalars().all())

    async def get_path(self, path_id: UUID) -> Optional[DunningPath]:
        """Pobierz sciezke z krokami."""
        result = await self.db.execute(
            select(DunningPath)
            .options(selectinload(DunningPath.steps))
            .where(DunningPath.id == path_id)
        )
        return result.scalar_one_or_none()

    async def create_path(
        self,
        name: str,
        description: str = None,
        steps: List[dict] = None,
        is_default: bool = False,
        applicable_plans: list = None,
    ) -> DunningPath:
        """Utworz nowa sciezke dunning."""
        path = DunningPath(
            name=name,
            description=description,
            is_default=is_default,
            applicable_plans=applicable_plans,
        )
        self.db.add(path)
        await self.db.flush()

        if steps:
            for step_data in steps:
                step = DunningStep(
                    path_id=path.id,
                    day_offset=step_data["day_offset"],
                    action_type=step_data["action_type"],
                    email_template_id=step_data.get("email_template_id"),
                    email_subject=step_data.get("email_subject"),
                    email_body_override=step_data.get("email_body_override"),
                    description=step_data.get("description"),
                )
                self.db.add(step)

        await self.db.flush()
        return await self.get_path(path.id)

    async def update_path(self, path_id: UUID, **kwargs) -> Optional[DunningPath]:
        """Aktualizuj sciezke."""
        path = await self.get_path(path_id)
        if not path:
            return None
        for key, value in kwargs.items():
            if hasattr(path, key):
                setattr(path, key, value)
        await self.db.flush()
        return path

    async def add_step(self, path_id: UUID, day_offset: int, action_type: str, **kwargs) -> DunningStep:
        """Dodaj krok do sciezki."""
        step = DunningStep(
            path_id=path_id,
            day_offset=day_offset,
            action_type=action_type,
            email_template_id=kwargs.get("email_template_id"),
            email_subject=kwargs.get("email_subject"),
            email_body_override=kwargs.get("email_body_override"),
            description=kwargs.get("description"),
        )
        self.db.add(step)
        await self.db.flush()
        return step

    async def update_step(self, step_id: UUID, **kwargs) -> Optional[DunningStep]:
        """Aktualizuj krok."""
        result = await self.db.execute(
            select(DunningStep).where(DunningStep.id == step_id)
        )
        step = result.scalar_one_or_none()
        if not step:
            return None
        for key, value in kwargs.items():
            if hasattr(step, key):
                setattr(step, key, value)
        await self.db.flush()
        return step

    async def delete_step(self, step_id: UUID) -> bool:
        """Usun krok ze sciezki."""
        result = await self.db.execute(
            select(DunningStep).where(DunningStep.id == step_id)
        )
        step = result.scalar_one_or_none()
        if not step:
            return False
        await self.db.delete(step)
        await self.db.flush()
        return True

    async def seed_default_path(self) -> DunningPath:
        """Stworz domyslna sciezke windykacyjna jesli nie istnieje."""
        result = await self.db.execute(
            select(DunningPath).where(DunningPath.is_default == True)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        return await self.create_path(
            name="Standardowa",
            description="Domyslna sciezka windykacyjna WebCreator",
            steps=DEFAULT_DUNNING_STEPS,
            is_default=True,
        )

    # === HISTORY ===

    async def get_dunning_history(
        self, subscription_id: UUID = None, organization_id: UUID = None, limit: int = 100
    ) -> List[DunningEvent]:
        """Historia akcji windykacyjnych."""
        query = select(DunningEvent).order_by(DunningEvent.executed_at.desc()).limit(limit)
        if subscription_id:
            query = query.where(DunningEvent.subscription_id == subscription_id)
        if organization_id:
            query = query.where(DunningEvent.organization_id == organization_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
