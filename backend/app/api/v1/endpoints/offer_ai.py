"""
Offer AI endpoints — email parsing, GUS lookup, text templates, personalization.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.offer import Offer, OfferSet, Product, Occasion
from app.services.offer.ai_service import OfferAIService
from app.services.offer.gus_client import lookup_by_nip

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/offers/ai", tags=["offer-ai"])


class ParseEmailRequest(BaseModel):
    email_text: str

class GusLookupRequest(BaseModel):
    nip: str

class PersonalizeRequest(BaseModel):
    template_text: str
    company_name: str = ""
    contact_person: str = ""
    contact_role: str = ""
    occasion_name: str = ""
    quantity: int = 0
    sets_summary: str = ""


@router.post("/parse-email")
async def parse_email(data: ParseEmailRequest):
    """Parse client email -> structured data. Uses AI."""
    if not data.email_text.strip():
        raise HTTPException(status_code=400, detail="Email nie może być pusty")
    service = OfferAIService()
    result = await service.parse_email(data.email_text)
    if result.get("error"):
        raise HTTPException(status_code=422, detail=result["error"])
    return result


@router.post("/gus-lookup")
async def gus_lookup(data: GusLookupRequest):
    """Look up company by NIP in GUS. No AI, deterministic."""
    return await lookup_by_nip(data.nip)


@router.get("/text-templates")
async def list_text_templates(
    block_type: str,
    occasion_code: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List text templates. block_type: greeting|why_us|fun_fact|closing"""
    return await OfferAIService.get_templates(db, block_type, occasion_code)


@router.post("/personalize-text")
async def personalize_text(data: PersonalizeRequest):
    """Personalize template with client data. Simple placeholders or AI."""
    service = OfferAIService()
    result = await service.personalize_text(
        template_text=data.template_text,
        company_name=data.company_name,
        contact_person=data.contact_person,
        contact_role=data.contact_role,
        occasion_name=data.occasion_name,
        quantity=data.quantity,
        sets_summary=data.sets_summary,
    )
    return {"personalized_text": result}
