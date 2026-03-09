"""Testy integracji GUS REGON API (Brief 25)."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add fasthub-backend to path for app.* imports
_backend_dir = os.path.join(os.path.dirname(__file__), "..", "fasthub-backend")
if os.path.isdir(_backend_dir) and _backend_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_backend_dir))


# === IMPORTS ===

def test_gus_module_imports():
    """Moduł GUS musi być importowalny."""
    from fasthub_core.integrations.gus import GUSService, GUSError
    assert GUSService is not None
    assert GUSError is not None


def test_gus_endpoint_imports():
    """Endpoint GUS musi być importowalny."""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
    from app.api.v1.endpoints.gus import router, GUSLookupResponse
    assert router is not None
    assert GUSLookupResponse is not None


# === GUSService — NIP VALIDATION ===

@pytest.mark.asyncio
async def test_lookup_invalid_nip_too_short():
    """Za krótki NIP → None."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)
    result = await service.lookup_by_nip("12345")
    assert result is None


@pytest.mark.asyncio
async def test_lookup_invalid_nip_letters():
    """NIP z literami → None."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)
    result = await service.lookup_by_nip("ABCDEFGHIJ")
    assert result is None


@pytest.mark.asyncio
async def test_nip_cleaning():
    """Myślniki i spacje w NIP powinny być usunięte."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)
    # NIP z myślnikami ale za krótki po czyszczeniu
    result = await service.lookup_by_nip("123-45")
    assert result is None


@pytest.mark.asyncio
async def test_nip_with_dashes_valid_format():
    """NIP 526-104-08-28 powinien zostać oczyszczony do 5261040828."""
    from fasthub_core.integrations.gus import GUSService

    mock_result = {
        "name": "TEST COMPANY",
        "nip": "5261040828",
        "regon": "012100784",
        "krs": None,
        "legal_form": "Sp. z o.o.",
        "street": "ul. Testowa 1",
        "city": "Warszawa",
        "postal_code": "00-001",
        "country": "PL",
        "pkd_main": None,
        "pkd_main_name": None,
        "status": "active",
    }

    with patch.object(GUSService, '_sync_lookup', return_value=mock_result):
        with patch.object(GUSService, '_get_cached', new_callable=AsyncMock, return_value=None):
            with patch.object(GUSService, '_set_cached', new_callable=AsyncMock):
                service = GUSService(api_key=None)
                result = await service.lookup_by_nip("526-104-08-28")
                assert result is not None
                assert result["nip"] == "5261040828"


# === GUSService — LEGAL FORM MAPPING ===

def test_legal_form_mapping():
    """Kody formy prawnej → czytelna nazwa."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)

    assert service._map_legal_form({"formaPrawna_Symbol": "9"}) == "Sp. z o.o."
    assert service._map_legal_form({"formaPrawna_Symbol": "117"}) == "S.A."
    assert service._map_legal_form({"formaPrawna_Symbol": "1"}) == "Osoba fizyczna"
    assert "999" in service._map_legal_form({"formaPrawna_Symbol": "999"})


# === GUSService — STATUS MAPPING ===

def test_status_mapping_active():
    """Brak daty zakończenia → active."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)
    assert service._map_status({}) == "active"


def test_status_mapping_closed():
    """Data zakończenia → closed."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)
    assert service._map_status({"dataZakonczeniaDzialalnosci": "2024-01-01"}) == "closed"


def test_status_mapping_suspended():
    """Data zawieszenia → suspended."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)
    assert service._map_status({"dataZawieszeniaDzialalnosci": "2024-01-01"}) == "suspended"


# === GUSService — GUS UNAVAILABLE ===

@pytest.mark.asyncio
async def test_gus_unavailable_raises_error():
    """Gdy GUS API rzuca wyjątek → GUSError."""
    from fasthub_core.integrations.gus import GUSService, GUSError

    with patch.object(GUSService, '_sync_lookup', side_effect=Exception("Connection timeout")):
        with patch.object(GUSService, '_get_cached', new_callable=AsyncMock, return_value=None):
            service = GUSService(api_key=None)
            with pytest.raises(GUSError, match="Nie udało się pobrać danych z GUS"):
                await service.lookup_by_nip("5261040828")


# === GUSService — CACHE ===

@pytest.mark.asyncio
async def test_cache_hit_returns_cached():
    """Drugie wywołanie z tym samym NIP bierze z cache."""
    from fasthub_core.integrations.gus import GUSService

    cached_data = {"name": "CACHED COMPANY", "nip": "5261040828", "status": "active"}

    with patch.object(GUSService, '_get_cached', new_callable=AsyncMock, return_value=cached_data):
        service = GUSService(api_key=None)
        result = await service.lookup_by_nip("5261040828")
        assert result["name"] == "CACHED COMPANY"


# === GUSService — SYNC LOOKUP MOCK ===

@pytest.mark.asyncio
async def test_lookup_valid_nip_mocked():
    """Lookup z mockowanym GUS API zwraca poprawne dane."""
    from fasthub_core.integrations.gus import GUSService

    mock_search = [
        {
            "nazwa": "TESTOWA FIRMA SP. Z O.O.",
            "regon": "012345678",
            "numerrejestrowewidencji": "0000567890",
            "formaPrawna_Symbol": "116",
            "miejscowosc": "Kraków",
            "kodpocztowy": "30-001",
            "ulica": "Floriańska",
            "nrNieruchomosci": "15",
            "nrLokalu": "3",
        }
    ]

    with patch.object(GUSService, '_get_cached', new_callable=AsyncMock, return_value=None):
        with patch.object(GUSService, '_set_cached', new_callable=AsyncMock):
            with patch('fasthub_core.integrations.gus.GUSService._sync_lookup') as mock_lookup:
                mock_lookup.return_value = {
                    "name": "TESTOWA FIRMA SP. Z O.O.",
                    "nip": "1234567890",
                    "regon": "012345678",
                    "krs": "0000567890",
                    "legal_form": "Sp. z o.o.",
                    "street": "ul. Floriańska 15/3",
                    "city": "Kraków",
                    "postal_code": "30-001",
                    "country": "PL",
                    "pkd_main": None,
                    "pkd_main_name": None,
                    "status": "active",
                }
                service = GUSService(api_key=None)
                result = await service.lookup_by_nip("1234567890")

                assert result is not None
                assert result["name"] == "TESTOWA FIRMA SP. Z O.O."
                assert result["regon"] == "012345678"
                assert result["krs"] == "0000567890"
                assert result["city"] == "Kraków"
                assert result["status"] == "active"


# === STREET BUILDING ===

def test_build_street_full():
    """Budowanie adresu ulicy z pól GUS."""
    from fasthub_core.integrations.gus import GUSService
    service = GUSService(api_key=None)

    assert service._build_street({"ulica": "Floriańska", "nrNieruchomosci": "15", "nrLokalu": "3"}) == "ul. Floriańska 15/3"
    assert service._build_street({"ulica": "Długa", "nrNieruchomosci": "10"}) == "ul. Długa 10"
    assert service._build_street({"nrNieruchomosci": "5"}) == "5"
    assert service._build_street({}) == ""


# === AUTH SCHEMA ===

def test_register_schema_accepts_company_fields():
    """UserRegister schema akceptuje pola firmowe."""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
    from app.schemas.auth import UserRegister

    data = UserRegister(
        email="test@example.com",
        password="StrongPass1",
        full_name="Test User",
        organization_name="Test Org",
        account_type="business",
        nip="1234567890",
        regon="012345678",
        legal_form="Sp. z o.o.",
        street="ul. Testowa 1",
        city="Warszawa",
        postal_code="00-001",
    )
    assert data.account_type == "business"
    assert data.nip == "1234567890"


def test_register_schema_rejects_invalid_account_type():
    """UserRegister odrzuca nieprawidłowy account_type."""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
    from app.schemas.auth import UserRegister
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UserRegister(
            email="test@example.com",
            password="StrongPass1",
            account_type="invalid_type",
        )
