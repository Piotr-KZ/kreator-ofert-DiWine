"""
send_templated_email — render template + send via EmailTransport.
"""

import logging
from typing import Dict, Optional

from fasthub_core.email.template_engine import TemplateEngine

logger = logging.getLogger(__name__)


async def send_templated_email(
    template_name: str,
    to: str,
    context: Dict,
    subject: Optional[str] = None,
    from_email: Optional[str] = None,
) -> bool:
    """
    Render a template and send it via the configured EmailTransport.

    Args:
        template_name: Template name (without extension), e.g. "welcome"
        to: Recipient email
        context: Template variables (subject should be in context or passed)
        subject: Email subject (overrides context["subject"])
        from_email: Sender override
    """
    try:
        from fasthub_core.config import get_settings
        settings = get_settings()
        app_dir = getattr(settings, "EMAIL_TEMPLATE_DIR", None)
    except Exception:
        app_dir = None

    engine = TemplateEngine(app_template_dir=app_dir)
    html, txt = engine.render(template_name, context)

    email_subject = subject or context.get("subject", template_name)
    body = html if html else txt

    if not body:
        logger.warning(f"Template '{template_name}' rendered empty, skipping send")
        return False

    from fasthub_core.notifications.email_transport import create_email_transport

    transport = create_email_transport()
    return await transport.send(to=to, subject=email_subject, body=body, from_email=from_email)
