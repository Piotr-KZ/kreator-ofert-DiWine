"""
OpenAPIGenerator — generate openapi.json for AI agents.
Brief 41: minimal OpenAPI 3.0 spec exposing contact/newsletter endpoints.
"""


class OpenAPIGenerator:
    """Generate OpenAPI 3.0 spec from project configuration."""

    def generate(self, project) -> dict | None:
        """Generate OpenAPI spec. Returns None if no API endpoints configured."""
        config = project.config_json or {}
        brief = project.brief_json or {}
        forms = config.get("forms", {}) or {}
        hosting = config.get("hosting", {}) or {}

        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain or ""
        base_url = f"https://{domain}" if domain else ""

        has_contact = bool(forms.get("contact_email"))
        has_newsletter = bool(forms.get("newsletter_enabled"))

        if not has_contact and not has_newsletter:
            return None

        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": f"{brief.get('company_name') or project.name or 'Website'} API",
                "description": brief.get("description") or "",
                "version": "1.0.0",
            },
            "paths": {},
        }

        if base_url:
            spec["servers"] = [{"url": base_url}]

        if has_contact:
            spec["paths"]["/api/contact"] = {
                "post": {
                    "summary": "Submit contact form",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "message": {"type": "string"},
                                    },
                                    "required": ["email", "message"],
                                },
                            },
                        },
                    },
                    "responses": {
                        "200": {"description": "Form submitted successfully"},
                    },
                },
            }

        if has_newsletter:
            spec["paths"]["/api/newsletter"] = {
                "post": {
                    "summary": "Subscribe to newsletter",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                    },
                                    "required": ["email"],
                                },
                            },
                        },
                    },
                    "responses": {
                        "200": {"description": "Subscribed successfully"},
                    },
                },
            }

        return spec
