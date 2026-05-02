"""
Seed — offer block templates. 3 categories, 11 blocks.
NO = Nagłówek Oferty, DW = DiWine Bloki, CTA = Zaproszenie.
Każdy klocek = 1 pełna strona landscape A4 (297×210mm).
page_height: F = Full page (jedyna opcja).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.block_template import BlockCategory, BlockTemplate

OFFER_CATEGORIES = [
    {"code": "NO", "name": "Nagłówek Oferty", "icon": "file-text", "order": 50},
    {"code": "DW", "name": "DiWine Bloki", "icon": "package", "order": 51},
    {"code": "CTA", "name": "Zaproszenie", "icon": "check-circle", "order": 52},
]

# Wspólne sloty
_SLOTS_HEADER = [
    {"id": "offer_number", "type": "text", "label": "Numer oferty"},
    {"id": "date", "type": "text", "label": "Data"},
    {"id": "client_name", "type": "text", "label": "Nazwa klienta"},
    {"id": "client_logo_url", "type": "image", "label": "Logo klienta"},
    {"id": "bg_photo_url", "type": "image", "label": "Zdjęcie w tle"},
    {"id": "occasion_name", "type": "text", "label": "Okazja"},
]

_SLOTS_IMG_TEXT = [
    {"id": "eyebrow", "type": "text", "label": "Nagłówek mały"},
    {"id": "heading", "type": "text", "label": "Tytuł"},
    {"id": "body", "type": "text", "label": "Treść"},
    {"id": "image", "type": "image", "label": "Zdjęcie"},
]

_SLOTS_MULTI = lambda n: [
    *[{"id": f"image_{i+1}", "type": "image", "label": f"Zdjęcie {i+1}"} for i in range(n)],
    *[{"id": f"heading_{i+1}", "type": "text", "label": f"Tytuł {i+1}"} for i in range(n)],
    *[{"id": f"body_{i+1}", "type": "text", "label": f"Tekst {i+1}"} for i in range(n)],
    {"id": "eyebrow", "type": "text", "label": "Nagłówek sekcji"},
]

# ═══ NO1 — Nagłówek standard ═══
_NO1 = {
    "code": "NO1", "category_code": "NO",
    "name": "Nagłówek oferty — standard",
    "description": "Logo, tytuł, dane oferty na tle zdjęcia. Pełna strona landscape.",
    "media_type": "photo", "layout_type": "full-width", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_HEADER,
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;align-items:center;background:linear-gradient(rgba(0,0,0,0.5),rgba(0,0,0,0.5)),url('{{bg_photo_url}}') center/cover no-repeat;">
  <div style="max-width:1100px;margin:0 auto;padding:80px 64px;width:100%;">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
      <div>
        <div style="color:#a78bfa;font-size:14px;font-weight:600;letter-spacing:5px;text-transform:uppercase;margin-bottom:12px;">OFERTA PREZENTOWA</div>
        <h1 style="font-size:56px;font-weight:700;color:#fff;margin:0 0 16px;line-height:1.1;">{{occasion_name}}</h1>
        <div style="color:#cbd5e1;font-size:22px;">dla <strong style="color:#fff;">{{client_name}}</strong></div>
        <div style="display:flex;gap:20px;margin-top:24px;font-size:14px;color:#94a3b8;">
          <span>Nr: {{offer_number}}</span><span>Data: {{date}}</span>
        </div>
      </div>
      {{#if client_logo_url}}<img src="{{client_logo_url}}" alt="" style="height:64px;background:#fff;border-radius:14px;padding:12px;box-shadow:0 4px 20px rgba(0,0,0,0.3);"/>{{/if}}
    </div>
  </div>
</section>""",
}

# ═══ NO2 — Nagłówek pełnoekranowy ═══
_NO2 = {
    "code": "NO2", "category_code": "NO",
    "name": "Nagłówek oferty — pełnoekranowy",
    "description": "Duże zdjęcie, minimalistyczny tekst na dole. Pełna strona landscape.",
    "media_type": "photo", "layout_type": "full-width", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_HEADER,
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;align-items:flex-end;background:linear-gradient(to top,rgba(0,0,0,0.75) 0%,rgba(0,0,0,0.05) 50%),url('{{bg_photo_url}}') center/cover no-repeat;">
  <div style="max-width:1100px;margin:0 auto;padding:0 64px 64px;width:100%;">
    {{#if client_logo_url}}<img src="{{client_logo_url}}" alt="" style="height:48px;background:rgba(255,255,255,0.9);border-radius:10px;padding:8px;margin-bottom:20px;"/>{{/if}}
    <h1 style="font-size:60px;font-weight:700;color:#fff;margin:0 0 10px;line-height:1.1;">Oferta prezentowa</h1>
    <div style="font-size:24px;color:#e2e8f0;">{{occasion_name}} — {{client_name}}</div>
    <div style="font-size:14px;color:#94a3b8;margin-top:16px;">{{offer_number}} • {{date}}</div>
  </div>
</section>""",
}

# ═══ DW1 — Obraz LEWO + Tekst PRAWO ═══
_DW1 = {
    "code": "DW1", "category_code": "DW",
    "name": "Obraz lewo + Tekst prawo",
    "description": "Zdjęcie po lewej (50%), tekst po prawej. Pełna strona.",
    "media_type": "photo", "layout_type": "split", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_IMG_TEXT,
    "html_template": """<section style="width:100%;min-height:100vh;display:grid;grid-template-columns:1fr 1fr;">
  <div style="overflow:hidden;"><img src="{{image}}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>
  <div style="padding:80px 64px;display:flex;flex-direction:column;justify-content:center;gap:20px;">
    {{#if eyebrow}}<div style="font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;">{{eyebrow}}</div>{{/if}}
    <h2 style="font-size:40px;font-weight:700;color:#1e293b;margin:0;line-height:1.2;">{{heading}}</h2>
    <div style="font-size:17px;color:#64748b;line-height:1.8;white-space:pre-line;">{{body}}</div>
  </div>
</section>""",
}

# ═══ DW2 — Tekst LEWO + Obraz PRAWO ═══
_DW2 = {
    "code": "DW2", "category_code": "DW",
    "name": "Tekst lewo + Obraz prawo",
    "description": "Tekst po lewej, zdjęcie po prawej. Pełna strona.",
    "media_type": "photo", "layout_type": "split", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_IMG_TEXT,
    "html_template": """<section style="width:100%;min-height:100vh;display:grid;grid-template-columns:1fr 1fr;">
  <div style="padding:80px 64px;display:flex;flex-direction:column;justify-content:center;gap:20px;">
    {{#if eyebrow}}<div style="font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;">{{eyebrow}}</div>{{/if}}
    <h2 style="font-size:40px;font-weight:700;color:#1e293b;margin:0;line-height:1.2;">{{heading}}</h2>
    <div style="font-size:17px;color:#64748b;line-height:1.8;white-space:pre-line;">{{body}}</div>
  </div>
  <div style="overflow:hidden;"><img src="{{image}}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>
</section>""",
}

# ═══ DW3 — Obraz GÓRA + Tekst DÓŁ ═══
_DW3 = {
    "code": "DW3", "category_code": "DW",
    "name": "Obraz góra + Tekst dół",
    "description": "Zdjęcie na pełną szerokość u góry, tekst na dole. Pełna strona.",
    "media_type": "photo", "layout_type": "stacked", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_IMG_TEXT,
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;flex-direction:column;">
  <div style="flex:0 0 55%;overflow:hidden;"><img src="{{image}}" alt="" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>
  <div style="flex:1;padding:48px 64px;display:flex;flex-direction:column;justify-content:center;gap:16px;max-width:900px;margin:0 auto;width:100%;">
    {{#if eyebrow}}<div style="font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;">{{eyebrow}}</div>{{/if}}
    <h2 style="font-size:40px;font-weight:700;color:#1e293b;margin:0;line-height:1.2;">{{heading}}</h2>
    <div style="font-size:17px;color:#64748b;line-height:1.8;white-space:pre-line;">{{body}}</div>
  </div>
</section>""",
}

# ═══ DW4 — 2 kolumny ═══
_DW4 = {
    "code": "DW4", "category_code": "DW",
    "name": "2 kolumny — obrazy + teksty",
    "description": "2 zdjęcia w rzędzie, 2 teksty pod nimi. Pełna strona.",
    "media_type": "photo", "layout_type": "grid-2", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_MULTI(2),
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;flex-direction:column;padding:48px 64px;">
  {{#if eyebrow}}<div style="text-align:center;font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;margin-bottom:32px;">{{eyebrow}}</div>{{/if}}
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;flex:1;">
    <div style="display:flex;flex-direction:column;gap:20px;">
      <div style="flex:0 0 55%;border-radius:16px;overflow:hidden;"><img src="{{image_1}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div>
      <h3 style="font-size:26px;font-weight:700;color:#1e293b;margin:0;">{{heading_1}}</h3>
      <div style="font-size:15px;color:#64748b;line-height:1.7;">{{body_1}}</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:20px;">
      <div style="flex:0 0 55%;border-radius:16px;overflow:hidden;"><img src="{{image_2}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div>
      <h3 style="font-size:26px;font-weight:700;color:#1e293b;margin:0;">{{heading_2}}</h3>
      <div style="font-size:15px;color:#64748b;line-height:1.7;">{{body_2}}</div>
    </div>
  </div>
</section>""",
}

# ═══ DW5 — 3 kolumny ═══
_DW5 = {
    "code": "DW5", "category_code": "DW",
    "name": "3 kolumny — obrazy + teksty",
    "description": "3 zdjęcia w rzędzie, 3 teksty pod nimi. Pełna strona.",
    "media_type": "photo", "layout_type": "grid-3", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_MULTI(3),
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;flex-direction:column;padding:48px 64px;">
  {{#if eyebrow}}<div style="text-align:center;font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;margin-bottom:32px;">{{eyebrow}}</div>{{/if}}
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;flex:1;">
    <div style="display:flex;flex-direction:column;gap:16px;"><div style="flex:0 0 55%;border-radius:14px;overflow:hidden;"><img src="{{image_1}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:22px;font-weight:700;color:#1e293b;margin:0;">{{heading_1}}</h3><div style="font-size:14px;color:#64748b;line-height:1.7;">{{body_1}}</div></div>
    <div style="display:flex;flex-direction:column;gap:16px;"><div style="flex:0 0 55%;border-radius:14px;overflow:hidden;"><img src="{{image_2}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:22px;font-weight:700;color:#1e293b;margin:0;">{{heading_2}}</h3><div style="font-size:14px;color:#64748b;line-height:1.7;">{{body_2}}</div></div>
    <div style="display:flex;flex-direction:column;gap:16px;"><div style="flex:0 0 55%;border-radius:14px;overflow:hidden;"><img src="{{image_3}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:22px;font-weight:700;color:#1e293b;margin:0;">{{heading_3}}</h3><div style="font-size:14px;color:#64748b;line-height:1.7;">{{body_3}}</div></div>
  </div>
</section>""",
}

# ═══ DW6 — 4 kolumny ═══
_DW6 = {
    "code": "DW6", "category_code": "DW",
    "name": "4 kolumny — obrazy + teksty",
    "description": "4 zdjęcia w rzędzie, 4 teksty pod nimi. Pełna strona.",
    "media_type": "photo", "layout_type": "grid-4", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_MULTI(4),
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;flex-direction:column;padding:48px 64px;">
  {{#if eyebrow}}<div style="text-align:center;font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;margin-bottom:32px;">{{eyebrow}}</div>{{/if}}
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:20px;flex:1;">
    <div style="display:flex;flex-direction:column;gap:12px;"><div style="flex:0 0 50%;border-radius:12px;overflow:hidden;"><img src="{{image_1}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:18px;font-weight:700;color:#1e293b;margin:0;">{{heading_1}}</h3><div style="font-size:13px;color:#64748b;line-height:1.6;">{{body_1}}</div></div>
    <div style="display:flex;flex-direction:column;gap:12px;"><div style="flex:0 0 50%;border-radius:12px;overflow:hidden;"><img src="{{image_2}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:18px;font-weight:700;color:#1e293b;margin:0;">{{heading_2}}</h3><div style="font-size:13px;color:#64748b;line-height:1.6;">{{body_2}}</div></div>
    <div style="display:flex;flex-direction:column;gap:12px;"><div style="flex:0 0 50%;border-radius:12px;overflow:hidden;"><img src="{{image_3}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:18px;font-weight:700;color:#1e293b;margin:0;">{{heading_3}}</h3><div style="font-size:13px;color:#64748b;line-height:1.6;">{{body_3}}</div></div>
    <div style="display:flex;flex-direction:column;gap:12px;"><div style="flex:0 0 50%;border-radius:12px;overflow:hidden;"><img src="{{image_4}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div><h3 style="font-size:18px;font-weight:700;color:#1e293b;margin:0;">{{heading_4}}</h3><div style="font-size:13px;color:#64748b;line-height:1.6;">{{body_4}}</div></div>
  </div>
</section>""",
}

# ═══ DW7 — Kolumny: obrazy LEWO + teksty PRAWO ═══
_DW7 = {
    "code": "DW7", "category_code": "DW",
    "name": "Obrazy lewo + Teksty prawo (kolumny)",
    "description": "Lewa kolumna: 3 zdjęcia. Prawa: 3 teksty. Pełna strona.",
    "media_type": "photo", "layout_type": "columns", "size": "L",
    "page_height": "F",
    "slots_definition": _SLOTS_MULTI(3),
    "html_template": """<section style="width:100%;min-height:100vh;display:grid;grid-template-columns:1fr 1fr;">
  <div style="display:flex;flex-direction:column;gap:8px;padding:32px;">
    <div style="flex:1;border-radius:14px;overflow:hidden;"><img src="{{image_1}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div>
    <div style="flex:1;border-radius:14px;overflow:hidden;"><img src="{{image_2}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div>
    <div style="flex:1;border-radius:14px;overflow:hidden;"><img src="{{image_3}}" alt="" style="width:100%;height:100%;object-fit:cover;"/></div>
  </div>
  <div style="display:flex;flex-direction:column;justify-content:center;gap:40px;padding:64px;">
    {{#if eyebrow}}<div style="font-size:12px;font-weight:600;letter-spacing:5px;text-transform:uppercase;color:#8b7355;">{{eyebrow}}</div>{{/if}}
    <div><h3 style="font-size:24px;font-weight:700;color:#1e293b;margin:0 0 10px;">{{heading_1}}</h3><div style="font-size:15px;color:#64748b;line-height:1.7;">{{body_1}}</div></div>
    <div><h3 style="font-size:24px;font-weight:700;color:#1e293b;margin:0 0 10px;">{{heading_2}}</h3><div style="font-size:15px;color:#64748b;line-height:1.7;">{{body_2}}</div></div>
    <div><h3 style="font-size:24px;font-weight:700;color:#1e293b;margin:0 0 10px;">{{heading_3}}</h3><div style="font-size:15px;color:#64748b;line-height:1.7;">{{body_3}}</div></div>
  </div>
</section>""",
}

# ═══ DW8 — Cytat z obrazem ═══
_DW8 = {
    "code": "DW8", "category_code": "DW",
    "name": "Cytat z obrazem",
    "description": "Zdjęcie w tle, wyróżniony cytat na pierwszym planie. Pełna strona.",
    "media_type": "photo", "layout_type": "quote", "size": "L",
    "page_height": "F",
    "slots_definition": [
        {"id": "image", "type": "image", "label": "Zdjęcie w tle"},
        {"id": "heading", "type": "text", "label": "Cytat / nagłówek"},
        {"id": "body", "type": "text", "label": "Podpis / autor"},
    ],
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.6)),url('{{image}}') center/cover no-repeat;">
  <div style="max-width:800px;text-align:center;padding:80px 64px;">
    <div style="width:56px;height:2px;background:#c4a87a;margin:0 auto 32px;"></div>
    <h2 style="font-size:36px;font-weight:300;font-style:italic;color:#fff;margin:0 0 24px;line-height:1.5;">{{heading}}</h2>
    {{#if body}}<div style="font-size:16px;color:#c4a87a;font-weight:500;">{{body}}</div>{{/if}}
    <div style="width:56px;height:2px;background:#c4a87a;margin:32px auto 0;"></div>
  </div>
</section>""",
}

# ═══ CTA1 — Zaproszenie ═══
_CTA1 = {
    "code": "CTA1", "category_code": "CTA",
    "name": "CTA — zaproszenie do kontaktu",
    "description": "Ciemne tło, nagłówek, przycisk, dane kontaktowe. Pełna strona.",
    "media_type": "none", "layout_type": "cta", "size": "L",
    "page_height": "F",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Nagłówek"},
        {"id": "body", "type": "text", "label": "Tekst"},
        {"id": "cta_text", "type": "text", "label": "Tekst przycisku"},
        {"id": "cta_url", "type": "url", "label": "Link"},
        {"id": "contact_name", "type": "text", "label": "Osoba kontaktowa"},
        {"id": "contact_email", "type": "text", "label": "Email"},
        {"id": "contact_phone", "type": "text", "label": "Telefon"},
    ],
    "html_template": """<section style="width:100%;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#111827;padding:80px 64px;">
  <div style="text-align:center;max-width:700px;">
    <h2 style="font-size:44px;font-weight:700;color:#fff;margin:0 0 20px;">{{heading}}</h2>
    {{#if body}}<p style="font-size:18px;color:#9ca3af;margin:0 0 40px;line-height:1.7;">{{body}}</p>{{/if}}
    {{#if cta_url}}<a href="{{cta_url}}" style="display:inline-block;background:#6366f1;color:#fff;padding:16px 44px;border-radius:14px;font-size:18px;font-weight:700;text-decoration:none;">{{cta_text}}</a>{{/if}}
    <div style="display:flex;justify-content:center;gap:32px;margin-top:40px;font-size:15px;color:#6b7280;">
      {{#if contact_name}}<span>{{contact_name}}</span>{{/if}}
      {{#if contact_email}}<a href="mailto:{{contact_email}}" style="color:#818cf8;">{{contact_email}}</a>{{/if}}
      {{#if contact_phone}}<span>{{contact_phone}}</span>{{/if}}
    </div>
  </div>
</section>""",
}


ALL_OFFER_BLOCKS = [_NO1, _NO2, _DW1, _DW2, _DW3, _DW4, _DW5, _DW6, _DW7, _DW8, _CTA1]


async def seed_offer_blocks(db: AsyncSession) -> dict:
    cat_count = 0
    for cat in OFFER_CATEGORIES:
        existing = (await db.execute(select(BlockCategory).where(BlockCategory.code == cat["code"]))).scalar_one_or_none()
        if not existing:
            db.add(BlockCategory(**cat)); cat_count += 1
        else:
            for k, v in cat.items(): setattr(existing, k, v)
    block_count = 0
    for block in ALL_OFFER_BLOCKS:
        existing = (await db.execute(select(BlockTemplate).where(BlockTemplate.code == block["code"]))).scalar_one_or_none()
        if not existing:
            db.add(BlockTemplate(**block)); block_count += 1
        else:
            for k, v in block.items(): setattr(existing, k, v)
    await db.commit()
    return {"categories": cat_count, "blocks": block_count}
