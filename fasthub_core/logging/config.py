"""
Structured Logging — konfiguracja structlog.

Dwa tryby:
- Production (DEBUG=False): JSON output — parsowalne przez Datadog/ELK/CloudWatch
- Development (DEBUG=True): kolorowe, czytelne logi w konsoli

Użycie:
    from fasthub_core.logging import configure_logging, get_logger

    configure_logging()  # Raz przy starcie aplikacji
    logger = get_logger(__name__)

    logger.info("user_login", user_id="abc", ip="1.2.3.4")
    # Production: {"event": "user_login", "user_id": "abc", "ip": "1.2.3.4", ...}
    # Dev:        [INFO] user_login  user_id=abc ip=1.2.3.4
"""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict


def _add_app_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Dodaj kontekst aplikacji do każdego logu."""
    try:
        from fasthub_core.config import get_settings
        settings = get_settings()
        event_dict["app"] = settings.APP_NAME
        event_dict["version"] = settings.APP_VERSION
        event_dict["environment"] = settings.SENTRY_ENVIRONMENT
    except Exception:
        event_dict["app"] = "fasthub"
    return event_dict


def configure_logging(debug: bool = None) -> None:
    """
    Konfiguruj structured logging.

    Wywołaj RAZ przy starcie aplikacji (w lifespan/startup).

    Args:
        debug: Tryb debug. Jeśli None — pobierz z Settings.DEBUG.
    """
    if debug is None:
        try:
            from fasthub_core.config import get_settings
            debug = get_settings().DEBUG
        except Exception:
            debug = True

    log_level = logging.DEBUG if debug else logging.INFO

    # Standard library
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Wycisz głośne loggery
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Procesory structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        _add_app_context,
    ]

    if debug:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Zwróć structured logger.

    Args:
        name: Nazwa loggera (zazwyczaj __name__)

    Returns:
        structlog.BoundLogger
    """
    return structlog.get_logger(name)
