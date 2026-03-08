"""
Template Engine — Jinja2 email templates with override chain.

Lookup order:
1. App template dir (e.g. autoflow/templates/email/) — app overrides
2. fasthub_core default templates                    — fallback

Brand config injected automatically into every render.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

DEFAULT_TEMPLATES_DIR = str(Path(__file__).parent / "templates")


class TemplateEngine:
    """Render email templates with Jinja2 and brand injection."""

    def __init__(self, app_template_dir: Optional[str] = None):
        dirs = []
        if app_template_dir and os.path.isdir(app_template_dir):
            dirs.append(app_template_dir)
        dirs.append(DEFAULT_TEMPLATES_DIR)

        self.env = Environment(
            loader=FileSystemLoader(dirs),
            autoescape=True,
        )

    def render(self, template_name: str, context: Dict) -> Tuple[str, str]:
        """
        Render template in HTML and TXT variants.

        Returns:
            (html_content, text_content)

        Brand config is auto-injected into context.
        """
        full_context = {**self._brand_context(), **context}

        html = self._render_one(f"{template_name}.html", full_context)
        txt = self._render_one(f"{template_name}.txt", full_context)

        return html, txt

    def _render_one(self, filename: str, context: Dict) -> str:
        try:
            tmpl = self.env.get_template(filename)
            return tmpl.render(**context)
        except TemplateNotFound:
            return ""

    @staticmethod
    def _brand_context() -> Dict:
        """Load brand config from settings."""
        try:
            from fasthub_core.config import get_settings
            s = get_settings()
            return {
                "app_name": getattr(s, "EMAIL_COMPANY_NAME", "FastHub"),
                "brand_color": getattr(s, "EMAIL_BRAND_COLOR", "#4F46E5"),
                "logo_url": getattr(s, "EMAIL_BRAND_LOGO_URL", ""),
                "company_address": getattr(s, "EMAIL_COMPANY_ADDRESS", ""),
            }
        except Exception:
            return {
                "app_name": "FastHub",
                "brand_color": "#4F46E5",
                "logo_url": "",
                "company_address": "",
            }
