"""
Brand motif presets for Lab Creator.
7 presets (including 'none') — one geometric shape used consistently across the page.
Each motif has 4 placements: hero_bg, card_accent, separator, cta_overlay.

AI picks motif in Visual Concept (global). User changes in TweakPanel.
Renderer calls get_motif_html(motif_id, placement, color) per section.
"""


def _alpha(hex_color: str, opacity: float) -> str:
    c = hex_color.lstrip("#")
    if len(c) != 6:
        return f"rgba(79,70,229,{opacity})"
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


BRAND_MOTIFS: dict[str, dict] = {
    "none": {"label": "Brak", "description": "Bez motywu marki"},
    "diamond": {"label": "Romb", "description": "Premium, elegancja, finanse"},
    "circle_ring": {"label": "Okrąg", "description": "Technika, innowacja, IT"},
    "triangle": {"label": "Trójkąt", "description": "Dynamika, sport, wzrost"},
    "hexagon": {"label": "Sześciokąt", "description": "Tech, nauka, systematyczność"},
    "slash": {"label": "Ukośnik", "description": "Nowoczesność, minimalizm"},
    "dot_cluster": {"label": "Klaster kropek", "description": "Kreatywność, edukacja"},
}

PLACEMENTS = ("hero_bg", "card_accent", "separator", "cta_overlay")


def _diamond(placement: str, ca: str, cb: str, cw: str) -> str:
    if placement == "hero_bg":
        return (
            f'<div style="position:absolute;top:-30px;right:-30px;width:200px;height:200px;'
            f'border:2px solid {ca};transform:rotate(45deg);pointer-events:none;"></div>'
            f'<div style="position:absolute;top:-5px;right:-5px;width:140px;height:140px;'
            f'border:1.5px solid {cb};transform:rotate(45deg);pointer-events:none;"></div>'
        )
    if placement == "card_accent":
        return (
            f'<div style="position:absolute;top:-8px;right:-8px;width:28px;height:28px;'
            f'background:{cb};transform:rotate(45deg);border-radius:3px;pointer-events:none;"></div>'
        )
    if placement == "separator":
        return (
            f'<div style="display:flex;align-items:center;gap:12px;justify-content:center;padding:0.75rem 0;">'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div>'
            f'<div style="width:10px;height:10px;background:{ca};transform:rotate(45deg);border-radius:2px;"></div>'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div></div>'
        )
    if placement == "cta_overlay":
        return (
            f'<div style="position:absolute;top:50%;left:50%;width:280px;height:280px;'
            f'border:2px solid {cw};transform:translate(-50%,-50%) rotate(45deg);pointer-events:none;"></div>'
            f'<div style="position:absolute;top:50%;left:50%;width:180px;height:180px;'
            f'border:1.5px solid {cw};transform:translate(-50%,-50%) rotate(45deg);pointer-events:none;"></div>'
        )
    return ""


def _circle_ring(placement: str, ca: str, cb: str, cw: str) -> str:
    if placement == "hero_bg":
        return (
            f'<div style="position:absolute;top:-40px;right:-40px;width:220px;height:220px;'
            f'border:2px solid {ca};border-radius:50%;pointer-events:none;"></div>'
            f'<div style="position:absolute;top:-10px;right:-10px;width:160px;height:160px;'
            f'border:1.5px solid {cb};border-radius:50%;pointer-events:none;"></div>'
        )
    if placement == "card_accent":
        return (
            f'<div style="position:absolute;top:-6px;right:-6px;width:24px;height:24px;'
            f'border:2px solid {cb};border-radius:50%;pointer-events:none;"></div>'
        )
    if placement == "separator":
        return (
            f'<div style="display:flex;align-items:center;gap:12px;justify-content:center;padding:0.75rem 0;">'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div>'
            f'<div style="width:8px;height:8px;border:2px solid {ca};border-radius:50%;"></div>'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div></div>'
        )
    if placement == "cta_overlay":
        return (
            f'<div style="position:absolute;top:50%;left:50%;width:260px;height:260px;'
            f'border:2px solid {cw};border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;"></div>'
        )
    return ""


def _triangle(placement: str, ca: str, cb: str, cw: str) -> str:
    if placement == "hero_bg":
        return (
            f'<svg style="position:absolute;top:-10px;right:-10px;opacity:0.08;pointer-events:none;" '
            f'width="200" height="200" viewBox="0 0 200 200">'
            f'<polygon points="100,10 190,180 10,180" fill="none" stroke="{ca}" stroke-width="2"/>'
            f'<polygon points="100,40 170,160 30,160" fill="none" stroke="{cb}" stroke-width="1.5"/></svg>'
        )
    if placement == "card_accent":
        return (
            f'<svg style="position:absolute;top:-4px;right:-4px;pointer-events:none;" '
            f'width="24" height="24" viewBox="0 0 24 24">'
            f'<polygon points="12,2 22,20 2,20" fill="{cb}"/></svg>'
        )
    if placement == "separator":
        return (
            f'<div style="display:flex;align-items:center;gap:12px;justify-content:center;padding:0.75rem 0;">'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div>'
            f'<svg width="12" height="12" viewBox="0 0 24 24"><polygon points="12,2 22,20 2,20" fill="{ca}"/></svg>'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div></div>'
        )
    if placement == "cta_overlay":
        return (
            f'<svg style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.06;pointer-events:none;" '
            f'width="300" height="300" viewBox="0 0 300 300">'
            f'<polygon points="150,20 280,260 20,260" fill="none" stroke="{cw}" stroke-width="2"/></svg>'
        )
    return ""


def _hexagon(placement: str, ca: str, cb: str, cw: str) -> str:
    hex_points = "25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%"
    if placement == "hero_bg":
        return (
            f'<div style="position:absolute;top:-20px;right:-20px;width:180px;height:180px;'
            f'clip-path:polygon({hex_points});border:2px solid {ca};pointer-events:none;"></div>'
            f'<svg style="position:absolute;top:-20px;right:-20px;pointer-events:none;opacity:0.08;" '
            f'width="180" height="180" viewBox="0 0 100 100">'
            f'<polygon points="25,0 75,0 100,50 75,100 25,100 0,50" fill="none" stroke="{ca}" stroke-width="1.5"/>'
            f'<polygon points="35,15 65,15 80,50 65,85 35,85 20,50" fill="none" stroke="{cb}" stroke-width="1"/></svg>'
        )
    if placement == "card_accent":
        return (
            f'<svg style="position:absolute;top:-5px;right:-5px;pointer-events:none;" '
            f'width="24" height="24" viewBox="0 0 100 100">'
            f'<polygon points="25,0 75,0 100,50 75,100 25,100 0,50" fill="{cb}"/></svg>'
        )
    if placement == "separator":
        return (
            f'<div style="display:flex;align-items:center;gap:12px;justify-content:center;padding:0.75rem 0;">'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div>'
            f'<svg width="14" height="14" viewBox="0 0 100 100">'
            f'<polygon points="25,0 75,0 100,50 75,100 25,100 0,50" fill="{ca}"/></svg>'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div></div>'
        )
    if placement == "cta_overlay":
        return (
            f'<svg style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;" '
            f'width="280" height="280" viewBox="0 0 100 100" opacity="0.06">'
            f'<polygon points="25,0 75,0 100,50 75,100 25,100 0,50" fill="none" stroke="{cw}" stroke-width="2"/></svg>'
        )
    return ""


def _slash(placement: str, ca: str, cb: str, cw: str) -> str:
    if placement == "hero_bg":
        return (
            f'<div style="position:absolute;top:10%;right:8%;width:3px;height:60%;'
            f'background:{ca};transform:rotate(15deg);pointer-events:none;"></div>'
            f'<div style="position:absolute;top:15%;right:12%;width:2px;height:50%;'
            f'background:{cb};transform:rotate(15deg);pointer-events:none;"></div>'
        )
    if placement == "card_accent":
        return (
            f'<div style="position:absolute;top:4px;right:8px;width:2px;height:20px;'
            f'background:{cb};transform:rotate(15deg);pointer-events:none;"></div>'
        )
    if placement == "separator":
        return (
            f'<div style="display:flex;align-items:center;gap:8px;justify-content:center;padding:0.75rem 0;">'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div>'
            f'<div style="width:2px;height:16px;background:{ca};transform:rotate(15deg);"></div>'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div></div>'
        )
    if placement == "cta_overlay":
        return (
            f'<div style="position:absolute;top:10%;right:15%;width:3px;height:80%;'
            f'background:{cw};transform:rotate(15deg);pointer-events:none;"></div>'
        )
    return ""


def _dot_cluster(placement: str, ca: str, cb: str, cw: str) -> str:
    if placement == "hero_bg":
        return (
            f'<svg style="position:absolute;top:15px;right:30px;pointer-events:none;opacity:0.12;" '
            f'width="80" height="80" viewBox="0 0 80 80">'
            f'<circle cx="20" cy="20" r="4" fill="{ca}"/>'
            f'<circle cx="45" cy="15" r="3" fill="{ca}"/>'
            f'<circle cx="60" cy="35" r="5" fill="{ca}"/>'
            f'<circle cx="30" cy="50" r="3" fill="{ca}"/>'
            f'<circle cx="55" cy="60" r="4" fill="{ca}"/></svg>'
        )
    if placement == "card_accent":
        return (
            f'<svg style="position:absolute;top:4px;right:4px;pointer-events:none;" '
            f'width="20" height="20" viewBox="0 0 20 20">'
            f'<circle cx="5" cy="5" r="2" fill="{cb}"/>'
            f'<circle cx="14" cy="8" r="1.5" fill="{cb}"/>'
            f'<circle cx="9" cy="15" r="2" fill="{cb}"/></svg>'
        )
    if placement == "separator":
        return (
            f'<div style="display:flex;align-items:center;gap:10px;justify-content:center;padding:0.75rem 0;">'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div>'
            f'<svg width="20" height="8" viewBox="0 0 20 8">'
            f'<circle cx="4" cy="4" r="2.5" fill="{ca}"/>'
            f'<circle cx="10" cy="4" r="2" fill="{ca}"/>'
            f'<circle cx="16" cy="4" r="2.5" fill="{ca}"/></svg>'
            f'<div style="flex:1;max-width:200px;height:1px;background:{ca};"></div></div>'
        )
    if placement == "cta_overlay":
        return (
            f'<svg style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none;opacity:0.08;" '
            f'width="200" height="100" viewBox="0 0 200 100">'
            f'<circle cx="30" cy="30" r="8" fill="{cw}"/>'
            f'<circle cx="80" cy="20" r="6" fill="{cw}"/>'
            f'<circle cx="140" cy="40" r="10" fill="{cw}"/>'
            f'<circle cx="60" cy="70" r="7" fill="{cw}"/>'
            f'<circle cx="160" cy="75" r="5" fill="{cw}"/></svg>'
        )
    return ""


_GENERATORS = {
    "diamond": _diamond,
    "circle_ring": _circle_ring,
    "triangle": _triangle,
    "hexagon": _hexagon,
    "slash": _slash,
    "dot_cluster": _dot_cluster,
}


def get_motif_html(
    motif_id: str,
    placement: str,
    color: str = "#4F46E5",
    motif_opacity: float = 0.08,
) -> str:
    """Generate brand motif HTML for a given placement.

    Args:
        motif_id: preset ID from BRAND_MOTIFS
        placement: one of hero_bg, card_accent, separator, cta_overlay
        color: brand color (hex)
        motif_opacity: base opacity (used for alpha calculations)

    Returns:
        HTML string or empty string
    """
    if motif_id == "none" or motif_id not in _GENERATORS:
        return ""
    if placement not in PLACEMENTS:
        return ""

    ca = _alpha(color, motif_opacity)
    cb = _alpha(color, motif_opacity * 0.6)
    cw = f"rgba(255,255,255,{motif_opacity * 0.8})"

    return _GENERATORS[motif_id](placement, ca, cb, cw)


def get_available_motifs() -> list[dict]:
    """Return all motif presets with id included."""
    return [{"id": k, **v} for k, v in BRAND_MOTIFS.items()]
