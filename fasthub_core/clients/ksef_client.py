"""
KSeF Client — HTTP client do Krajowego Systemu e-Faktur.

Wyciagniety z AutoFlow KSeF Provider — czysta warstwa HTTP.
BEZ logiki AutoFlow (CATALOG, CAPABILITIES).

Dwa tryby:
    1. Provider: KSeFClient(nip="1234567890", auth_token="xxx", environment="prod")
    2. Billing:  KSeFClient.from_config()  -> czyta KSEF_* z .env

Docs API: https://ksef.mf.gov.pl/api/v2
Srodowiska:
    - prod: https://ksef.mf.gov.pl/api/v2
    - demo: https://ksef-demo.mf.gov.pl/api/v2
    - test: https://ksef-test.mf.gov.pl/api/v2
"""

import logging
from typing import Any, Dict, Optional

from fasthub_core.clients.base_client import BaseHTTPClient

logger = logging.getLogger(__name__)


class KSeFClient(BaseHTTPClient):
    """
    HTTP client KSeF 2.0 — sesje, faktury, UPO, uprawnienia, auth v2.0.

    Dziedziczy po BaseHTTPClient (httpx, retry, timeout).
    """

    ENV_URLS = {
        "prod": "https://ksef.mf.gov.pl/api/v2",
        "demo": "https://ksef-demo.mf.gov.pl/api/v2",
        "test": "https://ksef-test.mf.gov.pl/api/v2",
    }
    LATARNIA_URL = "https://api-latarnia.ksef.mf.gov.pl"

    def __init__(
        self,
        nip: str,
        auth_method: str = "token",
        auth_token: str = "",
        certificate_base64: str = "",
        private_key_base64: str = "",
        environment: str = "test",
    ):
        base_url = self.ENV_URLS.get(environment, self.ENV_URLS["test"])
        super().__init__(base_url=base_url)
        self.nip = nip.replace("-", "").replace(" ", "")
        self.auth_method = auth_method
        self.auth_token = auth_token
        self.certificate_base64 = certificate_base64
        self.private_key_base64 = private_key_base64
        self.environment = environment
        self._access_token: Optional[str] = None
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def from_config(cls) -> "KSeFClient":
        """
        Billing mode — czyta config z .env.

        Wymagane: KSEF_NIP, KSEF_AUTH_TOKEN
        Opcjonalne: KSEF_ENVIRONMENT, KSEF_AUTH_METHOD, KSEF_CERTIFICATE_BASE64, KSEF_PRIVATE_KEY_BASE64
        """
        from fasthub_core.config import get_settings
        settings = get_settings()
        return cls(
            nip=getattr(settings, "KSEF_NIP", "") or "",
            auth_method=getattr(settings, "KSEF_AUTH_METHOD", "token"),
            auth_token=getattr(settings, "KSEF_AUTH_TOKEN", "") or "",
            certificate_base64=getattr(settings, "KSEF_CERTIFICATE_BASE64", "") or "",
            private_key_base64=getattr(settings, "KSEF_PRIVATE_KEY_BASE64", "") or "",
            environment=getattr(settings, "KSEF_ENVIRONMENT", "test"),
        )

    def is_configured(self) -> bool:
        """Czy klient ma wymagane dane do polaczenia."""
        return bool(self.nip and (self.auth_token or self.certificate_base64))

    def _update_session_token(self) -> None:
        """Update default headers with access token."""
        if self._access_token:
            self.default_headers["Authorization"] = f"Bearer {self._access_token}"
        elif "Authorization" in self.default_headers:
            del self.default_headers["Authorization"]

    # === SESJE ===

    async def open_session(self, context_nip: Optional[str] = None) -> Dict[str, Any]:
        """
        Otwiera sesje interaktywna KSeF:
        1. Pobierz challenge
        2. Podpisz AuthTokenRequest
        3. Wymien na accessToken (JWT)
        """
        nip = context_nip or self.nip

        # Step 1: Get challenge
        challenge_resp = await self.post("/sessions/challenge", json={
            "contextIdentifier": {"type": "onip", "identifier": nip}
        })
        challenge = challenge_resp.get("challenge", "")

        # Step 2: Build auth request
        if self.auth_method == "token":
            auth_data = {
                "contextIdentifier": {"type": "onip", "identifier": nip},
                "challenge": challenge,
                "token": self.auth_token,
            }
        else:
            auth_data = {
                "contextIdentifier": {"type": "onip", "identifier": nip},
                "challenge": challenge,
                "certificate": self.certificate_base64,
            }

        # Step 3: Open session
        session_resp = await self.post("/sessions/online", json=auth_data)
        self._access_token = session_resp.get("sessionToken", {}).get("token")
        self._update_session_token()
        return session_resp

    async def close_session(self, reference_number: str) -> Dict[str, Any]:
        """Zamknij sesje interaktywna."""
        return await self.post(f"/sessions/online/{reference_number}/close", json={})

    async def get_session_status(self, reference_number: str) -> Dict[str, Any]:
        """Status sesji."""
        return await self.get(f"/sessions/{reference_number}")

    # === FAKTURY — WYSYLANIE ===

    async def send_invoice(
        self, reference_number: str, invoice_xml_base64: str
    ) -> Dict[str, Any]:
        """Wyslij fakture XML w ramach otwartej sesji interaktywnej."""
        return await self.post(
            f"/sessions/online/{reference_number}/invoices",
            json={
                "invoicePayload": {
                    "type": "plain",
                    "invoiceBody": invoice_xml_base64,
                }
            },
        )

    async def send_batch(
        self, invoices_package_base64: str, package_signature_base64: str
    ) -> Dict[str, Any]:
        """Wysylka wsadowa (batch) — paczka faktur z podpisem."""
        return await self.post("/sessions/batch", json={
            "packageFile": invoices_package_base64,
            "packageSignature": package_signature_base64,
        })

    # === FAKTURY — WALIDACJA ===

    async def validate_invoice(self, invoice_xml_base64: str) -> Dict[str, Any]:
        """Walidacja faktury XML przed wysylka."""
        return await self.post("/invoices/validate", json={
            "invoicePayload": {"type": "plain", "invoiceBody": invoice_xml_base64}
        })

    # === FAKTURY — POBIERANIE ===

    async def get_invoice_by_ksef_number(self, ksef_number: str) -> Dict[str, Any]:
        """Pobierz fakture po numerze KSeF."""
        return await self.get(f"/invoices/ksef/{ksef_number}")

    async def query_invoices_sales(
        self,
        reference_number: str,
        date_from: str,
        date_to: str,
        buyer_nip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Wyszukaj faktury sprzedazy."""
        data: Dict[str, Any] = {
            "queryCriteria": {
                "type": "subject1",
                "invoicingDateFrom": date_from,
                "invoicingDateTo": date_to,
            }
        }
        if buyer_nip:
            data["queryCriteria"]["subjectType"] = "subject2"
            data["queryCriteria"]["subjectNip"] = buyer_nip
        return await self.post(
            f"/sessions/online/{reference_number}/query/invoices", json=data
        )

    async def query_invoices_purchases(
        self,
        reference_number: str,
        date_from: str,
        date_to: str,
        seller_nip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Wyszukaj faktury kosztowe."""
        data: Dict[str, Any] = {
            "queryCriteria": {
                "type": "subject2",
                "invoicingDateFrom": date_from,
                "invoicingDateTo": date_to,
            }
        }
        if seller_nip:
            data["queryCriteria"]["subjectType"] = "subject1"
            data["queryCriteria"]["subjectNip"] = seller_nip
        return await self.post(
            f"/sessions/online/{reference_number}/query/invoices", json=data
        )

    async def get_query_result(
        self, reference_number: str, query_element_reference_number: str
    ) -> Dict[str, Any]:
        """Pobierz wynik wyszukiwania faktur."""
        return await self.get(
            f"/sessions/online/{reference_number}/query/invoices/{query_element_reference_number}"
        )

    # === UPO ===

    async def get_upo(self, reference_number: str) -> Dict[str, Any]:
        """Pobierz UPO (Urzedowe Poswiadczenie Odbioru) dla sesji."""
        return await self.get(f"/sessions/{reference_number}/upo")

    # === UPRAWNIENIA ===

    async def get_permissions(self, context_nip: Optional[str] = None) -> Dict[str, Any]:
        """Sprawdz uprawnienia dla NIP."""
        nip = context_nip or self.nip
        return await self.get(f"/permissions/{nip}")

    async def grant_permission(
        self, reference_number: str, target_nip: str, permission_type: str
    ) -> Dict[str, Any]:
        """Nadaj uprawnienie."""
        return await self.post(
            f"/sessions/online/{reference_number}/permissions",
            json={
                "permissionTarget": {"type": "nip", "identifier": target_nip},
                "permissionType": permission_type,
            },
        )

    async def revoke_permission(
        self, reference_number: str, target_nip: str, permission_type: str
    ) -> Dict[str, Any]:
        """Cofnij uprawnienie."""
        return await self.delete(
            f"/sessions/online/{reference_number}/permissions/{target_nip}/{permission_type}"
        )

    # === AUTH v2.0 (JWT flow) ===

    async def get_auth_challenge(self, context_nip: Optional[str] = None) -> Dict[str, Any]:
        """Pobierz auth challenge (wazny 10 min)."""
        nip = context_nip or self.nip
        return await self.post("/auth/challenge", json={
            "contextIdentifier": {"type": "onip", "identifier": nip},
        })

    async def authenticate_xades(self, signed_xml_base64: str) -> Dict[str, Any]:
        """Uwierzytelnienie podpisem XAdES (certyfikat kwalifikowany)."""
        return await self.post("/auth/xades-signature", json={
            "signedDocument": signed_xml_base64,
        })

    async def authenticate_ksef_token(self, encrypted_token: str) -> Dict[str, Any]:
        """Uwierzytelnienie tokenem KSeF."""
        return await self.post("/auth/ksef-token", json={
            "encryptedToken": encrypted_token,
        })

    async def get_auth_status(self, reference_number: str) -> Dict[str, Any]:
        """Sprawdz status uwierzytelniania."""
        return await self.get(f"/auth/{reference_number}")

    async def redeem_token(self, authentication_token: str) -> Dict[str, Any]:
        """Wymien authenticationToken na JWT (accessToken + refreshToken)."""
        result = await self.post("/auth/token/redeem", json={
            "authenticationToken": authentication_token,
        })
        if "accessToken" in result:
            self._access_token = result["accessToken"]
            self._update_session_token()
        return result

    async def refresh_token(self, refresh_token_value: str) -> Dict[str, Any]:
        """Odswiez accessToken uzywajac refreshToken."""
        result = await self.post("/auth/token/refresh", json={
            "refreshToken": refresh_token_value,
        })
        if "accessToken" in result:
            self._access_token = result["accessToken"]
            self._update_session_token()
        return result

    # === WIZUALIZACJA ===

    async def get_invoice_visualization(
        self, ksef_number: str, format: str = "pdf", language: str = "pl"
    ) -> Dict[str, Any]:
        """Pobierz wizualizacje faktury (HTML/PDF)."""
        return await self.get(
            f"/invoices/{ksef_number}/visualization",
            params={"format": format, "language": language},
        )

    # === BATCH ===

    async def get_batch_status(self, reference_number: str) -> Dict[str, Any]:
        """Status sesji wsadowej."""
        return await self.get(f"/sessions/batch/{reference_number}/status")

    async def get_batch_rejected(self, reference_number: str) -> Dict[str, Any]:
        """Lista odrzuconych faktur w sesji wsadowej."""
        return await self.get(f"/sessions/batch/{reference_number}/rejected")

    # === STATUS SYSTEMU ===

    async def get_system_status(self) -> Dict[str, Any]:
        """Latarnia KSeF — status systemu."""
        import httpx
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.LATARNIA_URL}/status")
            resp.raise_for_status()
            return resp.json() if resp.content else {}

    async def get_system_messages(self) -> Dict[str, Any]:
        """Komunikaty techniczne MF."""
        import httpx
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.LATARNIA_URL}/messages")
            resp.raise_for_status()
            return resp.json() if resp.content else {}

    async def health_check(self) -> Dict[str, Any]:
        """Health check KSeF API."""
        return await self.get("/health")

    # === TEST ===

    async def test_connection(self) -> Dict[str, Any]:
        """Test polaczenia z KSeF."""
        await self.health_check()
        return {
            "success": True,
            "message": f"KSeF API OK ({self.environment})",
            "environment": self.environment,
            "base_url": self.base_url,
        }
