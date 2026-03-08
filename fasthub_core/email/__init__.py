"""
Email templates module — Jinja2 engine + brand config + 7 default templates.
"""

from fasthub_core.email.template_engine import TemplateEngine
from fasthub_core.email.send import send_templated_email

__all__ = ["TemplateEngine", "send_templated_email"]
