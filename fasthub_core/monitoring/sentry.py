"""
Sentry Error Tracking & Performance Monitoring.

Konfiguracja:
    SENTRY_DSN=https://xxx@sentry.io/yyy      (wymagane do włączenia)
    SENTRY_ENVIRONMENT=production               (default: development)
    SENTRY_TRACES_SAMPLE_RATE=0.1               (default: 10%)

Użycie:
    from fasthub_core.monitoring import init_monitoring, capture_exception

    init_monitoring()  # Raz przy starcie

    try:
        risky_operation()
    except Exception as e:
        capture_exception(e, context={"user_id": "abc", "action": "process_execute"})
"""

import logging
from typing import Optional, Dict, Any

try:
    from fasthub_core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Flaga — czy Sentry jest aktywny
_sentry_initialized = False


def init_monitoring() -> bool:
    """
    Inicjalizuj Sentry monitoring.

    Wymaga: SENTRY_DSN w settings. Bez niego — loguje warning i wraca False.

    Returns:
        True jeśli Sentry zainicjalizowany, False jeśli pominięty.
    """
    global _sentry_initialized

    try:
        from fasthub_core.config import get_settings
        settings = get_settings()
    except Exception:
        logger.warning("monitoring_skip", reason="cannot load settings") if hasattr(logger, 'warning') else None
        return False

    if not settings.SENTRY_DSN:
        logger.info("monitoring_disabled", reason="SENTRY_DSN not configured") if hasattr(logger, 'info') else None
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        logger.warning("monitoring_skip", reason="sentry-sdk not installed (pip install sentry-sdk[fastapi])") if hasattr(logger, 'warning') else None
        return False

    integrations = [
        FastApiIntegration(
            transaction_style="endpoint",
            failed_request_status_codes=[500, 502, 503, 504],
        ),
        SqlalchemyIntegration(),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        ),
    ]

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=getattr(settings, "APP_VERSION", "0.0.0"),
        integrations=integrations,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        sample_rate=1.0,
        attach_stacktrace=True,
        send_default_pii=False,
        max_breadcrumbs=50,
        before_send=_before_send_filter,
    )

    _sentry_initialized = True
    logger.info("monitoring_initialized", environment=settings.SENTRY_ENVIRONMENT) if hasattr(logger, 'info') else None
    return True


def _before_send_filter(event: dict, hint: dict) -> Optional[dict]:
    """Filtruj dane wrażliwe przed wysłaniem do Sentry."""
    if "request" in event:
        req = event["request"]
        # Headers
        if "headers" in req:
            for h in ("Authorization", "Cookie", "X-API-Key"):
                if h in req["headers"]:
                    req["headers"][h] = "[Filtered]"
        # Query string
        if "query_string" in req:
            qs = req["query_string"].lower()
            if "token" in qs or "password" in qs or "secret" in qs:
                req["query_string"] = "[Filtered]"
    return event


def capture_exception(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Wyślij wyjątek do Sentry (jeśli aktywny).

    Zawsze loguje błąd lokalnie, niezależnie od Sentry.
    """
    logger.error("exception_captured", error=str(error), context=context) if hasattr(logger, 'error') else None

    if not _sentry_initialized:
        return

    import sentry_sdk
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(
    message: str,
    level: str = "info",
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Wyślij wiadomość do Sentry."""
    if not _sentry_initialized:
        return

    import sentry_sdk
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(
    user_id: str,
    email: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> None:
    """Ustaw kontekst usera — Sentry dołączy go do wszystkich eventów."""
    if not _sentry_initialized:
        return
    import sentry_sdk
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "organization_id": organization_id,
    })


def clear_user_context() -> None:
    """Wyczyść kontekst usera (np. po logout)."""
    if not _sentry_initialized:
        return
    import sentry_sdk
    sentry_sdk.set_user(None)
