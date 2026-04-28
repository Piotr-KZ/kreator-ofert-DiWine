"""
Background decoration presets for Lab Creator.
6 presets — each generates SVG/HTML to inject into a section background.
Uses position:absolute + pointer-events:none so they don't interfere with content.
"""

import hashlib


def _uid(section_id: str, decoration_id: str) -> str:
    """Generate short unique ID for SVG pattern IDs (avoids collisions)."""
    raw = f"{section_id}-{decoration_id}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]


def _alpha(hex_color: str, opacity: float) -> str:
    """Convert #RRGGBB to rgba(r,g,b,opacity)."""
    c = hex_color.lstrip("#")
    if len(c) != 6:
        return f"rgba(79,70,229,{opacity})"
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


BG_DECORATIONS: dict[str, dict] = {
    "none": {
        "label": "Brak",
        "description": "Czyste tło bez dekoracji",
    },
    "dot_grid": {
        "label": "Siatka kropek",
        "description": "Regularne małe kropki — tech, profesjonalne",
    },
    "circles": {
        "label": "Kółka dekoracyjne",
        "description": "2-3 duże kółka w rogach — hero, CTA",
    },
    "blob": {
        "label": "Organiczny blob",
        "description": "1-2 miękkie kształty — kreatywne, wellness",
    },
    "diagonal_lines": {
        "label": "Ukośne linie",
        "description": "Cienkie linie 45° — premium, minimalistyczne",
    },
    "brand_shape": {
        "label": "Motyw marki",
        "description": "Powtórzenie motywu marki w tle sekcji",
    },
}


def generate_decoration_html(
    decoration_id: str,
    color: str = "#4F46E5",
    section_id: str = "s0",
) -> str:
    """Generate HTML/SVG decoration overlay for a section.

    Args:
        decoration_id: preset ID from BG_DECORATIONS
        color: brand color (hex)
        section_id: for unique SVG pattern IDs

    Returns:
        HTML string to inject inside section div (position:absolute)
        or empty string for 'none'
    """
    if decoration_id == "none" or decoration_id not in BG_DECORATIONS:
        return ""

    uid = _uid(section_id, decoration_id)
    wrap = 'style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:hidden;"'

    if decoration_id == "dot_grid":
        return (
            f'<div {wrap}>'
            f'<svg style="width:100%;height:100%;opacity:0.06;" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><pattern id="dots-{uid}" width="20" height="20" patternUnits="userSpaceOnUse">'
            f'<circle cx="2" cy="2" r="1" fill="{color}"/>'
            f'</pattern></defs>'
            f'<rect width="100%" height="100%" fill="url(#dots-{uid})"/>'
            f'</svg></div>'
        )

    if decoration_id == "circles":
        c1 = _alpha(color, 0.06)
        c2 = _alpha(color, 0.04)
        return (
            f'<div {wrap}>'
            f'<svg style="width:100%;height:100%;" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" viewBox="0 0 800 400">'
            f'<circle cx="680" cy="60" r="120" fill="{c1}"/>'
            f'<circle cx="680" cy="60" r="80" fill="none" stroke="{c2}" stroke-width="1"/>'
            f'<circle cx="80" cy="320" r="80" fill="{c2}"/>'
            f'</svg></div>'
        )

    if decoration_id == "blob":
        c1 = _alpha(color, 0.05)
        c2 = _alpha(color, 0.04)
        return (
            f'<div {wrap}>'
            f'<svg style="width:100%;height:100%;" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" viewBox="0 0 800 400">'
            f'<path d="M650,50 Q750,100 700,200 Q650,300 550,250 Q450,200 500,100 Q550,0 650,50Z" fill="{c1}"/>'
            f'<path d="M100,300 Q200,350 180,250 Q160,150 80,200 Q0,250 100,300Z" fill="{c2}"/>'
            f'</svg></div>'
        )

    if decoration_id == "diagonal_lines":
        return (
            f'<div {wrap}>'
            f'<svg style="width:100%;height:100%;opacity:0.04;" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><pattern id="diag-{uid}" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<line x1="0" y1="0" x2="0" y2="16" stroke="{color}" stroke-width="0.5"/>'
            f'</pattern></defs>'
            f'<rect width="100%" height="100%" fill="url(#diag-{uid})"/>'
            f'</svg></div>'
        )

    if decoration_id == "brand_shape":
        # Uses diamond shape as default brand motif
        c_a = _alpha(color, 0.08)
        c_b = _alpha(color, 0.05)
        return (
            f'<div {wrap}>'
            f'<div style="position:absolute;top:-30px;right:-30px;width:180px;height:180px;'
            f'border:2px solid {c_a};transform:rotate(45deg);"></div>'
            f'<div style="position:absolute;top:-5px;right:-5px;width:120px;height:120px;'
            f'border:1.5px solid {c_b};transform:rotate(45deg);"></div>'
            f'<div style="position:absolute;bottom:-20px;left:15%;width:60px;height:60px;'
            f'background:{c_b};transform:rotate(45deg);border-radius:4px;"></div>'
            f'</div>'
        )

    return ""


def get_available_decorations() -> list[dict]:
    """Return all decoration presets with id included."""
    return [{"id": k, **v} for k, v in BG_DECORATIONS.items()]
