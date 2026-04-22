"""
Canva MCP service stub — generates graphics via Canva MCP (banners, infographics, icons).
Currently a stub — returns None (falls back to HTML infographic templates).
Implementation will be added when Canva MCP is configured.
"""

from app.core.config import settings


class CanvaService:
    """Generate graphics via Canva MCP (banners, infographics, icons)."""

    def __init__(self):
        self.enabled = bool(getattr(settings, "CANVA_MCP_ENABLED", False))

    async def create_design(
        self,
        template_type: str,
        text_content: dict,
        brand_colors: list[str],
        size: str = "1200x630",
    ) -> str | None:
        """Create a design in Canva and return URL.

        Args:
            template_type: "banner", "infographic", "social_post", "icon_grid"
            text_content: {"title": "...", "subtitle": "...", "items": [...]}
            brand_colors: ["#2563eb", "#ffffff"]
            size: "1200x630" (landscape), "1080x1080" (square)

        Returns:
            URL of ready graphic or None
        """
        if not self.enabled:
            return None

        # TODO: implement when Canva MCP is configured
        return None

    async def create_infographic(
        self,
        infographic_type: str,
        data: dict,
        brand_colors: list[str],
    ) -> str | None:
        """Shortcut for infographics.

        E.g: create_infographic("steps",
            {"steps": [{"title": "Consultation", "desc": "..."}, ...]},
            ["#2563eb"])
        """
        return await self.create_design(
            template_type=f"infographic_{infographic_type}",
            text_content=data,
            brand_colors=brand_colors,
        )
