"""
Admin dunning endpoints — CRUD sciezek windykacyjnych + historia zdarzen.

Wszystkie endpointy wymagaja SuperAdmin.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel as PydanticBase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


# === SCHEMAS ===

class DunningStepCreate(PydanticBase):
    day_offset: int
    action_type: str
    email_template_id: Optional[str] = None
    email_subject: Optional[str] = None
    email_body_override: Optional[str] = None
    description: Optional[str] = None


class DunningStepUpdate(PydanticBase):
    day_offset: Optional[int] = None
    action_type: Optional[str] = None
    email_template_id: Optional[str] = None
    email_subject: Optional[str] = None
    email_body_override: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DunningPathCreate(PydanticBase):
    name: str
    description: Optional[str] = None
    applicable_plans: Optional[list] = None
    steps: Optional[List[DunningStepCreate]] = None


class DunningPathUpdate(PydanticBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    applicable_plans: Optional[list] = None


class DunningStepResponse(PydanticBase):
    id: UUID
    path_id: UUID
    day_offset: int
    action_type: str
    email_template_id: Optional[str] = None
    email_subject: Optional[str] = None
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class DunningPathResponse(PydanticBase):
    id: UUID
    name: str
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    applicable_plans: Optional[list] = None
    steps: List[DunningStepResponse] = []

    class Config:
        from_attributes = True


class DunningEventResponse(PydanticBase):
    id: UUID
    subscription_id: UUID
    organization_id: UUID
    step_id: Optional[UUID] = None
    day_offset: int
    action_type: str
    status: str
    details: Optional[dict] = None
    executed_at: Optional[str] = None

    class Config:
        from_attributes = True


# === ENDPOINTS ===

@router.get("/dunning/paths", response_model=List[DunningPathResponse])
async def list_dunning_paths(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lista sciezek windykacyjnych."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    return await service.list_paths()


@router.get("/dunning/paths/{path_id}", response_model=DunningPathResponse)
async def get_dunning_path(
    path_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Szczegoly sciezki z krokami."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    path = await service.get_path(path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Dunning path not found")
    return path


@router.post("/dunning/paths", response_model=DunningPathResponse, status_code=201)
async def create_dunning_path(
    data: DunningPathCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Utworz nowa sciezke."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    steps = [s.model_dump() for s in data.steps] if data.steps else None
    path = await service.create_path(
        name=data.name,
        description=data.description,
        steps=steps,
        applicable_plans=data.applicable_plans,
    )
    await db.commit()
    return path


@router.patch("/dunning/paths/{path_id}", response_model=DunningPathResponse)
async def update_dunning_path(
    path_id: UUID,
    data: DunningPathUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Aktualizuj sciezke."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    updates = data.model_dump(exclude_unset=True)
    path = await service.update_path(path_id, **updates)
    if not path:
        raise HTTPException(status_code=404, detail="Dunning path not found")
    await db.commit()
    return path


@router.delete("/dunning/paths/{path_id}", status_code=204)
async def delete_dunning_path(
    path_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Usun sciezke (nie mozna usunac domyslnej)."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    path = await service.get_path(path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Dunning path not found")
    if path.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default dunning path")
    await db.delete(path)
    await db.commit()


@router.post("/dunning/paths/{path_id}/steps", response_model=DunningStepResponse, status_code=201)
async def add_dunning_step(
    path_id: UUID,
    data: DunningStepCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Dodaj krok do sciezki."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    step = await service.add_step(
        path_id=path_id,
        day_offset=data.day_offset,
        action_type=data.action_type,
        email_template_id=data.email_template_id,
        email_subject=data.email_subject,
        email_body_override=data.email_body_override,
        description=data.description,
    )
    await db.commit()
    return step


@router.patch("/dunning/steps/{step_id}", response_model=DunningStepResponse)
async def update_dunning_step(
    step_id: UUID,
    data: DunningStepUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Aktualizuj krok."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    updates = data.model_dump(exclude_unset=True)
    step = await service.update_step(step_id, **updates)
    if not step:
        raise HTTPException(status_code=404, detail="Dunning step not found")
    await db.commit()
    return step


@router.delete("/dunning/steps/{step_id}", status_code=204)
async def delete_dunning_step(
    step_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Usun krok ze sciezki."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    deleted = await service.delete_step(step_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dunning step not found")
    await db.commit()


@router.get("/dunning/events", response_model=List[DunningEventResponse])
async def list_dunning_events(
    organization_id: Optional[UUID] = Query(None),
    subscription_id: Optional[UUID] = Query(None),
    limit: int = Query(100, le=500),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Historia akcji windykacyjnych."""
    from fasthub_core.billing.dunning_service import DunningService
    service = DunningService(db)
    return await service.get_dunning_history(
        subscription_id=subscription_id,
        organization_id=organization_id,
        limit=limit,
    )
