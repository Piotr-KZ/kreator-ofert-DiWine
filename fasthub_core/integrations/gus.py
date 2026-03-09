"""
GUS REGON API Client — pobieranie danych firmowych po NIP.

Użycie:
    from fasthub_core.integrations.gus import GUSService

    service = GUSService()
    data = await service.lookup_by_nip("5261040828")

Tryb sandbox:
    GUS_API_KEY nie ustawiony → sandbox mode (dane testowe)
"""

import asyncio
import json
import logging
from functools import partial
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

GUS_CACHE_TTL = 86400  # 24h


class GUSError(Exception):
    """Błąd komunikacji z GUS API."""
    pass


class GUSService:
    """Serwis do pobierania danych firmowych z GUS REGON."""

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            try:
                from fasthub_core.config import get_settings
                api_key = get_settings().GUS_API_KEY
            except Exception:
                api_key = None
        self._api_key = api_key

    async def lookup_by_nip(self, nip: str) -> Optional[Dict[str, Any]]:
        """
        Pobierz dane firmy po NIP.

        Returns:
            Dict z danymi firmy lub None jeśli nie znaleziono.
        Raises:
            GUSError: Gdy API GUS jest niedostępne.
        """
        clean_nip = nip.replace("-", "").replace(" ", "").strip()

        if len(clean_nip) != 10 or not clean_nip.isdigit():
            return None

        # Sprawdź cache
        cached = await self._get_cached(clean_nip)
        if cached is not None:
            return cached

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, partial(self._sync_lookup, clean_nip)
            )
        except Exception as e:
            logger.error(f"GUS lookup failed for NIP {clean_nip}: {e}")
            raise GUSError(f"Nie udało się pobrać danych z GUS: {e}")

        # Zapisz w cache
        if result:
            await self._set_cached(clean_nip, result)

        return result

    def _sync_lookup(self, nip: str) -> Optional[Dict[str, Any]]:
        """Synchroniczne wywołanie GUS API (uruchamiane w threadpool)."""
        from gusregon import GUS

        if self._api_key:
            gus = GUS(api_key=self._api_key)
        else:
            gus = GUS(sandbox=True)

        # Pobierz podstawowe dane
        search_data = gus.search(nip=nip)
        if not search_data:
            return None

        record = search_data[0] if isinstance(search_data, list) else search_data

        # Pobierz kody PKD
        main_pkd = None
        try:
            pkd_data = gus.get_pkd(nip=nip)
            if pkd_data:
                pkd_list = pkd_data if isinstance(pkd_data, list) else [pkd_data]
                main_pkd = next(
                    (p for p in pkd_list if p.get("pkd_przewazajace") == "1"),
                    pkd_list[0] if pkd_list else None,
                )
        except Exception:
            pass

        return {
            "name": record.get("nazwa", ""),
            "nip": nip,
            "regon": record.get("regon", None),
            "krs": record.get("numerrejestrowewidencji", None),
            "legal_form": self._map_legal_form(record),
            "street": self._build_street(record),
            "city": record.get("miejscowosc", ""),
            "postal_code": record.get("kodpocztowy", ""),
            "country": "PL",
            "pkd_main": main_pkd.get("pkd_kod") if main_pkd else None,
            "pkd_main_name": main_pkd.get("pkd_nazwa") if main_pkd else None,
            "status": self._map_status(record),
        }

    def _build_street(self, record: dict) -> str:
        """Zbuduj adres ulicy z pól GUS."""
        street = record.get("ulica", "")
        number = record.get("nrNieruchomosci", "")
        local = record.get("nrLokalu", "")
        if street:
            addr = f"ul. {street} {number}".strip()
            if local:
                addr += f"/{local}"
            return addr
        return number

    def _map_legal_form(self, record: dict) -> Optional[str]:
        """Zmapuj formę prawną z kodu GUS."""
        FORMS = {
            "1": "Osoba fizyczna",
            "2": "Sp. cywilna",
            "6": "Sp. jawna",
            "7": "Sp. komandytowa",
            "8": "Sp. akcyjna",
            "9": "Sp. z o.o.",
            "116": "Sp. z o.o.",
            "117": "S.A.",
            "118": "Sp. komandytowo-akcyjna",
            "019": "Sp. partnerska",
        }
        form_code = str(record.get("formaPrawna_Symbol", record.get("formaprawna_symbol", "")))
        if form_code:
            return FORMS.get(form_code, f"Forma prawna ({form_code})")
        return None

    def _map_status(self, record: dict) -> str:
        """Zmapuj status działalności."""
        end_date = (
            record.get("dataZakonczeniaDzialalnosci")
            or record.get("datazakonczeniaDzialalnosci")
            or record.get("data_zakonczenia_dzialalnosci")
        )
        suspend_date = (
            record.get("dataZawieszeniaDzialalnosci")
            or record.get("datazawieszeniadzialalnosci")
            or record.get("data_zawieszenia_dzialalnosci")
        )
        if end_date:
            return "closed"
        if suspend_date:
            return "suspended"
        return "active"

    async def _get_cached(self, nip: str) -> Optional[Dict[str, Any]]:
        """Pobierz z cache Redis."""
        try:
            from fasthub_core.infrastructure.redis import get_cache
            result = await get_cache(f"gus:{nip}")
            if result:
                logger.debug(f"GUS cache hit for NIP {nip}")
            return result
        except Exception:
            return None

    async def _set_cached(self, nip: str, data: Dict[str, Any]) -> None:
        """Zapisz w cache Redis na 24h."""
        try:
            from fasthub_core.infrastructure.redis import set_cache
            await set_cache(f"gus:{nip}", data, ttl=GUS_CACHE_TTL)
        except Exception:
            pass
