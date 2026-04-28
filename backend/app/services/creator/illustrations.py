"""
Section illustrations for Lab Creator.
30 monochrome SVG illustrations (64x64) for page sections.
All use stroke="currentColor" — color comes from CSS (brand color).

AI generates: "illustration": "small-group"
Renderer calls: get_illustration_svg("small-group", color="#4F46E5")

Categories:
  Business (7): target, chart-up, strategy, award, building, briefcase, handshake
  Time/Process (5): clock, refresh, calendar, hourglass, rocket
  People (4): small-group, user-expert, support, presentation
  Communication (4): mail, phone, chat, megaphone
  Security (3): shield, lock, certificate
  Tech (4): browser, network, code, cloud
  Documents (3): checklist, document, clipboard
"""

ILLUSTRATIONS: dict[str, str] = {

    # ─── Business ───

    "target": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="30" r="20"/><circle cx="32" cy="30" r="13"/><circle cx="32" cy="30" r="6" fill="currentColor" opacity=".15"/><circle cx="32" cy="30" r="2.5" fill="currentColor"/><path d="M50 12l4-4M54 8l-2 6-4-2"/><path d="M24 58h16M30 62h4"/></svg>',

    "chart-up": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="10" y="10" width="44" height="44" rx="4"/><path d="M10 46h44" stroke-width="1"/><rect x="18" y="32" width="7" height="14" rx="1" fill="currentColor" opacity=".1"/><rect x="29" y="24" width="7" height="22" rx="1" fill="currentColor" opacity=".15"/><rect x="40" y="18" width="7" height="28" rx="1" fill="currentColor" opacity=".2"/><path d="M18 30l12-10 8 6 12-10" stroke-width="2"/><path d="M46 14l4 2-2 4"/></svg>',

    "strategy": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M32 6L58 20v24L32 58 6 44V20z"/><path d="M32 6v52M6 20l26 14 26-14"/><circle cx="32" cy="34" r="6" fill="currentColor" opacity=".15"/><circle cx="32" cy="34" r="2.5" fill="currentColor"/></svg>',

    "award": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="24" r="14" fill="currentColor" opacity=".08"/><circle cx="32" cy="24" r="14"/><path d="M32 10l3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="currentColor" opacity=".12"/><path d="M22 36l-4 20 14-6 14 6-4-20"/></svg>',

    "building": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 54V18l16-10 16 10v36"/><path d="M16 54h32"/><rect x="24" y="24" width="6" height="6" rx="1" fill="currentColor" opacity=".15"/><rect x="34" y="24" width="6" height="6" rx="1" fill="currentColor" opacity=".15"/><rect x="24" y="34" width="6" height="6" rx="1" fill="currentColor" opacity=".15"/><rect x="34" y="34" width="6" height="6" rx="1" fill="currentColor" opacity=".15"/><rect x="28" y="44" width="8" height="10" rx="1"/></svg>',

    "briefcase": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="22" width="48" height="32" rx="4"/><path d="M24 22v-6a4 4 0 014-4h8a4 4 0 014 4v6"/><path d="M8 34h48"/><circle cx="32" cy="34" r="3" fill="currentColor"/></svg>',

    "handshake": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 26h10l8 4 12-4h10"/><path d="M48 26v16l-14 8-12-4-14 0"/><path d="M8 26v16h6"/><path d="M26 34l8-4"/><path d="M30 42l6-4"/><circle cx="8" cy="24" r="3" fill="currentColor" opacity=".2"/><circle cx="48" cy="24" r="3" fill="currentColor" opacity=".2"/></svg>',

    # ─── Time / Process ───

    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="32" r="22"/><path d="M32 14v18l12 7" stroke-width="2.5"/><circle cx="32" cy="32" r="3" fill="currentColor"/><path d="M32 8v2M32 54v2M8 32h2M54 32h2" stroke-width="1.5"/></svg>',

    "refresh": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 32a22 22 0 0138-15"/><path d="M48 12v10h-10"/><path d="M54 32a22 22 0 01-38 15"/><path d="M16 52V42h10"/><circle cx="32" cy="32" r="6" fill="currentColor" opacity=".15"/></svg>',

    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="10" y="14" width="44" height="40" rx="4"/><path d="M10 26h44"/><path d="M22 8v10M42 8v10"/><circle cx="22" cy="34" r="2" fill="currentColor" opacity=".3"/><circle cx="32" cy="34" r="2" fill="currentColor" opacity=".3"/><circle cx="42" cy="34" r="2" fill="currentColor"/><circle cx="22" cy="44" r="2" fill="currentColor" opacity=".3"/><circle cx="32" cy="44" r="2" fill="currentColor" opacity=".3"/></svg>',

    "hourglass": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 8h24M20 56h24"/><path d="M20 8c0 12 12 18 12 24s-12 12-12 24"/><path d="M44 8c0 12-12 18-12 24s12 12 12 24"/><path d="M24 48c2-2 5-3 8-3s6 1 8 3" fill="currentColor" opacity=".12"/><path d="M30 30h4" stroke-width="1.5"/></svg>',

    "rocket": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M32 8c-6 10-8 20-6 30h12c2-10 0-20-6-30z"/><circle cx="32" cy="26" r="4" fill="currentColor" opacity=".15"/><path d="M26 38l-8 6 2-12"/><path d="M38 38l8 6-2-12"/><path d="M28 50h8"/><path d="M30 50v6M34 50v6" stroke-width="2"/></svg>',

    # ─── People ───

    "small-group": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="20" cy="16" r="6"/><circle cx="44" cy="16" r="6"/><circle cx="32" cy="14" r="7" fill="currentColor" opacity=".1"/><circle cx="32" cy="14" r="7"/><path d="M10 40c0-7 4-12 10-12"/><path d="M44 28c6 0 10 5 10 12"/><path d="M20 28c6 0 12 5 12 12s6 12 12 12" stroke-width="0"/><path d="M18 40c0-8 6-14 14-14s14 6 14 14"/><path d="M8 54h48" stroke-width="1"/></svg>',

    "user-expert": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="18" r="10"/><path d="M16 52c0-10 7-18 16-18s16 8 16 18"/><path d="M32 8l2 4 4 0-3 3 1 4-4-2-4 2 1-4-3-3 4 0z" fill="currentColor" opacity=".15"/><path d="M12 54h40" stroke-width="1"/></svg>',

    "support": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="20" r="8"/><path d="M22 48c0-6 4-12 10-12s10 6 10 12"/><path d="M14 32a4 4 0 01-4-4v-4a4 4 0 018 0v4a4 4 0 01-4 0"/><path d="M50 32a4 4 0 01-4-4v-4a4 4 0 018 0v4a4 4 0 01-4 0"/><path d="M14 24c0-10 8-16 18-16s18 6 18 16"/><path d="M18 54h28" stroke-width="1"/></svg>',

    "presentation": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="8" width="48" height="34" rx="3"/><path d="M8 16h48" stroke-width="1"/><path d="M32 42v8M24 54h16"/><path d="M18 26h12M18 32h8" stroke-width="2"/><rect x="38" y="22" width="12" height="14" rx="2" fill="currentColor" opacity=".1"/></svg>',

    # ─── Communication ───

    "mail": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="14" width="48" height="36" rx="4"/><path d="M8 20l24 14 24-14"/><path d="M8 14l24 16 24-16"/></svg>',

    "phone": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 8h20v48H22z" rx="4"/><path d="M22 14h20M22 48h20"/><circle cx="32" cy="52" r="2" fill="currentColor"/><path d="M28 10h8" stroke-width="1.5"/><path d="M28 40l4-4 4 4 4-4" stroke-width="1.5"/></svg>',

    "chat": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14h32a4 4 0 014 4v16a4 4 0 01-4 4H24l-10 8v-8h-4a4 4 0 01-4-4V18a4 4 0 014-4z"/><path d="M18 24h20M18 30h12"/><circle cx="48" cy="24" r="3" fill="currentColor" opacity=".2"/><circle cx="48" cy="32" r="3" fill="currentColor" opacity=".2"/><circle cx="48" cy="40" r="3" fill="currentColor" opacity=".2"/></svg>',

    "megaphone": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M44 12L18 24v16l26 12z" fill="currentColor" opacity=".06"/><path d="M44 12L18 24v16l26 12z"/><rect x="10" y="24" width="8" height="16" rx="2"/><path d="M14 40v12h6l2-12"/><path d="M50 26h6M50 32h8M50 38h6" stroke-width="2"/></svg>',

    # ─── Security ───

    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M32 6L12 16v16c0 14 10 22 20 26 10-4 20-12 20-26V16z" fill="currentColor" opacity=".06"/><path d="M32 6L12 16v16c0 14 10 22 20 26 10-4 20-12 20-26V16z"/><path d="M24 32l6 6 12-14" stroke-width="2.5"/></svg>',

    "lock": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="14" y="28" width="36" height="26" rx="4"/><path d="M22 28V20a10 10 0 0120 0v8"/><circle cx="32" cy="40" r="4" fill="currentColor" opacity=".15"/><path d="M32 44v4" stroke-width="2.5"/></svg>',

    "certificate": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="10" y="8" width="44" height="48" rx="3"/><path d="M10 18h44" stroke-width="1"/><circle cx="32" cy="32" r="8" fill="currentColor" opacity=".08"/><circle cx="32" cy="32" r="8"/><path d="M29 32l3 3 5-6" stroke-width="2"/><path d="M22 48h20M28 52h8"/></svg>',

    # ─── Tech ───

    "browser": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="10" width="52" height="44" rx="4"/><path d="M6 22h52"/><circle cx="14" cy="16" r="2" fill="currentColor" opacity=".3"/><circle cx="22" cy="16" r="2" fill="currentColor" opacity=".3"/><circle cx="30" cy="16" r="2" fill="currentColor" opacity=".3"/><path d="M16 30h16M16 36h24M16 42h12"/></svg>',

    "network": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="32" cy="14" r="6" fill="currentColor" opacity=".1"/><circle cx="32" cy="14" r="6"/><circle cx="14" cy="44" r="6" fill="currentColor" opacity=".1"/><circle cx="14" cy="44" r="6"/><circle cx="50" cy="44" r="6" fill="currentColor" opacity=".1"/><circle cx="50" cy="44" r="6"/><path d="M28 19l-10 20M36 19l10 20M18 44h28"/></svg>',

    "code": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="10" width="48" height="44" rx="4"/><path d="M8 20h48" stroke-width="1"/><path d="M22 32l-6 6 6 6" stroke-width="2"/><path d="M42 32l6 6-6 6" stroke-width="2"/><path d="M30 44l4-20" stroke-width="1.5"/></svg>',

    "cloud": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 44h30a10 10 0 000-20 14 14 0 00-28 4 8 8 0 00-2 16z" fill="currentColor" opacity=".06"/><path d="M18 44h30a10 10 0 000-20 14 14 0 00-28 4 8 8 0 00-2 16z"/><path d="M28 50v6M36 50v6M44 50v6" stroke-width="1.5" stroke-dasharray="2 2"/></svg>',

    # ─── Documents ───

    "checklist": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="6" width="40" height="52" rx="3"/><path d="M24 6v-0h16v0" /><path d="M12 16h40" stroke-width="1"/><path d="M20 26l3 3 6-7" stroke-width="2"/><path d="M34 28h14"/><path d="M20 38l3 3 6-7" stroke-width="2"/><path d="M34 40h14"/><path d="M20 50l3 3 6-7" stroke-width="2"/><path d="M34 52h10"/></svg>',

    "document": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8h22l12 12v36a3 3 0 01-3 3H16a3 3 0 01-3-3V11a3 3 0 013-3z"/><path d="M38 8v12h12"/><path d="M22 28h20M22 36h20M22 44h14"/></svg>',

    "clipboard": '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="14" y="12" width="36" height="44" rx="3"/><path d="M24 12V8h16v4" /><rect x="24" y="6" width="16" height="8" rx="2"/><path d="M22 28h20M22 36h20M22 44h14"/><circle cx="22" cy="28" r="0" /><circle cx="22" cy="36" r="0" /><circle cx="22" cy="44" r="0" /></svg>',

}

_ILLUST_LOOKUP = {k.lower().replace("-", "_").replace(" ", "_"): k for k in ILLUSTRATIONS}


def get_illustration_svg(name: str, size: int = 64, color: str | None = None) -> str:
    """Return illustration SVG by name with configurable size and color.

    Args:
        name: illustration key (case-insensitive, hyphens or underscores)
        size: pixel size (default 64)
        color: CSS color string or None for currentColor (inherits from parent)

    Returns:
        SVG string or empty string if not found
    """
    lookup_key = name.lower().replace("-", "_").replace(" ", "_")
    canonical = _ILLUST_LOOKUP.get(lookup_key)
    if not canonical:
        return ""

    svg = ILLUSTRATIONS[canonical]
    if size != 64:
        svg = svg.replace('width="64"', f'width="{size}"')
        svg = svg.replace('height="64"', f'height="{size}"')
    if color:
        svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
        svg = svg.replace('fill="currentColor"', f'fill="{color}"')
    return svg


def get_available_illustrations() -> list[str]:
    """Get list of available illustration names."""
    return list(ILLUSTRATIONS.keys())
