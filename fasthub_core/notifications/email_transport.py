"""
Transport email — wysylka maili przez SMTP.

Dwa tryby:
1. SMTP (produkcja) — prawdziwa wysylka przez serwer SMTP
2. Console (dev) — loguje tresc maila do konsoli

Wybor automatyczny: jesli SMTP_HOST jest ustawiony -> SMTP, inaczej -> Console.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailTransport(ABC):
    """Interfejs transportu email"""

    @abstractmethod
    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
    ) -> bool:
        """Wyslij email. Zwraca True jesli sukces."""
        ...


class SMTPTransport(EmailTransport):
    """Prawdziwa wysylka przez SMTP"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        from_email: str = "noreply@fasthub.app",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.default_from = from_email

    async def send(self, to: str, subject: str, body: str, from_email: Optional[str] = None) -> bool:
        """Wyslij email przez SMTP"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            msg = MIMEMultipart()
            msg["From"] = from_email or self.default_from
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            if self.use_tls:
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()
            else:
                server = smtplib.SMTP(self.host, self.port)

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Email send failed to {to}: {e}")
            return False


class ConsoleTransport(EmailTransport):
    """Dev mode — loguje email do konsoli zamiast wysylac"""

    async def send(self, to: str, subject: str, body: str, from_email: Optional[str] = None) -> bool:
        logger.info(
            f"\n{'='*60}\n"
            f"EMAIL (console mode)\n"
            f"To: {to}\n"
            f"From: {from_email or 'noreply@fasthub.app'}\n"
            f"Subject: {subject}\n"
            f"{'-'*60}\n"
            f"{body}\n"
            f"{'='*60}\n"
        )
        return True


def create_email_transport() -> EmailTransport:
    """
    Factory — tworzy transport na podstawie settings.
    SMTP jesli skonfigurowany, inaczej Console.
    """
    try:
        from fasthub_core.config import get_settings
        settings = get_settings()

        smtp_host = getattr(settings, "SMTP_HOST", None)
        if smtp_host:
            return SMTPTransport(
                host=smtp_host,
                port=getattr(settings, "SMTP_PORT", 587),
                username=getattr(settings, "SMTP_USERNAME", ""),
                password=getattr(settings, "SMTP_PASSWORD", ""),
                use_tls=getattr(settings, "SMTP_USE_TLS", True),
                from_email=getattr(settings, "SMTP_FROM_EMAIL", "noreply@fasthub.app"),
            )
    except Exception:
        pass

    return ConsoleTransport()
