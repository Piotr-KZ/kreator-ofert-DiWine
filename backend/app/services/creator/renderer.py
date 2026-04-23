"""
Block & Page renderer — template + slot data + visual concept → HTML.
Brief 33: slot-based templating with loops, conditions, HTML escape.
Brief 43: Visual Concept support — backgrounds, stock photos.
Brief 44: Design tokens CSS, separators disabled, Unsplash integration.
"""

import re
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockTemplate
# Separators disabled (Brief 44) — import kept for potential future use
# from app.services.creator.separators import get_separator_svg


# ─── Background helpers ───

BG_STYLES = {
    "white": "background-color:#ffffff;color:#1f2937;",
    "light_gray": "background-color:#f3f4f6;color:#1f2937;",
    "dark": "background-color:#1a1a2e;color:#f9fafb;",
    "brand_color": "color:#ffffff;",  # bg set via bg_value
    "brand_gradient": "color:#ffffff;",  # bg set via gradient
    "dark_photo_overlay": "color:#ffffff;position:relative;",
}

BG_COLORS = {
    "white": "#ffffff",
    "light_gray": "#f3f4f6",
    "dark": "#1a1a2e",
}


def _get_bg_color(vc_section: dict) -> str:
    """Resolve actual background color from visual concept section."""
    bg_type = vc_section.get("bg_type", "white")
    bg_value = vc_section.get("bg_value")
    if bg_value:
        return bg_value
    return BG_COLORS.get(bg_type, "#ffffff")


def _build_section_style(vc_section: dict) -> str:
    """Build inline CSS style string for a section based on VC."""
    bg_type = vc_section.get("bg_type", "white")
    bg_value = vc_section.get("bg_value", "")

    base = BG_STYLES.get(bg_type, BG_STYLES["white"])

    if bg_type == "brand_color" and bg_value:
        base += f"background-color:{bg_value};"
    elif bg_type == "brand_gradient" and bg_value:
        # bg_value should be primary color; we create gradient with opacity
        base += f"background:linear-gradient(135deg, {bg_value}, {bg_value}cc);"
    elif bg_type == "dark_photo_overlay":
        # Real photo URL is injected by resolve_media() before rendering.
        # Here we use photo_url from vc_section if already resolved, else dark fallback.
        resolved_url = vc_section.get("resolved_photo_url")
        if resolved_url:
            base += (
                f"background:linear-gradient(rgba(0,0,0,0.65),rgba(0,0,0,0.65)),"
                f"url('{resolved_url}') center/cover no-repeat;"
            )
        else:
            base += "background-color:#1a1a2e;"

    return base


class BlockRenderer:
    """Render a single block: html_template + slots_data → HTML."""

    def render_block(self, html_template: str, slots_data: dict) -> str:
        """Main method: replace slots in template with data."""
        html = html_template

        # 1. Loops: {{#each items}}...{{/each}}
        html = self._render_loops(html, slots_data)

        # 2. Conditions: {{#if slot}}...{{/if}}
        html = self._render_conditions(html, slots_data)

        # 3. Simple slots: {{slot_id}}
        html = self._render_slots(html, slots_data)

        # 4. Cleanup: remove unrealized slots
        html = re.sub(r"\{\{[^}]+\}\}", "", html)

        return html

    def _render_slots(self, html: str, data: dict) -> str:
        """Replace {{slot_id}} with value."""
        for key, value in data.items():
            if isinstance(value, str):
                html = html.replace(f"{{{{{key}}}}}", self._escape_html(value))
            elif isinstance(value, (int, float)):
                html = html.replace(f"{{{{{key}}}}}", str(value))
        return html

    def _render_loops(self, html: str, data: dict) -> str:
        """Handle {{#each items}}...{{/each}}."""
        pattern = r"\{\{#each (\w+)\}\}(.*?)\{\{/each\}\}"

        def replace_loop(match: re.Match) -> str:
            key = match.group(1)
            template = match.group(2)
            items = data.get(key, [])

            if not isinstance(items, list):
                return ""

            rendered = []
            for item in items:
                item_html = template
                if isinstance(item, dict):
                    # Replace {{this.field}} with values
                    for k, v in item.items():
                        item_html = item_html.replace(
                            f"{{{{this.{k}}}}}", self._escape_html(str(v))
                        )
                    # Conditions inside loop
                    item_html = self._render_conditions(
                        item_html, {f"this.{k}": v for k, v in item.items()}
                    )
                else:
                    item_html = item_html.replace(
                        "{{this}}", self._escape_html(str(item))
                    )
                rendered.append(item_html)

            return "".join(rendered)

        return re.sub(pattern, replace_loop, html, flags=re.DOTALL)

    def _render_conditions(self, html: str, data: dict) -> str:
        """Handle {{#if slot}}...{{/if}}."""
        pattern = r"\{\{#if ([\w.]+)\}\}(.*?)\{\{/if\}\}"

        def replace_condition(match: re.Match) -> str:
            key = match.group(1)
            content = match.group(2)
            value = data.get(key)

            if value and str(value).strip():
                return content
            return ""

        return re.sub(pattern, replace_condition, html, flags=re.DOTALL)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML in text slots."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )


class PageRenderer:
    """Render full page: list of sections + style + visual concept → complete HTML + CSS."""

    def __init__(self) -> None:
        self.block_renderer = BlockRenderer()

    async def resolve_media(self, project, unsplash) -> None:
        """Fetch real photos from Unsplash for sections with photo_query."""
        vc = project.visual_concept_json or {}
        vc_sections_list = vc.get("sections", [])
        vc_sections = {s["block_code"]: s for s in vc_sections_list}

        for section in project.sections:
            vc_s = vc_sections.get(section.block_code, {})
            photo_query = vc_s.get("photo_query")
            media_type = vc_s.get("media_type", "none")
            bg_type = vc_s.get("bg_type", "white")

            if photo_query and media_type in ("photo_wide", "photo_split"):
                url = await unsplash.get_photo_for_section(photo_query, media_type)
                if url:
                    slots = dict(section.slots_json or {})
                    # Insert URL into the appropriate slot
                    for slot_key in ("hero_image", "image_url", "image", "photo"):
                        if slot_key in slots:
                            slots[slot_key] = url
                            section.slots_json = slots
                            break

                    # Also store in vc_section for background rendering
                    if bg_type == "dark_photo_overlay":
                        vc_s["resolved_photo_url"] = url

        # Persist vc changes back to project
        if vc_sections_list:
            project.visual_concept_json = vc

    async def render_project_html(
        self,
        db: AsyncSession,
        project,
        fixes: Optional[list] = None,
    ) -> tuple[str, str]:
        """Render full page from project sections.

        Args:
            db: database session (to fetch block templates)
            project: Project with sections, style, and visual_concept_json
            fixes: optional CSS fixes from Vision loop

        Returns:
            (html_body, css) — ready for <body> and <style>
        """
        visual_concept = project.visual_concept_json or {}
        vc_sections = {
            s["block_code"]: s
            for s in visual_concept.get("sections", [])
        }
        sorted_sections = sorted(project.sections, key=lambda s: s.position)
        sections_html = []

        for i, section in enumerate(sorted_sections):
            if not section.is_visible:
                continue

            # Fetch block template
            result = await db.execute(
                select(BlockTemplate).where(BlockTemplate.code == section.block_code)
            )
            block = result.scalar_one_or_none()
            if not block:
                continue

            # Render block with data
            html = self.block_renderer.render_block(
                block.html_template,
                section.slots_json or {},
            )

            # Apply visual concept styling
            vc_section = vc_sections.get(section.block_code, {})
            section_style = _build_section_style(vc_section) if vc_section else ""

            # Wrap with section styling and data attributes
            style_attr = f' style="{section_style}padding:3rem 0;"' if section_style else ' style="padding:3rem 0;"'
            sections_html.append(
                f'<div data-section-id="{section.id}" '
                f'data-block-code="{section.block_code}" '
                f'data-position="{section.position}"{style_attr}>\n'
                f'  <div style="max-width:1200px;margin:0 auto;padding:0 1.5rem;">\n{html}\n  </div>\n</div>'
            )

            # Separators disabled — they look amateurish (Brief 44)
            # Logic preserved as dead code in separators/__init__.py if needed later

        html_body = "\n".join(sections_html)

        # Generate CSS from project style
        css = self._generate_css(project.style_json or {}, visual_concept)

        # Apply Vision fixes if any
        if fixes:
            css = self._apply_fixes(css, fixes)

        return html_body, css

    def _generate_css(self, style: dict, visual_concept: dict = None) -> str:
        """Generate CSS from design tokens + project style overrides."""
        primary = style.get("primary_color", style.get("color_primary", "#4F46E5"))
        secondary = style.get("secondary_color", style.get("color_secondary", "#F59E0B"))
        heading_font = style.get("heading_font", "Inter")
        body_font = style.get("body_font", "Inter")

        # Load base design tokens
        tokens_path = Path(__file__).parent / "design_tokens.css"
        base_css = tokens_path.read_text(encoding="utf-8") if tokens_path.exists() else ""

        # Google Fonts import
        fonts_css = (
            f"@import url('https://fonts.googleapis.com/css2?"
            f"family={heading_font.replace(' ', '+')}:wght@400;500;600;700;800"
            f"&family={body_font.replace(' ', '+')}:wght@300;400;500;600&display=swap');\n\n"
        )

        # Override colors from user's brief
        overrides = (
            f":root {{\n"
            f"  --color-primary: {primary};\n"
            f"  --color-secondary: {secondary};\n"
            f"  --color-primary-light: {primary}1a;\n"
            f"  --color-primary-dark: {self._darken_color(primary)};\n"
            f"  --font-family: '{body_font}', -apple-system, BlinkMacSystemFont, sans-serif;\n"
            f"  --font-family-heading: '{heading_font}', -apple-system, BlinkMacSystemFont, sans-serif;\n"
            f"}}\n\n"
        )

        # CSS reset + normalization using design tokens
        reset = (
            "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n"
            "body { font-family: var(--font-family); color: var(--color-text); line-height: var(--line-height); }\n"
            "h1, h2, h3, h4 { font-family: var(--font-family-heading); line-height: var(--line-height-heading); }\n"
            "img { max-width: 100%; height: auto; border-radius: var(--radius-image); }\n"
            "a { color: var(--color-primary); text-decoration: none; }\n"
            "a:hover { text-decoration: underline; }\n\n"
            # Scroll animations
            "@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }\n"
            "[data-section-id] { animation: fadeInUp 0.6s ease-out both; }\n"
            "[data-section-id]:nth-child(2) { animation-delay: 0.1s; }\n"
            "[data-section-id]:nth-child(3) { animation-delay: 0.2s; }\n"
            "[data-section-id]:nth-child(4) { animation-delay: 0.3s; }\n"
            "@media (prefers-reduced-motion: reduce) { [data-section-id] { animation: none; } }\n"
        )

        return fonts_css + base_css + overrides + reset

    @staticmethod
    def _darken_color(hex_color: str) -> str:
        """Darken a hex color by ~30%."""
        c = hex_color.lstrip("#")
        if len(c) != 6:
            return "#312E81"
        r = max(0, int(c[0:2], 16) - 60)
        g = max(0, int(c[2:4], 16) - 60)
        b = max(0, int(c[4:6], 16) - 60)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _apply_fixes(self, css: str, fixes: list) -> str:
        """Apply CSS fixes from Vision loop."""
        for fix in fixes:
            if "css_addition" in fix:
                element = fix.get("element", "?")
                css += f"\n/* Vision fix: {element} */\n{fix['css_addition']}\n"
        return css
