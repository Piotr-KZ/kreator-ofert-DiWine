"""
Rate Limiting — ochrona API przed nadużyciami i DDoS.

Dwa backendy:
- Redis (produkcja): rate limit dzielony między instancjami
- Memory (dev): rate limit per proces

Użycie:
    from fasthub_core.rate_limiting import create_limiter, RateLimits

    limiter = create_limiter(app)

    @router.post("/login")
    @limiter.limit(RateLimits.AUTH_LOGIN)
    async def login(request: Request):
        ...

Konfiguracja:
    Aplikacja tworzy limiter z create_limiter() i podłącza do FastAPI app.
    Predefiniowane limity w RateLimits — można nadpisać.
"""

from typing import Optional
from fastapi import FastAPI

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


class RateLimits:
    """
    Predefiniowane limity per kategoria endpointów.

    Aplikacja może nadpisać wartości:
        RateLimits.AUTH_LOGIN = "10/minute"
    """
    # Auth — najbardziej restrykcyjne (brute-force protection)
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/hour"
    AUTH_PASSWORD_RESET = "3/hour"
    AUTH_MAGIC_LINK = "5/hour"
    AUTH_EMAIL_VERIFY = "5/hour"

    # API Tokens
    API_TOKEN_CREATE = "10/hour"
    API_TOKEN_LIST = "60/minute"

    # Public (umiarkowane)
    PUBLIC_READ = "100/minute"
    PUBLIC_WRITE = "30/minute"

    # Authenticated (mniej restrykcyjne)
    PROTECTED_READ = "200/minute"
    PROTECTED_WRITE = "60/minute"

    # Admin
    ADMIN = "100/minute"

    # Webhooks (permisywne — providerzy wysyłają wiele eventów)
    WEBHOOK = "1000/hour"

    # Default
    DEFAULT = "200/hour"


def create_limiter(
    app: Optional[FastAPI] = None,
    redis_url: Optional[str] = None,
    default_limits: Optional[list] = None,
    key_func=None,
    strategy: str = "fixed-window",
) -> Limiter:
    """
    Stwórz i skonfiguruj rate limiter.

    Args:
        app: FastAPI app (opcjonalnie — limiter dołączy się do app)
        redis_url: Redis URL. Jeśli None — próbuje z Settings, potem memory.
        default_limits: Domyślne limity (default: ["200/hour"])
        key_func: Funkcja wyciągająca klucz (default: IP klienta)
        strategy: "fixed-window" lub "moving-window"

    Returns:
        Limiter instance
    """
    # Resolve Redis URL
    if redis_url is None:
        try:
            from fasthub_core.config import get_settings
            settings = get_settings()
            redis_url = settings.REDIS_URL
        except Exception:
            redis_url = None

    storage_uri = redis_url if redis_url else "memory://"

    limiter = Limiter(
        key_func=key_func or get_remote_address,
        default_limits=default_limits or [RateLimits.DEFAULT],
        storage_uri=storage_uri,
        strategy=strategy,
        headers_enabled=True,
    )

    if app:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, get_rate_limit_handler())

    return limiter


def get_rate_limit_handler():
    """Handler dla HTTP 429 Too Many Requests."""
    return _rate_limit_exceeded_handler
