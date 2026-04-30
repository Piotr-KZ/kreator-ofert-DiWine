"""
PDF generator — converts HTML offer to PDF using weasyprint.
"""

import logging
from io import BytesIO

logger = logging.getLogger(__name__)


def html_to_pdf(html: str) -> bytes:
    """Convert HTML string to PDF bytes using WeasyPrint."""
    try:
        from weasyprint import HTML
        pdf_buffer = BytesIO()
        HTML(string=html).write_pdf(pdf_buffer)
        return pdf_buffer.getvalue()
    except ImportError:
        logger.error("WeasyPrint not installed. Run: pip install weasyprint")
        raise RuntimeError("WeasyPrint nie zainstalowany. Uruchom: pip install weasyprint")
    except Exception as e:
        logger.error("PDF generation failed: %s", e)
        raise RuntimeError(f"Błąd generowania PDF: {e}")
