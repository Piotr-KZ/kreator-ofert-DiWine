"""
Seed — offer block templates (8 blocks in 4 categories).
Separate from creator seed_blocks.py but same pattern.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.block_template import BlockCategory, BlockTemplate

OFFER_CATEGORIES = [
    {"code": "OG", "name": "Oferta Nagłówek", "icon": "file-text", "order": 50},
    {"code": "OZ", "name": "Oferta Zestaw", "icon": "package", "order": 51},
    {"code": "OT", "name": "Oferta Tekst", "icon": "type", "order": 52},
    {"code": "OA", "name": "Oferta Akcja", "icon": "check-circle", "order": 53},
]

# ════════════════════════════════════════
# OG — NAGŁÓWEK OFERTY
# ════════════════════════════════════════

_OG1 = {
    "code": "OG1",
    "category_code": "OG",
    "name": "Nagłówek oferty — standard",
    "description": "Numer oferty, data, logo firmy, zdjęcie lifestyle w tle.",
    "media_type": "photo",
    "layout_type": "full-width",
    "size": "L",
    "slots_definition": [
        {"id": "offer_number", "type": "text", "label": "Numer oferty", "required": True},
        {"id": "date", "type": "text", "label": "Data wystawienia"},
        {"id": "expires", "type": "text", "label": "Ważna do"},
        {"id": "client_name", "type": "text", "label": "Nazwa klienta", "required": True},
        {"id": "client_logo_url", "type": "image", "label": "Logo klienta"},
        {"id": "bg_photo_url", "type": "image", "label": "Zdjęcie w tle"},
        {"id": "occasion_name", "type": "text", "label": "Okazja"},
    ],
    "html_template": """<section class="relative min-h-[400px] flex items-center" style="background:linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.55)),url('{{bg_photo_url}}') center/cover no-repeat;">
  <div class="max-w-5xl mx-auto px-8 py-16 w-full">
    <div class="flex items-start justify-between">
      <div>
        <div class="text-indigo-300 text-sm font-semibold tracking-widest uppercase mb-2">OFERTA PREZENTOWA</div>
        <h1 class="text-4xl font-bold text-white mb-3">{{occasion_name}}</h1>
        <div class="text-gray-300 text-lg mb-1">dla <strong class="text-white">{{client_name}}</strong></div>
        <div class="flex gap-4 mt-4 text-sm text-gray-400">
          <span>Nr: {{offer_number}}</span>
          <span>Data: {{date}}</span>
          {{#if expires}}<span>Ważna do: {{expires}}</span>{{/if}}
        </div>
      </div>
      {{#if client_logo_url}}<img src="{{client_logo_url}}" alt="{{client_name}}" class="h-16 w-auto bg-white rounded-xl p-3 shadow-lg" />{{/if}}
    </div>
  </div>
</section>""",
}

_OG2 = {
    "code": "OG2",
    "category_code": "OG",
    "name": "Nagłówek oferty — pełnoekranowy",
    "description": "Duże zdjęcie, logo klienta, minimalistyczny tekst.",
    "media_type": "photo",
    "layout_type": "full-width",
    "size": "L",
    "slots_definition": _OG1["slots_definition"],
    "html_template": """<section class="relative min-h-[500px] flex items-end" style="background:linear-gradient(to top,rgba(0,0,0,0.7) 0%,rgba(0,0,0,0.1) 60%),url('{{bg_photo_url}}') center/cover no-repeat;">
  <div class="max-w-5xl mx-auto px-8 pb-12 w-full">
    {{#if client_logo_url}}<img src="{{client_logo_url}}" alt="" class="h-12 w-auto bg-white/90 rounded-lg p-2 mb-4" />{{/if}}
    <h1 class="text-5xl font-bold text-white mb-2">Oferta prezentowa</h1>
    <div class="text-xl text-gray-200 mb-1">{{occasion_name}} — {{client_name}}</div>
    <div class="text-sm text-gray-400 mt-3">{{offer_number}} • {{date}}</div>
  </div>
</section>""",
}

# ════════════════════════════════════════
# OZ — ZESTAW PREZENTOWY
# ════════════════════════════════════════

_OZ1 = {
    "code": "OZ1",
    "category_code": "OZ",
    "name": "Zestaw — tabela z opisem",
    "description": "Nazwa zestawu, opis, tabela składników z cenami, suma.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "set_name", "type": "text", "label": "Nazwa zestawu", "required": True},
        {"id": "set_description", "type": "text", "label": "Opis zestawu"},
        {"id": "unit_price", "type": "text", "label": "Cena za sztukę"},
        {"id": "total_price", "type": "text", "label": "Cena razem"},
        {"id": "quantity", "type": "text", "label": "Ilość sztuk"},
        {"id": "packaging_name", "type": "text", "label": "Opakowanie"},
        {"id": "packaging_price", "type": "text", "label": "Cena opakowania"},
        {"id": "items", "type": "list", "label": "Składniki", "item_fields": [
            {"id": "name", "type": "text", "label": "Nazwa"},
            {"id": "type_label", "type": "text", "label": "Typ"},
            {"id": "color_name", "type": "text", "label": "Kolor"},
            {"id": "price", "type": "text", "label": "Cena"},
        ]},
    ],
    "html_template": """<section class="py-12">
  <div class="max-w-4xl mx-auto px-8">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">{{set_name}}</h2>
        {{#if set_description}}<p class="text-gray-500 mt-1">{{set_description}}</p>{{/if}}
      </div>
      <div class="text-right">
        <div class="text-3xl font-bold text-indigo-600">{{unit_price}} zł</div>
        <div class="text-sm text-gray-400">za sztukę netto</div>
      </div>
    </div>
    <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead><tr class="bg-gray-50 border-b">
          <th class="text-left p-4 font-semibold text-gray-600">Pozycja</th>
          <th class="text-left p-4 font-semibold text-gray-600">Typ</th>
          <th class="text-right p-4 font-semibold text-gray-600">Cena / szt.</th>
        </tr></thead>
        <tbody>
          <tr class="border-b"><td class="p-4 font-medium">{{packaging_name}}</td><td class="p-4 text-gray-500">Opakowanie</td><td class="p-4 text-right font-semibold">{{packaging_price}} zł</td></tr>
          {{#each items}}<tr class="border-b last:border-0">
            <td class="p-4 font-medium">{{this.name}}{{#if this.color_name}} <span class="text-xs text-gray-400">({{this.color_name}})</span>{{/if}}</td>
            <td class="p-4 text-gray-500">{{this.type_label}}</td>
            <td class="p-4 text-right font-semibold">{{this.price}} zł</td>
          </tr>{{/each}}
        </tbody>
        <tfoot><tr class="bg-indigo-50">
          <td colspan="2" class="p-4 font-bold text-gray-900">RAZEM</td>
          <td class="p-4 text-right font-bold text-indigo-600 text-lg">{{unit_price}} zł</td>
        </tr></tfoot>
      </table>
    </div>
    <div class="text-right mt-3 text-sm text-gray-400">{{quantity}} szt. × {{unit_price}} zł = <strong class="text-gray-700">{{total_price}} zł netto</strong></div>
  </div>
</section>""",
}

_OZ2 = {
    "code": "OZ2",
    "category_code": "OZ",
    "name": "Zestaw — karty ze zdjęciami",
    "description": "Wizualna prezentacja zestawu — karty produktów z cenami.",
    "media_type": "photo",
    "layout_type": "cards",
    "size": "L",
    "slots_definition": _OZ1["slots_definition"],
    "html_template": """<section class="py-12 bg-gray-50">
  <div class="max-w-5xl mx-auto px-8">
    <div class="text-center mb-8">
      <h2 class="text-2xl font-bold text-gray-900">{{set_name}}</h2>
      {{#if set_description}}<p class="text-gray-500 mt-2 max-w-xl mx-auto">{{set_description}}</p>{{/if}}
      <div class="mt-3 inline-flex items-center gap-2 bg-indigo-100 text-indigo-700 px-4 py-1.5 rounded-full text-sm font-semibold">{{unit_price}} zł / szt.</div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl p-4 border border-gray-200">
        <div class="text-xs text-gray-400 uppercase font-semibold mb-1">Opakowanie</div>
        <div class="font-bold text-gray-900">{{packaging_name}}</div>
        <div class="text-indigo-600 font-semibold mt-1">{{packaging_price}} zł</div>
      </div>
      {{#each items}}<div class="bg-white rounded-xl p-4 border border-gray-200">
        <div class="text-xs text-gray-400 uppercase font-semibold mb-1">{{this.type_label}}</div>
        <div class="font-bold text-gray-900">{{this.name}}</div>
        {{#if this.color_name}}<div class="text-xs text-gray-400">{{this.color_name}}</div>{{/if}}
        <div class="text-indigo-600 font-semibold mt-1">{{this.price}} zł</div>
      </div>{{/each}}
    </div>
    <div class="text-center mt-6 text-sm text-gray-400">{{quantity}} szt. × {{unit_price}} zł = <strong class="text-gray-700">{{total_price}} zł netto</strong></div>
  </div>
</section>""",
}

# ════════════════════════════════════════
# OT — TEKST OFERTOWY
# ════════════════════════════════════════

_OT1 = {
    "code": "OT1",
    "category_code": "OT",
    "name": "Tekst — jasne tło",
    "description": "Blok tekstowy na jasnym tle. Do powitań, dlaczego my, ciekawostek, zakończeń.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Nagłówek (opcjonalny)"},
        {"id": "body", "type": "text", "label": "Treść", "required": True},
    ],
    "html_template": """<section class="py-10">
  <div class="max-w-3xl mx-auto px-8">
    {{#if heading}}<h3 class="text-xl font-bold text-gray-900 mb-4">{{heading}}</h3>{{/if}}
    <div class="text-gray-600 leading-relaxed whitespace-pre-line">{{body}}</div>
  </div>
</section>""",
}

_OT2 = {
    "code": "OT2",
    "category_code": "OT",
    "name": "Tekst — kolorowe tło",
    "description": "Blok tekstowy na kolorowym tle. Do wyróżnienia sekcji.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": _OT1["slots_definition"],
    "html_template": """<section class="py-10 bg-indigo-50">
  <div class="max-w-3xl mx-auto px-8">
    {{#if heading}}<h3 class="text-xl font-bold text-indigo-900 mb-4">{{heading}}</h3>{{/if}}
    <div class="text-indigo-800 leading-relaxed whitespace-pre-line">{{body}}</div>
  </div>
</section>""",
}

_OT3 = {
    "code": "OT3",
    "category_code": "OT",
    "name": "Tekst — cytat / ciekawostka",
    "description": "Wyróżniony blok z ikoną cudzysłowu. Do ciekawostek i cytatów.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": _OT1["slots_definition"],
    "html_template": """<section class="py-10">
  <div class="max-w-3xl mx-auto px-8">
    <div class="border-l-4 border-indigo-400 pl-6">
      {{#if heading}}<div class="text-sm font-bold text-indigo-600 uppercase tracking-wider mb-2">{{heading}}</div>{{/if}}
      <div class="text-gray-700 leading-relaxed italic whitespace-pre-line">{{body}}</div>
    </div>
  </div>
</section>""",
}

# ════════════════════════════════════════
# OA — AKCJA / CTA
# ════════════════════════════════════════

_OA1 = {
    "code": "OA1",
    "category_code": "OA",
    "name": "CTA — akceptacja oferty",
    "description": "Przycisk akceptacji oferty + dane kontaktowe.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Nagłówek", "required": True},
        {"id": "body", "type": "text", "label": "Tekst pod nagłówkiem"},
        {"id": "cta_text", "type": "text", "label": "Tekst przycisku", "required": True},
        {"id": "cta_url", "type": "url", "label": "Link przycisku"},
        {"id": "contact_name", "type": "text", "label": "Osoba kontaktowa"},
        {"id": "contact_email", "type": "text", "label": "Email"},
        {"id": "contact_phone", "type": "text", "label": "Telefon"},
    ],
    "html_template": """<section class="py-16 bg-gray-900">
  <div class="max-w-3xl mx-auto px-8 text-center">
    <h2 class="text-3xl font-bold text-white mb-4">{{heading}}</h2>
    {{#if body}}<p class="text-gray-300 mb-8 text-lg">{{body}}</p>{{/if}}
    {{#if cta_url}}<a href="{{cta_url}}" class="inline-block bg-indigo-500 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-indigo-600 transition-colors mb-8">{{cta_text}}</a>{{/if}}
    <div class="flex items-center justify-center gap-8 text-sm text-gray-400">
      {{#if contact_name}}<span>{{contact_name}}</span>{{/if}}
      {{#if contact_email}}<a href="mailto:{{contact_email}}" class="text-indigo-400 hover:text-indigo-300">{{contact_email}}</a>{{/if}}
      {{#if contact_phone}}<span>{{contact_phone}}</span>{{/if}}
    </div>
  </div>
</section>""",
}


ALL_OFFER_BLOCKS = [_OG1, _OG2, _OZ1, _OZ2, _OT1, _OT2, _OT3, _OA1]


async def seed_offer_blocks(db: AsyncSession) -> dict:
    """Seed offer block categories and templates. Returns counts."""
    # Categories
    cat_count = 0
    for cat in OFFER_CATEGORIES:
        existing = (await db.execute(
            select(BlockCategory).where(BlockCategory.code == cat["code"])
        )).scalar_one_or_none()
        if not existing:
            db.add(BlockCategory(**cat))
            cat_count += 1
        else:
            for k, v in cat.items():
                setattr(existing, k, v)

    # Templates
    block_count = 0
    for block in ALL_OFFER_BLOCKS:
        existing = (await db.execute(
            select(BlockTemplate).where(BlockTemplate.code == block["code"])
        )).scalar_one_or_none()
        if not existing:
            db.add(BlockTemplate(**block))
            block_count += 1
        else:
            for k, v in block.items():
                setattr(existing, k, v)

    await db.commit()
    return {"categories": cat_count, "blocks": block_count}
