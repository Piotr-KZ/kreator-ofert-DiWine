"""
Webhook config endpoints per organizacja.

CRUD webhookow + test + deliveries log.
"""

import secrets
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel as PydanticBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


# === SCHEMAS ===

class WebhookCreate(PydanticBase):
    url: str
    events: List[str]
    description: Optional[str] = None


class WebhookUpdate(PydanticBase):
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class WebhookResponse(PydanticBase):
    id: UUID
    organization_id: UUID
    url: str
    events: list
    is_active: bool
    description: Optional[str] = None
    last_triggered_at: Optional[str] = None
    last_status_code: Optional[int] = None
    consecutive_failures: int = 0
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class WebhookWithSecretResponse(WebhookResponse):
    secret: str


class WebhookDeliveryResponse(PydanticBase):
    id: UUID
    endpoint_id: UUID
    event_type: str
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    success: bool
    error: Optional[str] = None
    attempt: int = 1
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# === HELPERS ===

async def _get_user_org(user: User, db: AsyncSession):
    """Get the user's organization."""
    from app.models.organization import Organization
    result = await db.execute(
        select(Organization).where(Organization.owner_id == user.id).limit(1)
    )
    return result.scalar_one_or_none()


# === ENDPOINTS ===

@router.get("/organizations/{org_id}/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista webhookow organizacji."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint

    result = await db.execute(
        select(WebhookEndpoint)
        .where(WebhookEndpoint.organization_id == org_id)
        .order_by(WebhookEndpoint.created_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/organizations/{org_id}/webhooks",
    response_model=WebhookWithSecretResponse,
    status_code=201,
)
async def create_webhook(
    org_id: UUID,
    data: WebhookCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Utworz webhook. Secret generowany automatycznie — pokazywany TYLKO raz."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint, WEBHOOK_EVENT_TYPES

    # Validate event types
    invalid = [e for e in data.events if e not in WEBHOOK_EVENT_TYPES]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event types: {invalid}. Valid: {WEBHOOK_EVENT_TYPES}",
        )

    generated_secret = secrets.token_hex(32)
    endpoint = WebhookEndpoint(
        organization_id=org_id,
        url=data.url,
        secret=generated_secret,
        events=data.events,
        description=data.description,
    )
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)
    return endpoint


@router.patch("/organizations/{org_id}/webhooks/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    org_id: UUID,
    webhook_id: UUID,
    data: WebhookUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Aktualizuj webhook (url, events, is_active, description)."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint

    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.organization_id == org_id,
        )
    )
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook not found")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(endpoint, key, value)

    await db.commit()
    await db.refresh(endpoint)
    return endpoint


@router.delete("/organizations/{org_id}/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(
    org_id: UUID,
    webhook_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Usun webhook."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint

    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.organization_id == org_id,
        )
    )
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook not found")

    await db.delete(endpoint)
    await db.commit()


@router.post("/organizations/{org_id}/webhooks/{webhook_id}/rotate-secret")
async def rotate_webhook_secret(
    org_id: UUID,
    webhook_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Wygeneruj nowy secret."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint

    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.organization_id == org_id,
        )
    )
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook not found")

    new_secret = secrets.token_hex(32)
    endpoint.secret = new_secret
    await db.commit()
    return {"secret": new_secret}


@router.post("/organizations/{org_id}/webhooks/{webhook_id}/test")
async def test_webhook(
    org_id: UUID,
    webhook_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Wyslij testowy webhook."""
    from fasthub_core.integrations.webhook_config import WebhookEndpoint
    from fasthub_core.integrations.webhook_dispatcher import WebhookDispatcher

    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.organization_id == org_id,
        )
    )
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook not found")

    dispatcher = WebhookDispatcher()
    return await dispatcher.send_test(endpoint, db)


@router.get(
    "/organizations/{org_id}/webhooks/{webhook_id}/deliveries",
    response_model=List[WebhookDeliveryResponse],
)
async def list_webhook_deliveries(
    org_id: UUID,
    webhook_id: UUID,
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Historia wyslanych webhookow (ostatnie N)."""
    from fasthub_core.integrations.webhook_config import WebhookDelivery, WebhookEndpoint

    # Verify webhook belongs to org
    wh_result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.organization_id == org_id,
        )
    )
    if not wh_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Webhook not found")

    result = await db.execute(
        select(WebhookDelivery)
        .where(WebhookDelivery.endpoint_id == webhook_id)
        .order_by(WebhookDelivery.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
