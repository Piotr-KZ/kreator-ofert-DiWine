"""
GUS REGON API — lookup danych firmowych po NIP.
Publiczny endpoint (nie wymaga auth) — żeby działał na stronie rejestracji.
Rate limited — max 10 zapytań na minutę per IP.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from app.core.rate_limit import limiter

router = APIRouter()


class GUSLookupResponse(BaseModel):
    name: str
    nip: str
    regon: Optional[str] = None
    krs: Optional[str] = None
    legal_form: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "PL"
    pkd_main: Optional[str] = None
    pkd_main_name: Optional[str] = None
    status: str = "active"


@router.get("/gus/lookup", response_model=GUSLookupResponse)
@limiter.limit("10/minute")
async def gus_lookup(request: Request, nip: str):
    """
    Pobierz dane firmy z GUS REGON po NIP.

    Użycie: GET /api/v1/gus/lookup?nip=5261040828
    """
    from fasthub_core.integrations.gus import GUSService, GUSError

    clean_nip = nip.replace("-", "").replace(" ", "").strip()
    if len(clean_nip) != 10 or not clean_nip.isdigit():
        raise HTTPException(status_code=400, detail="NIP musi mieć 10 cyfr")

    try:
        service = GUSService()
        result = await service.lookup_by_nip(clean_nip)

        if not result:
            raise HTTPException(status_code=404, detail="Nie znaleziono firmy o podanym NIP")

        return result

    except GUSError as e:
        raise HTTPException(status_code=503, detail=str(e))
