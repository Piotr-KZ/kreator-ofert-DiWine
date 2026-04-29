"""
Block & Page renderer — template + slot data + visual concept → HTML.
Brief 33: slot-based templating with loops, conditions, HTML escape.
Brief 43: Visual Concept support — backgrounds, stock photos.
Brief 44: Design tokens CSS, separators disabled, Unsplash integration.
Brief 47: Icon resolution (Lucide SVG), infographic rendering, better photo queries.
Brief 48: Photo shapes, bg decorations, brand motifs, photo layouts.
"""

import re
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockTemplate
from app.services.creator.icons import get_icon_svg
from app.services.creator.illustrations import get_illustration_svg
from app.services.creator.infographics import get_infographic_template
from app.services.creator.photo_shapes import get_photo_shape_css
from app.services.creator.bg_decorations import generate_decoration_html
from app.services.creator.brand_motifs import get_motif_html
from app.services.creator.photo_layouts import get_photo_layout_html


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
        base += f"background:linear-gradient(135deg, {bg_value}, {bg_value}cc);"
    elif bg_type == "dark_photo_overlay":
        resolved_url = vc_section.get("resolved_photo_url")
        if resolved_url:
            base += (
                f"background:linear-gradient(rgba(0,0,0,0.65),rgba(0,0,0,0.65)),"
                f"url('{resolved_url}') center/cover no-repeat;"
            )
        else:
            base += "background-color:#1a1a2e;"

    return base


# ─── Icon resolution patterns ───

# Matches icon references in rendered HTML: text content that is a known icon name
# inside small containers (48px divs, icon wrappers etc.)
_EMOJI_PATTERN = re.compile(
    r'([\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F'
    r'\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
    r'\U0000200D\U00002640\U00002642]+)'
)


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
                    for k, v in item.items():
                        item_html = item_html.replace(
                            f"{{{{this.{k}}}}}", self._escape_html(str(v))
                        )
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

    @staticmethod
    def _is_url(val: str) -> bool:
        """Check if a string looks like a URL (vs. a text description)."""
        return val.startswith("http://") or val.startswith("https://") or val.startswith("data:")

    @staticmethod
    def _extract_text(val) -> str:
        """Unwrap {text:"..."} objects to plain string."""
        if isinstance(val, dict):
            return val.get("text") or val.get("name") or val.get("url") or val.get("src") or ""
        return str(val) if val else ""

    async def _resolve_photo(self, unsplash, query: str, media_type: str = "photo_wide",
                             trigger_dl: bool = False):
        """Fetch a single photo from Unsplash and return (url, credit) or None."""
        photo = await unsplash.get_photo_for_section(query, media_type)
        if not photo:
            return None
        if trigger_dl:
            await unsplash.trigger_download(photo["photo_id"])
        credit = {
            "photographer_name": photo["photographer_name"],
            "photographer_url": photo["photographer_url"],
            "photo_page_url": photo["photo_page_url"],
        }
        return photo["url"], credit

    # ─── NEW: Icon resolution (Brief 47 — Problem 1) ───

    def resolve_icons_in_html(self, html: str, brand_color: str = "#4F46E5") -> str:
        """Replace Lucide icon names and emoji with SVG in rendered HTML.

        Detects icon name patterns inside small containers (48px icon wrappers)
        and replaces them with proper SVG icons from the Lucide library.

        Also replaces stray emoji characters with a generic icon SVG.
        """
        # Step 1: Replace known Lucide icon names (case-insensitive)
        # Pattern: icon name appears as escaped text inside a div
        # After render_block, icon names are HTML-escaped text like "Target" or "Shield"
        from app.services.creator.icons import _ICON_LOOKUP

        for name_lower, canonical in _ICON_LOOKUP.items():
            # Match the icon name as standalone text (word boundaries)
            # It appears as plain text after slot replacement
            escaped_name = canonical
            if escaped_name in html:
                svg = get_icon_svg(canonical, size=24, color=brand_color)
                html = html.replace(escaped_name, svg, 1)

        # Step 2: Replace any remaining emoji with a generic circle icon
        def _replace_emoji(match):
            return get_icon_svg("Circle", size=24, color=brand_color)

        html = _EMOJI_PATTERN.sub(_replace_emoji, html)

        return html

    def resolve_icons_in_slots(self, slots: dict, brand_color: str = "#4F46E5") -> dict:
        """Pre-process slots: replace icon names with SVG BEFORE template rendering.

        This handles nested items (features, services) where icon is a list item field.
        """
        for key, value in slots.items():
            # Direct icon slots
            if key == "icon" and isinstance(value, str) and not value.startswith("<"):
                svg = get_icon_svg(value, size=24, color=brand_color)
                if svg and "Circle" not in svg:
                    slots[key] = svg
                continue

            # Direct illustration slots
            if key == "illustration" and isinstance(value, str) and not value.startswith("<"):
                svg = get_illustration_svg(value, size=64, color=brand_color)
                if svg:
                    slots[key] = svg
                continue

            # Nested lists (features, services, steps, items, etc.)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "icon" in item:
                        icon_val = item["icon"]
                        if isinstance(icon_val, str) and not icon_val.startswith("<"):
                            svg = get_icon_svg(icon_val, size=24, color=brand_color)
                            if svg:
                                item["icon"] = svg
                    if isinstance(item, dict) and "illustration" in item:
                        ill_val = item["illustration"]
                        if isinstance(ill_val, str) and not ill_val.startswith("<"):
                            svg = get_illustration_svg(ill_val, size=64, color=brand_color)
                            if svg:
                                item["illustration"] = svg

        return slots

    # ─── NEW: Infographic resolution (Brief 47 — Problem 3) ───

    def resolve_infographic(self, section, vc_section: dict) -> str:
        """Render infographic HTML for a section if media_type is infographic_*.

        Args:
            section: ProjectSection with slots_json
            vc_section: visual concept data for this section

        Returns:
            Rendered infographic HTML or empty string
        """
        media_type = vc_section.get("media_type", "none")
        if not media_type.startswith("infographic_"):
            return ""

        template_name = media_type.replace("infographic_", "")
        template = get_infographic_template(template_name)
        if not template:
            return ""

        return self.block_renderer.render_block(template, section.slots_json or {})

    # ─── NEW: Photo shapes, decorations, motifs, layouts (Brief 48) ───

    @staticmethod
    def _apply_photo_shape(html: str, shape_id: str) -> str:
        """Apply photo shape CSS to all <img> tags in rendered HTML."""
        if not shape_id or shape_id == "rounded_sm":
            return html  # default — no change needed
        css = get_photo_shape_css(shape_id)
        # Add shape CSS to img style attributes
        html = re.sub(
            r'(<img\b[^>]*style=")',
            rf'\1{css}',
            html,
        )
        # imgs without style attr
        html = re.sub(
            r'(<img\b(?![^>]*style=)[^>]*)(\/?>)',
            rf'\1 style="{css}overflow:hidden;"\2',
            html,
        )
        return html

    @staticmethod
    def _apply_bg_decoration(
        inner_html: str,
        decoration_id: str,
        color: str,
        section_id: str,
    ) -> str:
        """Inject background decoration SVG into section content."""
        if not decoration_id or decoration_id == "none":
            return inner_html
        deco_html = generate_decoration_html(decoration_id, color, section_id)
        if deco_html:
            return deco_html + inner_html
        return inner_html

    @staticmethod
    def _apply_brand_motif(
        motif_id: str,
        placement: str,
        color: str,
        motif_opacity: float = 0.08,
    ) -> str:
        """Generate brand motif HTML for a specific placement."""
        if not motif_id or motif_id == "none":
            return ""
        return get_motif_html(motif_id, placement, color, motif_opacity)

    @staticmethod
    def _apply_photo_layout(
        image_urls: list[str],
        layout_id: str,
        shape_id: str = "rounded_sm",
    ) -> str:
        """Arrange multiple images in a creative layout."""
        if not layout_id or layout_id == "single":
            return ""
        shape_css = get_photo_shape_css(shape_id)
        return get_photo_layout_html(layout_id, image_urls, shape_css)

    # ─── IMPROVED: Photo query building (Brief 47 — Problem 2) ───

    @staticmethod
    def _build_smart_query(
        photo_query: str | None,
        slots: dict,
        block_code: str,
        description: str = "",
    ) -> str:
        """Build a more relevant Unsplash query from context.

        Instead of generic "business team", uses section heading + brief description
        to create targeted queries like "sales training workshop whiteboard".
        """
        # If VC already provided a good query, use it
        if photo_query and len(photo_query) > 10:
            return photo_query

        parts = []

        # Extract heading keywords (most relevant)
        heading = slots.get("heading") or slots.get("title") or ""
        if isinstance(heading, dict):
            heading = heading.get("text", "")
        if heading and len(heading) > 3:
            # Take first 4-5 meaningful words
            words = [w for w in heading.split() if len(w) > 2][:4]
            parts.extend(words)

        # Add context from block type
        _BLOCK_CONTEXT = {
            "HE": "professional hero banner",
            "FI": "company team office",
            "OF": "business services professional",
            "RO": "solution product professional",
            "PR": "process workflow team collaboration",
            "KR": "results achievement success",
            "OP": "professional person portrait headshot",
            "CT": "motivation call to action professional",
            "PB": "business challenge problem",
            "ST": "statistics data results",
            "CF": "benefits features modern",
        }
        prefix = block_code[:2] if block_code else ""
        if prefix in _BLOCK_CONTEXT:
            parts.append(_BLOCK_CONTEXT[prefix])

        # Use photo_query as supplement
        if photo_query:
            parts.append(photo_query)

        query = " ".join(parts).strip()
        return query if query else "professional business modern"

    # ─── resolve_media with improvements ───

    async def resolve_media(self, project, unsplash) -> None:
        """Fetch real photos from Unsplash for sections with photo_query
        AND for sections whose slots contain text descriptions instead of URLs.
        Also resolves icons and infographics."""
        vc = project.visual_concept_json or {}
        vc_sections_list = vc.get("sections", [])
        vc_sections = {s["block_code"]: s for s in vc_sections_list}
        brief = project.brief_json or {}
        style = project.style_json or {}
        brand_color = style.get("primary_color", style.get("color_primary", "#4F46E5"))

        IMAGE_SLOTS = ("hero_image", "image_url", "image", "photo")

        for section in project.sections:
            vc_s = vc_sections.get(section.block_code, {})
            photo_query = vc_s.get("photo_query")
            media_type = vc_s.get("media_type", "none")
            bg_type = vc_s.get("bg_type", "white")
            slots = dict(section.slots_json or {})
            changed = False

            # ─── NEW: Resolve icons in slots before anything else ───
            slots = self.resolve_icons_in_slots(slots, brand_color)
            if slots != (section.slots_json or {}):
                changed = True

            # ─── Pass 1: VC-driven photo resolution ───
            existing_url = any(
                self._is_url(self._extract_text(slots.get(k)))
                for k in IMAGE_SLOTS
            )

            # IMPROVED: build smarter query
            smart_query = self._build_smart_query(
                photo_query, slots, section.block_code,
                brief.get("description", ""),
            )

            if smart_query and media_type in ("photo_wide", "photo_split", "avatars") and not existing_url:
                result = await self._resolve_photo(unsplash, smart_query, media_type, trigger_dl=True)
                if result:
                    photo_url, credit = result
                    inserted = False
                    for slot_key in IMAGE_SLOTS:
                        if slot_key in slots:
                            slots[slot_key] = photo_url
                            slots["image_credit"] = credit
                            inserted = True
                            break
                    if not inserted:
                        slots["image"] = photo_url
                        slots["image_credit"] = credit
                    changed = True

                    if bg_type == "dark_photo_overlay":
                        vc_s["resolved_photo_url"] = photo_url

            # ─── Pass 2: Slot-driven resolution ───
            for slot_key in IMAGE_SLOTS:
                val = self._extract_text(slots.get(slot_key))
                if val and not self._is_url(val) and len(val) > 3:
                    result = await self._resolve_photo(unsplash, val, "photo_wide")
                    if result:
                        photo_url, credit = result
                        slots[slot_key] = photo_url
                        slots["image_credit"] = credit
                        changed = True

            # ─── Pass 3: Nested array images ───
            _FALLBACK_QUERIES = {
                "features": "business technology professional",
                "tiers": "product service pricing",
                "testimonials": "professional person portrait",
            }

            for list_key in ("features", "tiers", "testimonials"):
                items = slots.get(list_key)
                if not isinstance(items, list):
                    continue

                needs_image: list[tuple[int, dict, str | None]] = []
                for idx, item in enumerate(items):
                    if not isinstance(item, dict):
                        continue
                    has_url_img = any(
                        self._is_url(self._extract_text(item.get(k)))
                        for k in ("img", "image", "photo", "avatar")
                    )
                    if has_url_img:
                        continue
                    text_desc_key = None
                    for img_key in ("img", "image", "photo", "avatar"):
                        val = self._extract_text(item.get(img_key))
                        if val and not self._is_url(val) and len(val) > 3:
                            text_desc_key = img_key
                            break
                    needs_image.append((idx, item, text_desc_key))

                if not needs_image:
                    continue

                # IMPROVED: smarter batch query using heading
                batch_query = _FALLBACK_QUERIES.get(list_key, "business professional")
                heading = self._extract_text(slots.get("heading") or slots.get("title"))
                if heading and len(heading) > 3:
                    batch_query = f"{heading} {batch_query}"

                batch_results = await unsplash.search_photos_batch(
                    batch_query,
                    count=len(needs_image),
                    orientation="squarish" if list_key == "testimonials" else "landscape",
                    width=200 if list_key == "testimonials" else 800,
                )

                for i, (idx, item, text_desc_key) in enumerate(needs_image):
                    photo = batch_results[i] if i < len(batch_results) else None

                    if not photo and not unsplash._rate_limited:
                        title = self._extract_text(item.get("title") or item.get("name"))
                        if text_desc_key:
                            title = self._extract_text(item.get(text_desc_key))
                        if title and len(title) > 2:
                            result = await self._resolve_photo(unsplash, title, "photo_wide")
                            if result:
                                photo_url, credit = result
                                target_key = text_desc_key or ("avatar" if list_key == "testimonials" else "img")
                                item[target_key] = photo_url
                                changed = True
                                continue

                    if photo:
                        photo_url = photo["url"]
                        target_key = text_desc_key or ("avatar" if list_key == "testimonials" else "img")
                        item[target_key] = photo_url
                        changed = True

            # ─── Pass 4: Top-level image from heading ───
            has_top_img = any(
                self._is_url(self._extract_text(slots.get(k)))
                for k in IMAGE_SLOTS
            )
            if not has_top_img and section.block_code not in ("NA1", "NA2", "NA3", "FO1", "LO1"):
                heading = self._extract_text(slots.get("heading"))
                if heading and len(heading) > 3:
                    result = await self._resolve_photo(unsplash, heading, "photo_wide")
                    if result:
                        photo_url, credit = result
                        slots["image"] = photo_url
                        slots["image_credit"] = credit
                        changed = True

            if changed:
                section.slots_json = slots

        if vc_sections_list:
            project.visual_concept_json = vc

    async def render_project_html(
        self,
        db: AsyncSession,
        project,
        fixes: Optional[list] = None,
    ) -> tuple[str, str]:
        """Render full page from project sections.

        Returns:
            (html_body, css) — ready for <body> and <style>
        """
        visual_concept = project.visual_concept_json or {}
        vc_sections = {
            s["block_code"]: s
            for s in visual_concept.get("sections", [])
        }
        style = project.style_json or {}
        brand_color = style.get("primary_color", style.get("color_primary", "#4F46E5"))
        brand_motif = visual_concept.get("brand_motif", "none")
        motif_usage = visual_concept.get("brand_motif_usage", [])
        motif_opacity = visual_concept.get("brand_motif_opacity", 0.08)
        sorted_sections = sorted(project.sections, key=lambda s: s.position)
        sections_html = []
        prev_section_code = None

        for i, section in enumerate(sorted_sections):
            if not section.is_visible:
                continue

            result = await db.execute(
                select(BlockTemplate).where(BlockTemplate.code == section.block_code)
            )
            block = result.scalar_one_or_none()
            if not block:
                continue

            vc_section = vc_sections.get(section.block_code, {})

            # Render block with data
            html = self.block_renderer.render_block(
                block.html_template,
                section.slots_json or {},
            )

            # ─── Post-process icons in rendered HTML ───
            html = self.resolve_icons_in_html(html, brand_color)

            # ─── Apply photo shape to images ───
            photo_shape = vc_section.get("photo_shape")
            if photo_shape:
                html = self._apply_photo_shape(html, photo_shape)

            # ─── Append infographic if applicable ───
            infographic_html = self.resolve_infographic(section, vc_section)
            if infographic_html:
                html += f'\n<div class="infographic-container" style="margin-top:1.5rem;">{infographic_html}</div>'

            # ─── Apply photo layout for multi-image sections ───
            photo_layout = vc_section.get("photo_layout")
            if photo_layout and photo_layout != "single":
                slots = section.slots_json or {}
                image_urls = []
                for key in ("image", "image_url", "hero_image", "photo"):
                    val = self._extract_text(slots.get(key))
                    if val and self._is_url(val):
                        image_urls.append(val)
                photo_queries = vc_section.get("photo_queries", [])
                for pq_url in photo_queries:
                    if isinstance(pq_url, str) and self._is_url(pq_url):
                        image_urls.append(pq_url)
                if len(image_urls) >= 2:
                    layout_html = self._apply_photo_layout(
                        image_urls, photo_layout, photo_shape or "rounded_sm"
                    )
                    if layout_html:
                        html += f'\n<div class="photo-layout" style="margin-top:1.5rem;">{layout_html}</div>'

            # ─── Brand motif: separator between sections ───
            if prev_section_code and "separator" in motif_usage:
                sep_html = self._apply_brand_motif(brand_motif, "separator", brand_color, motif_opacity)
                if sep_html:
                    sections_html.append(sep_html)

            # ─── Apply bg decoration ───
            bg_decoration = vc_section.get("bg_decoration")
            section_uid = str(section.id) if hasattr(section, "id") else f"s{i}"
            html = self._apply_bg_decoration(html, bg_decoration or "none", brand_color, section_uid)

            # ─── Brand motif: hero_bg or cta_overlay ───
            prefix = section.block_code[:2] if section.block_code else ""
            motif_extra = ""
            if prefix == "HE" and "hero_bg" in motif_usage:
                motif_extra = self._apply_brand_motif(brand_motif, "hero_bg", brand_color, motif_opacity)
            elif prefix == "CT" and "cta_overlay" in motif_usage:
                motif_extra = self._apply_brand_motif(brand_motif, "cta_overlay", brand_color, motif_opacity)
            if motif_extra:
                html = motif_extra + html

            # Apply visual concept styling
            section_style = _build_section_style(vc_section) if vc_section else ""

            style_attr = f' style="{section_style}padding:3rem 0;position:relative;overflow:hidden;"' if section_style else ' style="padding:3rem 0;position:relative;overflow:hidden;"'
            sections_html.append(
                f'<div data-section-id="{section.id}" '
                f'data-block-code="{section.block_code}" '
                f'data-position="{section.position}"{style_attr}>\n'
                f'  <div style="max-width:1200px;margin:0 auto;padding:0 1.5rem;position:relative;z-index:1;">\n{html}\n  </div>\n</div>'
            )
            prev_section_code = section.block_code

        html_body = "\n".join(sections_html)

        css = self._generate_css(project.style_json or {}, visual_concept)

        if fixes:
            css = self._apply_fixes(css, fixes)

        return html_body, css

    def _generate_css(self, style: dict, visual_concept: dict = None) -> str:
        """Generate CSS from design tokens + project style overrides."""
        primary = style.get("primary_color", style.get("color_primary", "#4F46E5"))
        secondary = style.get("secondary_color", style.get("color_secondary", "#F59E0B"))
        heading_font = style.get("heading_font", "Inter")
        body_font = style.get("body_font", "Inter")

        tokens_path = Path(__file__).parent / "design_tokens.css"
        base_css = tokens_path.read_text(encoding="utf-8") if tokens_path.exists() else ""

        fonts_css = (
            f"@import url('https://fonts.googleapis.com/css2?"
            f"family={heading_font.replace(' ', '+')}:wght@400;500;600;700;800"
            f"&family={body_font.replace(' ', '+')}:wght@300;400;500;600&display=swap');\n\n"
        )

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

        reset = (
            "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n"
            "body { font-family: var(--font-family); color: var(--color-text); line-height: var(--line-height); }\n"
            "h1, h2, h3, h4 { font-family: var(--font-family-heading); line-height: var(--line-height-heading); }\n"
            "img { max-width: 100%; height: auto; border-radius: var(--radius-image); }\n"
            "a { color: var(--color-primary); text-decoration: none; }\n"
            "a:hover { text-decoration: underline; }\n\n"
            "svg { vertical-align: middle; }\n\n"
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
