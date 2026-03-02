"""
Health Check — endpoint /health dla monitoring i Docker.

Sprawdza:
- Database (SELECT 1)
- Redis (PING)
- Encryption (klucz dostępny?)
- Sentry (zainicjalizowany?)

Format odpowiedzi:
    {
        "status": "healthy" | "degraded" | "unhealthy",
        "timestamp": "2026-03-02T12:00:00Z",
        "version": "2.0.0",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "encryption": "active",
        }
    }

HTTP 200 = healthy/degraded, HTTP 503 = unhealthy.

Użycie:
    from fasthub_core.health import health_router
    app.include_router(health_router)
"""

from datetime import datetime
from typing import Dict, Any, Callable, Awaitable
from fastapi import APIRouter
from starlette.responses import JSONResponse

try:
    from fasthub_core.logging import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


class HealthChecker:
    """
    Rejestruj custom health checks per aplikacja.

    Użycie:
        checker = HealthChecker()
        checker.add_check("scheduler", check_scheduler_health)
        checker.add_check("ai_service", check_ai_health)
    """

    def __init__(self):
        self._checks: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {}
        self._version: str = "0.0.0"
        self._app_name: str = "fasthub"

    def configure(self, app_name: str = None, version: str = None):
        """Ustaw nazwę i wersję aplikacji."""
        if app_name:
            self._app_name = app_name
        if version:
            self._version = version

    def add_check(
        self,
        name: str,
        check_fn: Callable[[], Awaitable[Dict[str, Any]]],
    ) -> None:
        """
        Dodaj custom health check.

        check_fn musi zwracać dict z co najmniej {"status": "ok"|"error"}.

        Przykład:
            async def check_scheduler():
                return {"status": "ok", "jobs_running": 3}

            checker.add_check("scheduler", check_scheduler)
        """
        self._checks[name] = check_fn

    async def run_all(self) -> Dict[str, Any]:
        """Uruchom wszystkie health checki."""
        checks = {}
        overall = "healthy"

        # 1. Database
        try:
            from fasthub_core.db.session import async_session_maker
            from sqlalchemy import text
            async with async_session_maker() as session:
                await session.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)[:100]}"
            overall = "unhealthy"

        # 2. Redis
        try:
            from fasthub_core.infrastructure.redis import redis_health_check
            redis_h = await redis_health_check()
            checks["redis"] = redis_h.get("status", "unknown")
            if redis_h.get("status") == "error":
                checks["redis_error"] = redis_h.get("error", "")[:100]
                if overall == "healthy":
                    overall = "degraded"
        except Exception:
            checks["redis"] = "unavailable"

        # 3. Encryption
        try:
            from fasthub_core.security.encryption import is_encryption_available
            checks["encryption"] = "active" if is_encryption_available() else "inactive"
            if not is_encryption_available() and overall == "healthy":
                overall = "degraded"
        except Exception:
            checks["encryption"] = "unknown"

        # 4. Monitoring (Sentry)
        try:
            from fasthub_core.monitoring.sentry import _sentry_initialized
            checks["monitoring"] = "active" if _sentry_initialized else "inactive"
        except Exception:
            checks["monitoring"] = "unknown"

        # 5. Custom checks
        for name, check_fn in self._checks.items():
            try:
                result = await check_fn()
                checks[name] = result.get("status", "ok")
                if result.get("status") == "error" and overall == "healthy":
                    overall = "degraded"
            except Exception as e:
                checks[name] = f"error: {str(e)[:80]}"
                if overall == "healthy":
                    overall = "degraded"

        return {
            "status": overall,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "app": self._app_name,
            "version": self._version,
            "checks": checks,
        }


# Singleton
_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Zwróć globalny HealthChecker (singleton)."""
    return _checker


# ============================================================================
# Router
# ============================================================================

@router.get("/health")
async def health_endpoint():
    """
    Health check endpoint.

    HTTP 200: healthy lub degraded (działa, ale nie wszystko OK).
    HTTP 503: unhealthy (krytyczny komponent nie działa).
    """
    result = await _checker.run_all()
    status_code = 200 if result["status"] != "unhealthy" else 503
    return JSONResponse(status_code=status_code, content=result)


@router.get("/ready")
async def readiness_endpoint():
    """
    Readiness probe — czy aplikacja jest gotowa przyjmować ruch.

    Prostsze niż /health — sprawdza tylko bazę danych.
    Używane przez Kubernetes/Docker.
    """
    try:
        from fasthub_core.db.session import async_session_maker
        from sqlalchemy import text
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return JSONResponse(status_code=503, content={"ready": False})


# Alias
health_router = router
