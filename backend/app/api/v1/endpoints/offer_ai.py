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
from app.models.offer import Client, Offer, OfferSet, Product, Occasion
from app.services.offer.ai_service import OfferAIService
from app.services.offer.gus_client import lookup_by_nip, lookup_by_name

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/offers/ai", tags=["offer-ai"])


class ParseEmailRequest(BaseModel):
    email_text: str

class GusLookupRequest(BaseModel):
    nip: str

class NameSearchRequest(BaseModel):
    name: str

class WebsiteLookupRequest(BaseModel):
    company_name: str
    email: Optional[str] = None

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


@router.post("/search-client-db")
async def search_client_db(data: NameSearchRequest, db: AsyncSession = Depends(get_db)):
    """Search existing clients by company name (case-insensitive)."""
    if not data.name or len(data.name.strip()) < 2:
        return {"found": False}
    result = await db.execute(
        select(Client).where(Client.company_name.ilike(f"%{data.name.strip()}%")).limit(1)
    )
    client = result.scalars().first()
    if client:
        return {
            "found": True,
            "id": client.id,
            "company_name": client.company_name,
            "nip": client.nip,
            "source": "DB",
        }
    return {"found": False}


@router.post("/search-registry-by-name")
async def search_registry_by_name(data: NameSearchRequest):
    """Search KRS/GUS by company name → return NIP."""
    return await lookup_by_name(data.name)


@router.post("/find-website")
async def find_website(data: WebsiteLookupRequest):
    """Find company website from email domain or AI search."""
    import httpx

    SKIP_DOMAINS = {"gmail.com", "wp.pl", "onet.pl", "o2.pl", "interia.pl",
                    "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "protonmail.com"}

    # 1. Try email domain
    if data.email and "@" in data.email:
        domain = data.email.split("@")[1].lower()
        if domain not in SKIP_DOMAINS:
            url = f"https://{domain}"
            try:
                async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                    r = await client.head(url)
                    if r.status_code < 400:
                        return {"found": True, "website": url, "source": "email_domain"}
            except Exception:
                # Try www subdomain
                url_www = f"https://www.{domain}"
                try:
                    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                        r = await client.head(url_www)
                        if r.status_code < 400:
                            return {"found": True, "website": url_www, "source": "email_domain"}
                except Exception:
                    pass

    # 2. Try AI to find website by company name
    if data.company_name:
        service = OfferAIService()
        try:
            from app.services.offer.ai_prompts import FIND_WEBSITE_PROMPT
            response = await service.claude.complete_json(
                system="Jesteś asystentem. Zwracasz JSON.",
                user_message=FIND_WEBSITE_PROMPT.format(company_name=data.company_name),
            )
            if isinstance(response.data, dict) and response.data.get("website"):
                return {"found": True, "website": response.data["website"], "source": "ai"}
        except Exception:
            pass

    return {"found": False}


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
