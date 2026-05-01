"""
Company settings endpoints — GET/PUT single record.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.company_settings import CompanySettings

router = APIRouter(prefix="/offers/company-settings", tags=["company-settings"])


class CompanySettingsSchema(PydanticBase):
    name: str = "DiWine"
    legal_form: str = ""
    nip: str = ""
    regon: str = ""
    reg_street: str = ""
    reg_number: str = ""
    reg_postal: str = ""
    reg_city: str = ""
    email: str = ""
    phone: str = ""
    www: str = ""
    person_first_name: str = ""
    person_last_name: str = ""
    person_role: str = ""
    person_phone: str = ""
    person_email: str = ""
    logo_url: str = ""


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get company settings (single record)."""
    result = await db.execute(select(CompanySettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = CompanySettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return {
        "id": settings.id,
        "name": settings.name, "legal_form": settings.legal_form,
        "nip": settings.nip, "regon": settings.regon,
        "reg_street": settings.reg_street, "reg_number": settings.reg_number,
        "reg_postal": settings.reg_postal, "reg_city": settings.reg_city,
        "email": settings.email, "phone": settings.phone, "www": settings.www,
        "person_first_name": settings.person_first_name, "person_last_name": settings.person_last_name,
        "person_role": settings.person_role, "person_phone": settings.person_phone, "person_email": settings.person_email,
        "logo_url": settings.logo_url,
    }


@router.put("")
async def update_settings(data: CompanySettingsSchema, db: AsyncSession = Depends(get_db)):
    """Update company settings."""
    result = await db.execute(select(CompanySettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = CompanySettings()
        db.add(settings)

    for field, value in data.model_dump().items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return {"ok": True}
