"""
Block & Page renderer — template + slot data → HTML.
Brief 33: slot-based templating with loops, conditions, HTML escape.
"""

import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockTemplate


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
    """Render full page: list of sections + style → complete HTML + CSS."""

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
            project: Project with sections and style
            fixes: optional CSS fixes from Vision loop (Brief 31)

        Returns:
            (html_body, css) — ready for <body> and <style>
        """
        sections_html = []

        for section in sorted(project.sections, key=lambda s: s.position):
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

            # Wrap with data attributes (for editing in step 6)
            sections_html.append(
                f'<div data-section-id="{section.id}" '
                f'data-block-code="{section.block_code}" '
                f'data-position="{section.position}">\n{html}\n</div>'
            )

        html_body = "\n".join(sections_html)

        # Generate CSS from project style
        css = self._generate_css(project.style_json or {})

        # Apply Vision fixes if any
        if fixes:
            css = self._apply_fixes(css, fixes)

        return html_body, css

    def _generate_css(self, style: dict) -> str:
        """Generate CSS from project style settings."""
        primary = style.get("color_primary", "#4F46E5")
        secondary = style.get("color_secondary", "#64748B")
        accent = style.get("color_accent", "#F59E0B")
        heading_font = style.get("heading_font", "Outfit")
        body_font = style.get("body_font", "Inter")
        radius = style.get("border_radius", "rounded")

        radius_map = {
            "sharp": "0",
            "rounded-sm": "0.375rem",
            "rounded": "0.75rem",
        }

        return (
            f"@import url('https://fonts.googleapis.com/css2?"
            f"family={heading_font.replace(' ', '+')}:wght@400;500;600;700;800"
            f"&family={body_font.replace(' ', '+')}:wght@300;400;500;600&display=swap');\n\n"
            f":root {{\n"
            f"  --color-primary: {primary};\n"
            f"  --color-secondary: {secondary};\n"
            f"  --color-accent: {accent};\n"
            f"  --font-heading: '{heading_font}', system-ui;\n"
            f"  --font-body: '{body_font}', system-ui;\n"
            f"  --radius: {radius_map.get(radius, '0.75rem')};\n"
            f"}}\n\n"
            f"body {{ font-family: var(--font-body); color: #1f2937; }}\n"
            f"h1, h2, h3, h4 {{ font-family: var(--font-heading); }}\n"
        )

    def _apply_fixes(self, css: str, fixes: list) -> str:
        """Apply CSS fixes from Vision loop."""
        for fix in fixes:
            if "css_addition" in fix:
                element = fix.get("element", "?")
                css += f"\n/* Vision fix: {element} */\n{fix['css_addition']}\n"
        return css
