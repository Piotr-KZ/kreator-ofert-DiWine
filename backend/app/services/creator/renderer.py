"""
Block & Page renderer — template + slot data + visual concept → HTML.
Brief 33: slot-based templating with loops, conditions, HTML escape.
Brief 43: Visual Concept support — backgrounds, separators, stock photos.
"""

import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockTemplate
from app.services.creator.separators import get_separator_svg


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
        photo_query = vc_section.get("photo_query", "")
        if photo_query:
            photo_url = f"https://source.unsplash.com/1600x900/?{photo_query.replace(' ', '+')}"
            base += (
                f"background:linear-gradient(rgba(0,0,0,0.65),rgba(0,0,0,0.65)),"
                f"url('{photo_url}') center/cover no-repeat;"
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
        separator_type = visual_concept.get("separator_type", "none")

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

            # Add separator between sections with different backgrounds
            if separator_type != "none" and i < len(sorted_sections) - 1:
                next_section = sorted_sections[i + 1]
                next_vc = vc_sections.get(next_section.block_code, {})
                should_separate = vc_section.get("separator_after", False)

                if should_separate:
                    color_top = _get_bg_color(vc_section)
                    color_bottom = _get_bg_color(next_vc)

                    if color_top != color_bottom:
                        sep_svg = get_separator_svg(separator_type, color_top, color_bottom)
                        if sep_svg:
                            sections_html.append(sep_svg)

        html_body = "\n".join(sections_html)

        # Generate CSS from project style
        css = self._generate_css(project.style_json or {}, visual_concept)

        # Apply Vision fixes if any
        if fixes:
            css = self._apply_fixes(css, fixes)

        return html_body, css

    def _generate_css(self, style: dict, visual_concept: dict = None) -> str:
        """Generate CSS from project style settings + visual concept."""
        primary = style.get("primary_color", style.get("color_primary", "#4F46E5"))
        secondary = style.get("secondary_color", style.get("color_secondary", "#F59E0B"))
        accent = style.get("color_accent", primary)
        heading_font = style.get("heading_font", "Outfit")
        body_font = style.get("body_font", "Inter")
        radius = style.get("border_radius", "rounded")

        radius_map = {
            "sharp": "0",
            "rounded-sm": "0.375rem",
            "rounded": "0.75rem",
        }

        css = (
            f"@import url('https://fonts.googleapis.com/css2?"
            f"family={heading_font.replace(' ', '+')}:wght@400;500;600;700;800"
            f"&family={body_font.replace(' ', '+')}:wght@300;400;500;600&display=swap');\n\n"
            f"@font-face {{ font-display: swap; }}\n\n"
            f":root {{\n"
            f"  --color-primary: {primary};\n"
            f"  --color-secondary: {secondary};\n"
            f"  --color-accent: {accent};\n"
            f"  --font-heading: '{heading_font}', system-ui;\n"
            f"  --font-body: '{body_font}', system-ui;\n"
            f"  --radius: {radius_map.get(radius, '0.75rem')};\n"
            f"}}\n\n"
            f"* {{ margin: 0; padding: 0; box-sizing: border-box; }}\n"
            f"body {{ font-family: var(--font-body); color: #1f2937; line-height: 1.6; }}\n"
            f"h1, h2, h3, h4 {{ font-family: var(--font-heading); line-height: 1.2; }}\n"
            f"img {{ max-width: 100%; height: auto; }}\n"
            f"a {{ color: var(--color-primary); text-decoration: none; }}\n"
            f"a:hover {{ text-decoration: underline; }}\n\n"
            # Responsive
            f"@media (max-width: 768px) {{\n"
            f"  [data-section-id] {{ padding: 2rem 0 !important; }}\n"
            f"  [data-section-id] > div {{ padding: 0 1rem !important; }}\n"
            f"}}\n\n"
            # Scroll animations
            f"@keyframes fadeInUp {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}\n"
            f"[data-section-id] {{ animation: fadeInUp 0.6s ease-out both; }}\n"
            f"[data-section-id]:nth-child(2) {{ animation-delay: 0.1s; }}\n"
            f"[data-section-id]:nth-child(3) {{ animation-delay: 0.2s; }}\n"
            f"[data-section-id]:nth-child(4) {{ animation-delay: 0.3s; }}\n"
            f"@media (prefers-reduced-motion: reduce) {{ [data-section-id] {{ animation: none; }} }}\n"
        )

        return css

    def _apply_fixes(self, css: str, fixes: list) -> str:
        """Apply CSS fixes from Vision loop."""
        for fix in fixes:
            if "css_addition" in fix:
                element = fix.get("element", "?")
                css += f"\n/* Vision fix: {element} */\n{fix['css_addition']}\n"
        return css
