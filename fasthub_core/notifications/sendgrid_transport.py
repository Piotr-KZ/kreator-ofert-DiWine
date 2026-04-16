"""
SendGrid EmailTransport — send emails via SendGrid REST API v3.

Simpler than SMTP, better deliverability tracking.
Requires: SENDGRID_API_KEY in config.
"""

import logging
from typing import Optional

from fasthub_core.notifications.email_transport import EmailTransport

logger = logging.getLogger(__name__)


class SendGridTransport(EmailTransport):
    """Send emails via SendGrid API v3 (httpx)."""

    def __init__(self, api_key: str, from_email: str = "noreply@webcreator.app"):
        self.api_key = api_key
        self.from_email = from_email

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
    ) -> bool:
        try:
            import httpx

            is_html = "<" in body and ">" in body
            content_type = "text/html" if is_html else "text/plain"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "personalizations": [{"to": [{"email": to}]}],
                        "from": {"email": from_email or self.from_email},
                        "subject": subject,
                        "content": [{"type": content_type, "value": body}],
                    },
                    timeout=30.0,
                )
                response.raise_for_status()

            logger.info(f"SendGrid email sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"SendGrid send failed to {to}: {e}")
            return False
