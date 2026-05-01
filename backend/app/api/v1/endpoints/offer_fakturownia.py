"""
Fakturownia integration endpoints — generate proforma/VAT from offer, list invoices.
"""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.offer import Client, Offer, OfferSet, OfferSetItem, Packaging, Product
from app.services.offer.fakturownia_client import FakturowniaClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/offers", tags=["offer-fakturownia"])


async def _get_client(db: AsyncSession) -> FakturowniaClient:
    """Get Fakturownia client from company settings in DB."""
    from app.models.company_settings import CompanySettings
    result = await db.execute(select(CompanySettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings or not settings.fakturownia_token or not settings.fakturownia_account:
        raise HTTPException(
            status_code=400,
            detail="Fakturownia nie skonfigurowana. Wpisz token API i nazwę konta w Ustawienia → Dane DiWine."
        )
    return FakturowniaClient(
        api_token=settings.fakturownia_token,
        account_name=settings.fakturownia_account,
    )


class ProformaRequest(BaseModel):
    set_ids: list[str]  # which sets to include
    as_marketing: bool = False  # True = one line "Zestawy prezentowe marketingowe"
    payment_days: int = 14
    notes: Optional[str] = None


class ProformaResult(BaseModel):
    invoice_id: str
    invoice_number: str
    pdf_url: str
    view_url: str
    total_net: float
    total_gross: float


# ─── Shared logic ───

async def _generate_invoice(
    offer_id: str,
    data: ProformaRequest,
    kind: str,
    db: AsyncSession,
) -> ProformaResult:
    """Shared logic for proforma and VAT generation."""
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.sets).selectinload(OfferSet.items), selectinload(Offer.client))
        .where(Offer.id == offer_id)
    )
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta nie znaleziona")
    if not offer.client:
        raise HTTPException(status_code=400, detail="Brak klienta")

    selected_sets = [s for s in offer.sets if s.id in data.set_ids]
    if not selected_sets:
        raise HTTPException(status_code=400, detail="Nie wybrano zestawów")

    product_ids = set()
    for s in selected_sets:
        for item in s.items:
            if item.product_id:
                product_ids.add(item.product_id)
    products = {}
    if product_ids:
        r = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        for p in r.scalars().all():
            products[p.id] = p

    pkg_ids = {s.packaging_id for s in selected_sets if s.packaging_id}
    packagings = {}
    if pkg_ids:
        r = await db.execute(select(Packaging).where(Packaging.id.in_(pkg_ids)))
        for p in r.scalars().all():
            packagings[p.id] = p

    today = date.today().isoformat()
    client = offer.client

    if data.as_marketing:
        total_net = sum(s.total_price for s in selected_sets)
        positions = [{"name": "Zestawy prezentowe marketingowe", "quantity": 1, "price_net": round(total_net, 2), "tax": 23}]
    else:
        positions = []
        for s in selected_sets:
            pkg = packagings.get(s.packaging_id)
            if pkg:
                positions.append({"name": f"[{s.name}] {pkg.name}", "quantity": offer.quantity, "price_net": round(pkg.price, 2), "tax": 23})
            for item in sorted(s.items, key=lambda x: x.created_at):
                prod = products.get(item.product_id)
                prod_name = prod.name if prod else "Produkt"
                color_suffix = f" ({item.color_code})" if item.color_code else ""
                positions.append({"name": f"[{s.name}] {prod_name}{color_suffix}", "quantity": offer.quantity, "price_net": round(item.unit_price, 2), "tax": 23})

    fakt = await _get_client(db)

    try:
        await fakt.find_or_create_client(name=client.company_name, tax_no=client.nip, email=client.email)
    except Exception:
        pass

    try:
        inv = await fakt.create_invoice(
            buyer_name=client.company_name, buyer_tax_no=client.nip, buyer_email=client.email,
            buyer_street=getattr(client, 'reg_street', None), buyer_city=getattr(client, 'reg_city', None),
            buyer_post_code=getattr(client, 'reg_postal_code', None),
            positions=positions, kind=kind, issue_date=today, payment_days=data.payment_days,
            notes=data.notes or f"Oferta {offer.offer_number}",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Błąd Fakturownia: {e}")

    return ProformaResult(
        invoice_id=inv["invoice_id"], invoice_number=inv["invoice_number"],
        pdf_url=inv["pdf_url"], view_url=inv.get("view_url", ""),
        total_net=inv["total_net"], total_gross=inv["total_gross"],
    )


# ─── Endpoints ───

@router.post("/{offer_id}/generate-proforma")
async def generate_proforma(offer_id: str, data: ProformaRequest, db: AsyncSession = Depends(get_db)) -> ProformaResult:
    """Generate proforma in Fakturownia from selected offer sets."""
    return await _generate_invoice(offer_id, data, "proforma", db)


class VatInvoiceRequest(BaseModel):
    set_ids: list[str]
    as_marketing: bool = True  # VAT domyślnie jako marketing
    payment_days: int = 14
    notes: Optional[str] = None


@router.post("/{offer_id}/generate-vat")
async def generate_vat_invoice(
    offer_id: str,
    data: VatInvoiceRequest,
    db: AsyncSession = Depends(get_db),
) -> ProformaResult:
    """Generate VAT invoice. Same logic as proforma but kind='vat'."""
    proforma_data = ProformaRequest(
        set_ids=data.set_ids,
        as_marketing=data.as_marketing,
        payment_days=data.payment_days,
        notes=data.notes,
    )
    return await _generate_invoice(offer_id, proforma_data, "vat", db)


@router.get("/invoices/list")
async def list_fakturownia_invoices(
    db: AsyncSession = Depends(get_db),
):
    """List recent invoices from Fakturownia."""
    try:
        fakt = await _get_client(db)
        invoices = await fakt._request("GET", "/invoices.json", params={"per_page": 50})
        return [
            {
                "id": str(inv.get("id", "")),
                "number": inv.get("number", ""),
                "kind": inv.get("kind", ""),
                "buyer_name": inv.get("buyer_name", ""),
                "total_net": float(inv.get("total_price_net", 0)),
                "total_gross": float(inv.get("total_price_gross", 0)),
                "issue_date": inv.get("issue_date", ""),
                "status": inv.get("status", ""),
                "paid": inv.get("paid", False),
                "pdf_url": f"{fakt.base_url}{inv.get('view_url', '')}.pdf" if inv.get("view_url") else "",
            }
            for inv in (invoices if isinstance(invoices, list) else [])
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Błąd pobierania faktur: {e}")


@router.post("/fakturownia/test")
async def test_fakturownia(db: AsyncSession = Depends(get_db)):
    """Test connection to Fakturownia."""
    try:
        fakt = await _get_client(db)
        result = await fakt.test_connection()
        return result
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}
