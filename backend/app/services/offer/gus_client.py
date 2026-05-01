"""
NIP lookup — uses MF White List API (Biała Lista) as primary source.
Falls back to GUS REGON test API. Zero AI tokens.
"""

import logging
from datetime import date
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# MF White List API — free, no key, production data
MF_API = "https://wl-api.mf.gov.pl/api/search/nip"

# GUS REGON — fallback
GUS_API_URL = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
GUS_TEST_URL = "https://Wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
GUS_TEST_KEY = "abcde12345abcde12345"
NS = "http://CIS/BIR/PUBL/2014/07"
SVC = "IUslugaBIRzewnPubl"


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


async def lookup_by_name(name: str) -> dict:
    """Search KRS API by company name → return NIP if found."""
    if not name or len(name.strip()) < 3:
        return {"found": False, "error": "Za krótka nazwa do wyszukania"}

    clean_name = name.strip()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # KRS API (Ministerstwo Sprawiedliwości) — free, no key
            r = await client.get(
                "https://api-krs.ms.gov.pl/api/krs/OdsijSzukajPodpsLoadMore",
                params={"rejestr": "P", "nazwa": clean_name, "t": "1", "ac": "1"},
            )
            if r.status_code == 200:
                data = r.json()
                items = data if isinstance(data, list) else data.get("items", data.get("odppisList", []))
                if items and isinstance(items, list) and len(items) > 0:
                    first = items[0]
                    krs_nip = first.get("nip") or first.get("identNip")
                    krs_name = first.get("nazwa") or first.get("name")
                    krs_num = first.get("krsNumber") or first.get("nrKrs")
                    if krs_nip:
                        return {
                            "found": True,
                            "nip": krs_nip.replace("-", "").replace(" ", ""),
                            "name": krs_name,
                            "krs": krs_num,
                            "source": "KRS",
                        }
            # Try REGON by name (GUS test API)
            return await _lookup_gus_by_name(clean_name)
    except Exception as e:
        logger.warning("KRS name lookup failed for %s: %s", clean_name, e)
        return await _lookup_gus_by_name(clean_name)


async def _lookup_gus_by_name(name: str, api_key: Optional[str] = None) -> dict:
    """GUS REGON search by company name — fallback."""
    use_key = api_key or GUS_TEST_KEY
    use_url = GUS_API_URL if api_key else GUS_TEST_URL

    login_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{NS}">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>{NS}/{SVC}/Zaloguj</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:Zaloguj><ns:pKluczUzytkownika>{use_key}</ns:pKluczUzytkownika></ns:Zaloguj></soap:Body>
</soap:Envelope>"""

    search_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{NS}">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>{NS}/{SVC}/DaneSzukajPodmioty</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:DaneSzukajPodmioty><ns:pParametryWyszukiwania><ns:Nazwa>{name}</ns:Nazwa></ns:pParametryWyszukiwania></ns:DaneSzukajPodmioty></soap:Body>
</soap:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            lr = await client.post(use_url, content=login_env, headers=headers)
            if lr.status_code != 200:
                return {"found": False, "error": "Błąd logowania do GUS"}

            sid = _extract_xml_value(lr.text, "ZalogujResult")
            if not sid:
                return {"found": False, "error": "Brak sesji GUS"}

            sr = await client.post(use_url, content=search_env, headers={**headers, "sid": sid})

            # Logout
            lo_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{NS}">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>{NS}/{SVC}/Wyloguj</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:Wyloguj><ns:pIdentyfikatorSesji>{sid}</ns:pIdentyfikatorSesji></ns:Wyloguj></soap:Body>
</soap:Envelope>"""
            await client.post(use_url, content=lo_env, headers=headers)

            if sr.status_code != 200:
                return {"found": False, "error": "Błąd wyszukiwania GUS"}

            body = sr.text
            nip_found = _extract_xml_value(body, "Nip")
            name_found = _extract_xml_value(body, "Nazwa")

            if nip_found:
                return {
                    "found": True,
                    "nip": nip_found,
                    "name": name_found,
                    "source": "GUS REGON (nazwa)",
                }
            return {"found": False, "error": "Nie znaleziono w rejestrach"}

    except Exception as e:
        logger.warning("GUS name lookup failed for %s: %s", name, e)
        return {"found": False, "error": f"Błąd wyszukiwania: {e}"}


async def lookup_by_nip(nip: str, api_key: Optional[str] = None) -> dict:
    """Look up company by NIP. Primary: MF White List, fallback: GUS REGON."""
    clean = nip.replace("-", "").replace(" ", "").strip()
    if len(clean) != 10 or not clean.isdigit():
        return {"found": False, "error": "Nieprawidłowy format NIP"}

    # Try MF White List first
    result = await _lookup_mf(clean)
    if result.get("found"):
        return result

    # Fallback to GUS REGON
    return await _lookup_gus(clean, api_key)


async def _lookup_mf(nip: str) -> dict:
    """MF White List API — free, production data, no key required."""
    try:
        today = date.today().isoformat()
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{MF_API}/{nip}", params={"date": today})
            if r.status_code != 200:
                return {"found": False}

            data = r.json()
            subject = data.get("result", {}).get("subject")
            if not subject:
                return {"found": False}

            name = subject.get("name", "")
            regon = subject.get("regon", "")
            address = subject.get("workingAddress") or subject.get("residenceAddress") or ""
            krs = subject.get("krs", "")
            status_vat = subject.get("statusVat", "")

            # Parse address (format: "ul. ULICA NR, KOD MIASTO")
            import re
            city = ""
            postal_code = ""
            street = ""
            building_number = ""
            addr_line = address

            if ", " in address:
                parts = address.rsplit(", ", 1)
                addr_line = parts[0]
                city_part = parts[1] if len(parts) > 1 else ""
                if city_part and len(city_part) > 6 and city_part[2] == "-":
                    postal_code = city_part[:6]
                    city = city_part[7:].strip()
                else:
                    city = city_part

            # Split addr_line into street + number
            # Formats: "ul. Marszałkowska 10", "Marszałkowska 10/5", "al. Jerozolimskie 100A"
            if addr_line:
                # Remove prefix ul./al./pl.
                clean_addr = re.sub(r'^(ul\.|al\.|pl\.|os\.)\s*', '', addr_line, flags=re.IGNORECASE).strip()
                # Split: last part with digits = number
                m = re.match(r'^(.+?)\s+(\d+\S*)$', clean_addr)
                if m:
                    street = m.group(1).strip()
                    building_number = m.group(2).strip()
                else:
                    street = clean_addr

            return {
                "found": True,
                "nip": nip,
                "regon": regon,
                "name": name,
                "address": address,
                "street": street,
                "building_number": building_number,
                "city": city,
                "postal_code": postal_code,
                "krs": krs,
                "status_vat": status_vat,
                "source": "MF Biała Lista",
            }

    except Exception as e:
        logger.warning("MF lookup failed for %s: %s", nip, e)
        return {"found": False}


async def _lookup_gus(nip: str, api_key: Optional[str] = None) -> dict:
    """GUS REGON SOAP fallback."""
    use_key = api_key or GUS_TEST_KEY
    use_url = GUS_API_URL if api_key else GUS_TEST_URL

    login_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{NS}">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>{NS}/{SVC}/Zaloguj</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:Zaloguj><ns:pKluczUzytkownika>{use_key}</ns:pKluczUzytkownika></ns:Zaloguj></soap:Body>
</soap:Envelope>"""

    search_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{NS}">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>{NS}/{SVC}/DaneSzukajPodmioty</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:DaneSzukajPodmioty><ns:pParametryWyszukiwania><ns:Nip>{nip}</ns:Nip></ns:pParametryWyszukiwania></ns:DaneSzukajPodmioty></soap:Body>
</soap:Envelope>"""

    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            lr = await client.post(use_url, content=login_env, headers=headers)
            if lr.status_code != 200:
                return {"found": False, "error": "Błąd logowania do GUS"}

            sid = _extract_xml_value(lr.text, "ZalogujResult")
            if not sid:
                return {"found": False, "error": "Brak sesji GUS"}

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
                return {"found": False, "error": "Firma nie znaleziona"}

            lo_env = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{NS}">
  <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>{NS}/{SVC}/Wyloguj</wsa:Action>
    <wsa:To>{use_url}</wsa:To>
  </soap:Header>
  <soap:Body><ns:Wyloguj><ns:pIdentyfikatorSesji>{sid}</ns:pIdentyfikatorSesji></ns:Wyloguj></soap:Body>
</soap:Envelope>"""
            await client.post(use_url, content=lo_env, headers=headers)

            return {"found": True, "nip": nip, "regon": regon, "name": name,
                    "street": street or "", "building_number": building or "",
                    "city": city, "postal_code": postal, "pkd": pkd,
                    "source": "GUS REGON"}

    except httpx.TimeoutException:
        return {"found": False, "error": "GUS API timeout"}
    except Exception as e:
        logger.error("GUS lookup failed: %s", e)
        return {"found": False, "error": f"Błąd GUS: {e}"}
