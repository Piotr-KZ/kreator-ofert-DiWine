"""
Billing payments endpoint — historia platnosci per organizacja.

GET /billing/payments — lista platnosci
GET /billing/payments/{id} — szczegoly
"""

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


class PaymentResponse(PydanticBase):
    id: UUID
    organization_id: UUID
    subscription_id: Optional[UUID] = None
    amount: int
    currency: str
    gateway_id: str
    gateway_payment_id: Optional[str] = None
    payment_method: Optional[str] = None
    payment_method_details: Optional[str] = None
    status: str
    description: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    refunded_at: Optional[str] = None
    invoice_id: Optional[UUID] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/payments", response_model=List[PaymentResponse])
async def list_payments(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    """Lista platnosci organizacji uzytkownika."""
    from fasthub_core.billing.payment_models import Payment
    from app.models.organization import Organization

    # Get user's organization
    org_result = await db.execute(
        select(Organization).where(Organization.owner_id == current_user.id).limit(1)
    )
    org = org_result.scalar_one_or_none()
    if not org:
        return []

    result = await db.execute(
        select(Payment)
        .where(Payment.organization_id == org.id)
        .order_by(Payment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Szczegoly platnosci."""
    from fasthub_core.billing.payment_models import Payment
    from app.models.organization import Organization

    # Get user's organization
    org_result = await db.execute(
        select(Organization).where(Organization.owner_id == current_user.id).limit(1)
    )
    org = org_result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.organization_id == org.id,
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
