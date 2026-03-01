"""
Security Headers Middleware — dodaje naglowki bezpieczenstwa do kazdego response.

Co chronia:
- X-Content-Type-Options: nosniff -> przegladarka nie zgaduje typu pliku
- X-Frame-Options: DENY -> strona nie moze byc osadzona w iframe (clickjacking)
- X-XSS-Protection: 1; mode=block -> przegladarka blokuje wykryte ataki XSS
- Strict-Transport-Security -> wymusza HTTPS
- Content-Security-Policy -> kontroluje skad moga byc ladowane zasoby
- Referrer-Policy -> kontroluje jakie dane wysylane w Referer header
- Permissions-Policy -> kontroluje dostep do API przegladarki (kamera, mikrofon)

Uzycie:
    from fasthub_core.middleware.security_headers import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware)
"""

from typing import Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware dodajacy naglowki bezpieczenstwa.

    Parametry:
        csp: Content-Security-Policy (domyslnie: restrictive)
        hsts_max_age: Strict-Transport-Security max-age (domyslnie: 1 rok)
        enable_hsts: wlacz HSTS (domyslnie False — potrzebne SSL)
        custom_headers: dodatkowe naglowki (dict)
    """

    def __init__(
        self,
        app,
        csp: Optional[str] = None,
        hsts_max_age: int = 31536000,  # 1 rok
        enable_hsts: bool = False,  # Domyslnie wylaczone (potrzebne SSL)
        custom_headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.enable_hsts = enable_hsts
        self.custom_headers = custom_headers or {}

        # Domyslny CSP — restrykcyjny ale praktyczny
        self.csp = csp or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' wss: ws:; "
            "frame-ancestors 'none'"
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Zawsze dodawane
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=()"
        )
        response.headers["Content-Security-Policy"] = self.csp

        # HSTS — tylko jesli wlaczony (wymaga SSL)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains"
            )

        # Custom headers
        for key, value in self.custom_headers.items():
            response.headers[key] = value

        return response
