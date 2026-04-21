"""
SVG Separators for visual transitions between sections.
CSS variables: --color-top, --color-bottom determine fill colors.
"""

SEPARATORS = {
    "wave": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 80" preserveAspectRatio="none" style="display:block;width:100%;height:60px;">
  <path d="M0,40 C360,80 720,0 1080,40 C1260,60 1380,40 1440,40 L1440,80 L0,80 Z" fill="var(--color-bottom, #f3f4f6)"/>
  <path d="M0,0 L0,40 C360,80 720,0 1080,40 C1260,60 1380,40 1440,40 L1440,0 Z" fill="var(--color-top, #ffffff)"/>
</svg>""",

    "diagonal": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60" preserveAspectRatio="none" style="display:block;width:100%;height:60px;">
  <polygon points="0,0 1440,0 1440,60 0,0" fill="var(--color-top, #ffffff)"/>
  <polygon points="0,0 1440,60 0,60" fill="var(--color-bottom, #f3f4f6)"/>
</svg>""",

    "curve": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 80" preserveAspectRatio="none" style="display:block;width:100%;height:60px;">
  <path d="M0,0 L0,60 Q720,-20 1440,60 L1440,0 Z" fill="var(--color-top, #ffffff)"/>
  <path d="M0,60 Q720,-20 1440,60 L1440,80 L0,80 Z" fill="var(--color-bottom, #f3f4f6)"/>
</svg>""",

    "zigzag": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 40" preserveAspectRatio="none" style="display:block;width:100%;height:40px;">
  <path d="M0,0 L0,20 L80,40 L160,20 L240,40 L320,20 L400,40 L480,20 L560,40 L640,20 L720,40 L800,20 L880,40 L960,20 L1040,40 L1120,20 L1200,40 L1280,20 L1360,40 L1440,20 L1440,0 Z" fill="var(--color-top, #ffffff)"/>
  <path d="M0,20 L80,40 L160,20 L240,40 L320,20 L400,40 L480,20 L560,40 L640,20 L720,40 L800,20 L880,40 L960,20 L1040,40 L1120,20 L1200,40 L1280,20 L1360,40 L1440,20 L1440,40 L0,40 Z" fill="var(--color-bottom, #f3f4f6)"/>
</svg>""",

    "triangle": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60" preserveAspectRatio="none" style="display:block;width:100%;height:60px;">
  <polygon points="0,0 1440,0 720,60" fill="var(--color-top, #ffffff)"/>
  <polygon points="0,0 720,60 0,60" fill="var(--color-bottom, #f3f4f6)"/>
  <polygon points="1440,0 720,60 1440,60" fill="var(--color-bottom, #f3f4f6)"/>
</svg>""",
}


def get_separator_svg(separator_type: str, color_top: str, color_bottom: str) -> str:
    """Get separator SVG with specific colors inlined."""
    svg = SEPARATORS.get(separator_type, "")
    if not svg:
        return ""
    # Replace CSS variables with actual colors
    svg = svg.replace("var(--color-top, #ffffff)", color_top)
    svg = svg.replace("var(--color-bottom, #f3f4f6)", color_bottom)
    return svg
