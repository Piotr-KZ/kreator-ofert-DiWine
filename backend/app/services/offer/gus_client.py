"""
GUS REGON API client — deterministic NIP/REGON lookup.
Zero AI tokens, zero hallucinations.
"""

import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

GUS_API_URL = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzworcel.svc"
GUS_TEST_URL = "https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzworcel.svc"
GUS_TEST_KEY = "abcde12345abcde12345"


def _extract_xml_value(xml: str, tag: str) -> Optional[str]:
    """Extract value from XML by tag name."""
    for prefix in ["", "dane:", "s:"]:
        st = f"<{prefix}{tag}>"
        et = f"</{prefix}{tag}>"
        s = xml.find(st)
        if s != -1:
            s += len(st)
            e = xml.find(et, s)
            if e != -1:
                val = xml[s:e].strip()
                return val if val else None
    return None


async def lookup_by_nip(nip: str, api_key: Optional[str] = None) -> dict:
    """Look up company by NIP in GUS REGON database."""
    clean = nip.replace("-", "").replace(" ", "").strip()
    if len(clean) != 10 or not clean.isdigit():
        return {"found": False, "error": "Nieprawidłowy format NIP"}

    use_key = api_key or GUS_TEST_KEY
    use_url = GUS_API_URL if api_key else GUS_TEST_URL

    login_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/2014/07">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>http://CIS/BIR/2014/07/IUslugaBIR/Zaloguj</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:Zaloguj><ns:pKluczUzytkownika>{use_key}</ns:pKluczUzytkownika></ns:Zaloguj></soap:Body>
</soap:Envelope>"""

    search_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/PUBL/2014/07">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>http://CIS/BIR/PUBL/2014/07/IUslugaBIRzworcel/DaneSzukajPodmioty</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:DaneSzukajPodmioty><ns:pParametryWyszukiwania><ns:Nip>{clean}</ns:Nip></ns:pParametryWyszukiwania></ns:DaneSzukajPodmioty></soap:Body>
</soap:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Login
            lr = await client.post(use_url, content=login_env, headers=headers)
            if lr.status_code != 200:
                return {"found": False, "error": "Błąd logowania do GUS"}

            sid = _extract_xml_value(lr.text, "ZalogujResult")
            if not sid:
                return {"found": False, "error": "Brak sesji GUS"}

            # Search
            sr = await client.post(use_url, content=search_env, headers={**headers, "sid": sid})
            if sr.status_code != 200:
                return {"found": False, "error": "Błąd wyszukiwania GUS"}

            body = sr.text
            regon = _extract_xml_value(body, "Regon")
            name = _extract_xml_value(body, "Nazwa")
            city = _extract_xml_value(body, "Miejscowosc")
            street = _extract_xml_value(body, "Ulica")
            building = _extract_xml_value(body, "NrNieruchomosci")
            postal = _extract_xml_value(body, "KodPocztowy")
            pkd = _extract_xml_value(body, "Pkd")

            if not regon and not name:
                return {"found": False, "error": "Firma nie znaleziona w GUS"}

            address = f"ul. {street} {building}, {postal} {city}" if street else city

            # Logout
            lo_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="http://CIS/BIR/2014/07">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>http://CIS/BIR/2014/07/IUslugaBIR/Wyloguj</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:Wyloguj><ns:pIdentyfikatorSesji>{sid}</ns:pIdentyfikatorSesji></ns:Wyloguj></soap:Body>
</soap:Envelope>"""
            await client.post(use_url, content=lo_env, headers=headers)

            return {"found": True, "nip": clean, "regon": regon, "name": name,
                    "address": address, "city": city, "postal_code": postal, "pkd": pkd}

    except httpx.TimeoutException:
        return {"found": False, "error": "GUS API timeout"}
    except Exception as e:
        logger.error("GUS lookup failed: %s", e)
        return {"found": False, "error": f"Błąd GUS: {e}"}
