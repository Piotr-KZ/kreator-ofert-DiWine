"""
Image processing service — crop, resize, convert to WebP.
Brief 33: 8 aspect ratios for block image slots.
"""

import io
from typing import Optional

from PIL import Image

IMAGE_FORMATS = {
    "16:9": {"width": 1920, "height": 1080, "use": "Hero fullscreen, bannery"},
    "16:7": {"width": 1920, "height": 840, "use": "Hero 3/4"},
    "4:3": {"width": 800, "height": 600, "use": "Split 50%, karty szerokie"},
    "3:4": {"width": 600, "height": 800, "use": "Portrait, zespol"},
    "1:1": {"width": 400, "height": 400, "use": "Karty kwadratowe, avatary"},
    "3:2": {"width": 600, "height": 400, "use": "Galeria, realizacje"},
    "2:3": {"width": 400, "height": 600, "use": "Portfolio portrait"},
    "auto": {"width": None, "height": None, "use": "Oryginalne proporcje"},
}


def process_image(
    file_bytes: bytes,
    target_ratio: str,
    max_width: int = 1920,
    quality: int = 85,
) -> bytes:
    """Crop and resize image to target aspect ratio, output as WebP.

    Args:
        file_bytes: raw image bytes
        target_ratio: key from IMAGE_FORMATS (e.g. "16:9", "1:1", "auto")
        max_width: maximum output width in px
        quality: WebP quality (1-100)

    Returns:
        WebP image bytes
    """
    img = Image.open(io.BytesIO(file_bytes))

    # Convert RGBA/palette to RGB for WebP
    if img.mode in ("RGBA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    fmt = IMAGE_FORMATS.get(target_ratio)
    if not fmt or not fmt["width"]:
        # auto — only resize to max_width
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize(
                (max_width, int(img.height * ratio)), Image.LANCZOS
            )
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=quality)
        return buf.getvalue()

    # Crop to target ratio
    target_w, target_h = fmt["width"], fmt["height"]
    target_aspect = target_w / target_h
    img_aspect = img.width / img.height

    if img_aspect > target_aspect:
        # Too wide — crop sides
        new_w = int(img.height * target_aspect)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        # Too tall — crop top/bottom
        new_h = int(img.width / target_aspect)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))

    # Resize to target resolution
    final_w = min(img.width, target_w, max_width)
    final_h = int(final_w / target_aspect)
    if img.width > final_w:
        img = img.resize((final_w, final_h), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality)
    return buf.getvalue()
