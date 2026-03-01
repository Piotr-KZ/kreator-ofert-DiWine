"""Testy WebSocket Manager, Security Headers, Request ID"""

import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient


# === WEBSOCKET MANAGER ===

def test_connection_manager_exists():
    """ConnectionManager i get_connection_manager musza istniec"""
    from fasthub_core.realtime.manager import ConnectionManager, get_connection_manager
    manager = get_connection_manager()
    assert isinstance(manager, ConnectionManager)


def test_connection_manager_methods():
    """ConnectionManager musi miec wszystkie wymagane metody"""
    from fasthub_core.realtime.manager import ConnectionManager
    assert hasattr(ConnectionManager, 'connect')
    assert hasattr(ConnectionManager, 'disconnect')
    assert hasattr(ConnectionManager, 'send_to_user')
    assert hasattr(ConnectionManager, 'broadcast_to_organization')
    assert hasattr(ConnectionManager, 'broadcast_all')
    assert hasattr(ConnectionManager, 'is_user_online')
    assert hasattr(ConnectionManager, 'get_online_users')
    assert hasattr(ConnectionManager, 'get_connection_count')


def test_connection_manager_initial_state():
    """Nowy ConnectionManager musi byc pusty"""
    from fasthub_core.realtime.manager import ConnectionManager
    manager = ConnectionManager()
    stats = manager.get_connection_count()
    assert stats["total_connections"] == 0
    assert stats["online_users"] == 0
    assert stats["organizations"] == 0


def test_is_user_online_false():
    """Nieistniejacy user nie jest online"""
    from fasthub_core.realtime.manager import ConnectionManager
    manager = ConnectionManager()
    assert manager.is_user_online("nonexistent-user") is False


def test_get_online_users_empty():
    """Pusta lista online userow"""
    from fasthub_core.realtime.manager import ConnectionManager
    manager = ConnectionManager()
    assert manager.get_online_users() == []
    assert manager.get_online_users("some-org") == []


def test_ws_router_exists():
    """WebSocket router musi istniec"""
    from fasthub_core.realtime.routes import router
    assert router is not None


def test_realtime_status_router_prefix():
    """Status router musi miec prefix /api/realtime"""
    from fasthub_core.realtime.status_routes import router
    assert router.prefix == "/api/realtime"


def test_realtime_status_router_has_endpoints():
    """Status router musi miec /status i /online-users"""
    from fasthub_core.realtime.status_routes import router
    routes = [r.path for r in router.routes]
    assert any("status" in r for r in routes)
    assert any("online-users" in r for r in routes)


# === SECURITY HEADERS MIDDLEWARE ===

def test_security_headers_middleware_exists():
    """SecurityHeadersMiddleware musi istniec"""
    from fasthub_core.middleware.security_headers import SecurityHeadersMiddleware
    assert SecurityHeadersMiddleware is not None


def _create_test_app_with_security(**kwargs):
    from fasthub_core.middleware.security_headers import SecurityHeadersMiddleware

    async def homepage(request):
        return PlainTextResponse("OK")

    app = Starlette(routes=[Route("/", homepage)])
    app.add_middleware(SecurityHeadersMiddleware, **kwargs)
    return app


def test_security_headers_present():
    """Wszystkie naglowki bezpieczenstwa musza byc w response"""
    app = _create_test_app_with_security()
    client = TestClient(app)
    response = client.get("/")

    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers
    assert "Content-Security-Policy" in response.headers


def test_security_headers_no_hsts_by_default():
    """HSTS domyslnie wylaczony"""
    app = _create_test_app_with_security()
    client = TestClient(app)
    response = client.get("/")
    assert "Strict-Transport-Security" not in response.headers


def test_security_headers_hsts_when_enabled():
    """HSTS wlaczony gdy enable_hsts=True"""
    app = _create_test_app_with_security(enable_hsts=True)
    client = TestClient(app)
    response = client.get("/")
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=" in response.headers["Strict-Transport-Security"]


def test_security_headers_csp_allows_websocket():
    """CSP musi pozwalac na WebSocket (wss: / ws:)"""
    app = _create_test_app_with_security()
    client = TestClient(app)
    response = client.get("/")
    csp = response.headers.get("Content-Security-Policy", "")
    assert "wss:" in csp or "ws:" in csp


def test_security_headers_custom_csp():
    """Custom CSP powinien nadpisac domyslny"""
    custom_csp = "default-src 'none'"
    app = _create_test_app_with_security(csp=custom_csp)
    client = TestClient(app)
    response = client.get("/")
    assert response.headers.get("Content-Security-Policy") == custom_csp


def test_security_headers_custom_headers():
    """Custom headers powinny byc dodane"""
    app = _create_test_app_with_security(custom_headers={"X-Custom": "test123"})
    client = TestClient(app)
    response = client.get("/")
    assert response.headers.get("X-Custom") == "test123"


# === REQUEST ID MIDDLEWARE ===

def test_request_id_middleware_exists():
    """RequestIDMiddleware musi istniec"""
    from fasthub_core.middleware.request_id import RequestIDMiddleware
    assert RequestIDMiddleware is not None


def _create_test_app_with_request_id(**kwargs):
    from fasthub_core.middleware.request_id import RequestIDMiddleware

    async def homepage(request):
        rid = getattr(request.state, 'request_id', 'none')
        return PlainTextResponse(f"Request ID: {rid}")

    app = Starlette(routes=[Route("/", homepage)])
    app.add_middleware(RequestIDMiddleware, **kwargs)
    return app


def test_request_id_in_response_header():
    """X-Request-ID musi byc w response header"""
    app = _create_test_app_with_request_id()
    client = TestClient(app)
    response = client.get("/")

    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 36  # UUID format: 8-4-4-4-12
    assert request_id.count("-") == 4


def test_request_id_unique_per_request():
    """Kazdy request musi miec inny ID"""
    app = _create_test_app_with_request_id()
    client = TestClient(app)

    r1 = client.get("/")
    r2 = client.get("/")

    id1 = r1.headers["X-Request-ID"]
    id2 = r2.headers["X-Request-ID"]
    assert id1 != id2


def test_request_id_in_request_state():
    """Endpoint musi miec dostep do request_id"""
    app = _create_test_app_with_request_id()
    client = TestClient(app)
    response = client.get("/")

    assert "Request ID:" in response.text
    assert "none" not in response.text


def test_request_id_trust_client():
    """trust_client=True powinno akceptowac ID od klienta"""
    app = _create_test_app_with_request_id(trust_client=True)
    client = TestClient(app)
    custom_id = "custom-request-id-12345678901234"
    response = client.get("/", headers={"X-Request-ID": custom_id})

    assert response.headers["X-Request-ID"] == custom_id


# === INIT IMPORTS ===

def test_realtime_init_imports():
    """Pakiet realtime musi eksportowac kluczowe elementy"""
    from fasthub_core.realtime import ConnectionManager, get_connection_manager
    assert ConnectionManager is not None
    assert callable(get_connection_manager)


def test_middleware_init_imports():
    """Pakiet middleware musi eksportowac oba middleware"""
    from fasthub_core.middleware import SecurityHeadersMiddleware, RequestIDMiddleware
    assert SecurityHeadersMiddleware is not None
    assert RequestIDMiddleware is not None
