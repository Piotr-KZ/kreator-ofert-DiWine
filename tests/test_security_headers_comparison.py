"""
Test Security Headers — porównanie z wymaganiami AutoFlow.
Moduł G z Brief 10 — SecurityHeadersMiddleware z Briefu 9 powinien pokrywać wszystko.
"""

def test_security_headers_comparison():
    """Sprawdź czy wszystkie nagłówki z AutoFlow są w FastHub"""
    from fasthub_core.middleware.security_headers import SecurityHeadersMiddleware
    from starlette.testclient import TestClient
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    async def homepage(request):
        return PlainTextResponse("OK")

    app = Starlette(routes=[Route("/", homepage)])
    app.add_middleware(SecurityHeadersMiddleware)
    client = TestClient(app)
    response = client.get("/")

    # Wymagane nagłówki (z AutoFlow):
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    csp = response.headers.get("Content-Security-Policy", "")
    assert "wss:" in csp or "ws:" in csp  # WebSocket musi być dozwolony
