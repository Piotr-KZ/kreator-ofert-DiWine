"""
Photo layout presets for Lab Creator.
5 presets — creative arrangements of multiple images within a section.
AI selects in Visual Concept per section. User changes via LayoutPicker in toolbar.

When layout != 'single', AI generates multiple photo_queries (photo_queries: list).
Renderer calls get_photo_layout_html(layout_id, image_urls, shape_css) → HTML.
"""

PHOTO_LAYOUTS: dict[str, dict] = {
    "single": {
        "label": "Jedno zdjęcie",
        "description": "Standardowe — jedno zdjęcie na pełną szerokość lub split",
        "image_count": 1,
    },
    "duo_overlap": {
        "label": "Dwa nachodzące",
        "description": "Dwa zdjęcia lekko nachodzące pod kątem — O firmie, hero",
        "image_count": 2,
    },
    "trio_mosaic": {
        "label": "Mozaika 3",
        "description": "Duże + 2 małe obok siebie — portfolio, realizacje",
        "image_count": 3,
    },
    "scattered": {
        "label": "Rozrzucone",
        "description": "3-4 zdjęcia pod losowymi kątami — kreatywne, eventy",
        "image_count": 4,
    },
    "grid_2x2": {
        "label": "Siatka 2×2",
        "description": "4 równe zdjęcia — zespół, portfolio",
        "image_count": 4,
    },
}


def _img_tag(url: str, shape_css: str, extra_style: str = "") -> str:
    """Generate <img> tag with shape and extra inline styles."""
    return (
        f'<img src="{url}" alt="" loading="lazy" '
        f'style="{shape_css}width:100%;height:100%;object-fit:cover;{extra_style}"/>'
    )


def get_photo_layout_html(
    layout_id: str,
    image_urls: list[str],
    shape_css: str = "border-radius:8px;",
) -> str:
    """Generate HTML for a photo layout with given images.

    Args:
        layout_id: preset ID from PHOTO_LAYOUTS
        image_urls: list of image URLs (count should match layout's image_count)
        shape_css: CSS from photo_shapes.get_photo_shape_css()

    Returns:
        HTML string with arranged images, or single <img> if layout unknown
    """
    if not image_urls:
        return ""

    # Pad with duplicates if not enough images
    layout = PHOTO_LAYOUTS.get(layout_id, PHOTO_LAYOUTS["single"])
    needed = layout["image_count"]
    while len(image_urls) < needed:
        image_urls.append(image_urls[-1])

    if layout_id == "single" or layout_id not in PHOTO_LAYOUTS:
        return _img_tag(image_urls[0], shape_css)

    if layout_id == "duo_overlap":
        return (
            f'<div style="position:relative;height:280px;padding:10px;">'
            f'<div style="position:absolute;left:0;top:10px;width:58%;height:90%;'
            f'transform:rotate(-3deg);z-index:2;overflow:hidden;{shape_css}'
            f'box-shadow:0 4px 16px rgba(0,0,0,0.1);">'
            f'{_img_tag(image_urls[0], "")}'
            f'</div>'
            f'<div style="position:absolute;right:0;top:0;width:52%;height:85%;'
            f'transform:rotate(2deg);z-index:1;overflow:hidden;{shape_css}'
            f'box-shadow:0 4px 12px rgba(0,0,0,0.08);">'
            f'{_img_tag(image_urls[1], "")}'
            f'</div>'
            f'</div>'
        )

    if layout_id == "trio_mosaic":
        return (
            f'<div style="display:grid;grid-template-columns:2fr 1fr;'
            f'grid-template-rows:1fr 1fr;gap:8px;height:300px;">'
            f'<div style="grid-row:1/3;overflow:hidden;{shape_css}">'
            f'{_img_tag(image_urls[0], "")}'
            f'</div>'
            f'<div style="overflow:hidden;{shape_css}">'
            f'{_img_tag(image_urls[1], "")}'
            f'</div>'
            f'<div style="overflow:hidden;{shape_css}">'
            f'{_img_tag(image_urls[2], "")}'
            f'</div>'
            f'</div>'
        )

    if layout_id == "scattered":
        positions = [
            ("left:5%;top:8%;width:48%;", "rotate(-4deg)", "2"),
            ("right:5%;top:3%;width:38%;", "rotate(3deg)", "1"),
            ("left:22%;bottom:3%;width:42%;", "rotate(-1.5deg)", "3"),
            ("right:10%;bottom:8%;width:35%;", "rotate(2.5deg)", "1"),
        ]
        items = []
        for i, (pos, rot, z) in enumerate(positions):
            if i >= len(image_urls):
                break
            items.append(
                f'<div style="position:absolute;{pos}aspect-ratio:4/3;'
                f'transform:{rot};z-index:{z};overflow:hidden;{shape_css}'
                f'box-shadow:0 4px 14px rgba(0,0,0,0.1);">'
                f'{_img_tag(image_urls[i], "")}'
                f'</div>'
            )
        return (
            f'<div style="position:relative;height:320px;">'
            f'{"".join(items)}'
            f'</div>'
        )

    if layout_id == "grid_2x2":
        items = []
        for i in range(min(4, len(image_urls))):
            items.append(
                f'<div style="overflow:hidden;{shape_css}aspect-ratio:1;">'
                f'{_img_tag(image_urls[i], "")}'
                f'</div>'
            )
        return (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">'
            f'{"".join(items)}'
            f'</div>'
        )

    return _img_tag(image_urls[0], shape_css)


def get_available_layouts() -> list[dict]:
    """Return all layout presets with id included."""
    return [{"id": k, **v} for k, v in PHOTO_LAYOUTS.items()]
