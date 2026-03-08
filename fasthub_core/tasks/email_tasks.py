"""
Email Tasks — wysyłanie emaili w tle.

Zamiast:
    # Synchronicznie — blokuje request 3 sekundy
    await smtp_transport.send(to, subject, body)

Teraz:
    # W tle — request wraca natychmiast
    from fasthub_core.tasks import enqueue_email
    await enqueue_email(to="user@example.com", subject="Witaj", body="<h1>Cześć</h1>")

Retry: 3 próby z 30s przerwą (konfiguracja w BaseWorkerSettings).
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def send_email_task(
    ctx: Dict[str, Any],
    to: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    is_html: bool = True,
) -> Dict[str, Any]:
    """
    ARQ task: wyślij email przez skonfigurowany transport (SMTP/Console).
    """
    logger.info(f"Sending email to={to}, subject='{subject}'")

    try:
        from fasthub_core.notifications.email_transport import create_email_transport
        transport = create_email_transport()

        success = await transport.send(
            to=to, subject=subject, body=body, from_email=from_email,
        )

        if success:
            logger.info(f"Email sent to={to}")
        else:
            logger.warning(f"Email send returned False for to={to}")

        return {"sent": success, "to": to, "subject": subject}

    except Exception as e:
        logger.error(f"Email send failed to={to}: {e}")
        raise  # ARQ retry
