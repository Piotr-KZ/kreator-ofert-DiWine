"""
Seed data — 40 block templates with HTML + slot definitions.
Brief 33: slot-based templates, Tailwind CSS, responsive.

Run via: seed_block_templates(db)
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockTemplate

# ============================================================================
# NAWIGACJA (3)
# ============================================================================

_NA1 = {
    "code": "NA1",
    "category_code": "NA",
    "name": "Nawigacja jasna",
    "description": "Klasyczna jasna nawigacja. Logo po lewej, menu po prawej, przycisk CTA. Dobra dla wiekszosci stron.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": [
        {"id": "logo_url", "type": "image", "label": "Logo", "required": False},
        {"id": "logo", "type": "text", "label": "Nazwa firmy", "max_length": 40, "required": True},
        {"id": "links", "type": "list", "label": "Menu", "item_fields": [
            {"id": "text", "type": "text", "label": "Tekst"},
        ]},
        {"id": "cta", "type": "text", "label": "Przycisk CTA", "max_length": 25, "required": False},
        {"id": "cta_url", "type": "url", "label": "Link CTA", "required": False},
    ],
    "html_template": """<nav class="bg-white border-b border-gray-100 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
    <div class="flex items-center gap-3">
      {{#if logo_url}}<img src="{{logo_url}}" alt="{{logo_text}}" class="h-8 w-auto" />{{/if}}
      <span class="text-lg font-bold text-gray-900">{{logo_text}}</span>
    </div>
    <div class="hidden md:flex items-center gap-8">
      {{#each menu_items}}<a href="{{this.url}}" class="text-sm text-gray-600 hover:text-gray-900 font-medium">{{this.label}}</a>{{/each}}
      {{#if cta_text}}<a href="{{cta_url}}" class="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700">{{cta_text}}</a>{{/if}}
    </div>
  </div>
</nav>""",
}

_NA2 = {
    "code": "NA2",
    "category_code": "NA",
    "name": "Nawigacja ciemna",
    "description": "Ciemna nawigacja na dark header. Profesjonalny wyglad, pasuje do ciemnych hero.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": _NA1["slots_definition"],
    "html_template": """<nav class="bg-gray-950 border-b border-gray-800 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
    <div class="flex items-center gap-3">
      {{#if logo_url}}<img src="{{logo_url}}" alt="{{logo_text}}" class="h-8 w-auto" />{{/if}}
      <span class="text-lg font-bold text-white">{{logo_text}}</span>
    </div>
    <div class="hidden md:flex items-center gap-8">
      {{#each menu_items}}<a href="{{this.url}}" class="text-sm text-gray-400 hover:text-white font-medium">{{this.label}}</a>{{/each}}
      {{#if cta_text}}<a href="{{cta_url}}" class="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700">{{cta_text}}</a>{{/if}}
    </div>
  </div>
</nav>""",
}

_NA3 = {
    "code": "NA3",
    "category_code": "NA",
    "name": "Nawigacja z podkresleniem",
    "description": "Menu wycentrowane z podkresleniem aktywnego elementu. Elegancka, nowoczesna.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": _NA1["slots_definition"],
    "html_template": """<nav class="bg-white border-b border-gray-100 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
    <div class="flex items-center gap-3">
      {{#if logo_url}}<img src="{{logo_url}}" alt="{{logo_text}}" class="h-8 w-auto" />{{/if}}
      <span class="text-lg font-bold text-gray-900">{{logo_text}}</span>
    </div>
    <div class="hidden md:flex items-center gap-8">
      {{#each menu_items}}<a href="{{this.url}}" class="text-sm text-gray-600 hover:text-indigo-600 font-medium border-b-2 border-transparent hover:border-indigo-600 pb-1">{{this.label}}</a>{{/each}}
    </div>
    {{#if cta_text}}<a href="{{cta_url}}" class="hidden md:inline-flex bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700">{{cta_text}}</a>{{/if}}
  </div>
</nav>""",
}

# ============================================================================
# HERO (5)
# ============================================================================

_HE1 = {
    "code": "HE1",
    "category_code": "HE",
    "name": "Hero centered, ciemne tlo, statystyki",
    "description": "Uzyj gdy: strona ma robic wrazenie, firma ma liczby (lata, projekty, klienci). Ciemne tlo = profesjonalizm.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "L",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul glowny", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": True},
        {"id": "cta", "type": "text", "label": "Przycisk glowny", "max_length": 30, "required": True},
        {"id": "cta2", "type": "text", "label": "Drugi przycisk", "max_length": 30, "required": False},
        {"id": "stats", "type": "list", "label": "Statystyki", "item_fields": [
            {"id": "value", "type": "text", "label": "Liczba"},
            {"id": "label", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-gradient-to-br from-gray-950 via-indigo-950 to-gray-900 text-white py-24 px-8">
  <div class="max-w-4xl mx-auto text-center">
    {{#if pre_title}}<p class="text-indigo-400 font-semibold text-sm uppercase tracking-wide mb-4">{{pre_title}}</p>{{/if}}
    <h1 class="text-4xl lg:text-5xl font-extrabold leading-tight mb-6">{{title}}</h1>
    <p class="text-xl text-gray-400 max-w-2xl mx-auto mb-10">{{subtitle}}</p>
    <div class="flex gap-4 justify-center flex-wrap">
      <a href="#kontakt" class="bg-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700">{{cta_primary}}</a>
      {{#if cta_secondary}}<a href="#oferta" class="border-2 border-gray-600 text-gray-300 px-8 py-4 rounded-xl font-semibold text-lg hover:border-gray-400">{{cta_secondary}}</a>{{/if}}
    </div>
    {{#if stats}}<div class="mt-12 flex justify-center gap-12 flex-wrap text-sm text-gray-500">
      {{#each stats}}<div><span class="text-white font-bold text-lg">{{this.value}}</span><br/>{{this.label}}</div>{{/each}}
    </div>{{/if}}
  </div>
</section>""",
}

_HE2 = {
    "code": "HE2",
    "category_code": "HE",
    "name": "Hero split tekst L + zdjecie R",
    "description": "Klasyczny split hero: tekst po lewej, zdjecie po prawej. Idealny gdy masz dobre zdjecie firmy/produktu.",
    "media_type": "photo",
    "layout_type": "photo-full-2",
    "size": "L",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul glowny", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": True},
        {"id": "cta", "type": "text", "label": "Przycisk glowny", "max_length": 30, "required": True},
        {"id": "cta_url", "type": "url", "label": "Link przycisku", "required": True},
        {"id": "cta2", "type": "text", "label": "Drugi przycisk (opcj.)", "max_length": 30, "required": False},
        {"id": "image", "type": "image", "label": "Zdjecie", "aspect_ratio": "4:3", "required": True},
        {"id": "image_alt", "type": "text", "label": "Opis zdjecia (alt)", "max_length": 100, "required": False},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
    <div>
      {{#if pre_title}}<p class="text-indigo-600 font-semibold text-sm uppercase tracking-wide mb-4">{{pre_title}}</p>{{/if}}
      <h1 class="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight mb-6">{{title}}</h1>
      <p class="text-lg text-gray-600 mb-8">{{subtitle}}</p>
      <div class="flex flex-wrap gap-4">
        <a href="{{cta_url}}" class="bg-indigo-600 text-white px-7 py-3.5 rounded-xl font-semibold hover:bg-indigo-700">{{cta_primary}}</a>
        {{#if cta_secondary_text}}<span class="text-indigo-600 font-semibold px-7 py-3.5">{{cta_secondary_text}}</span>{{/if}}
      </div>
    </div>
    <div>
      <img src="{{image}}" alt="{{image_alt}}" class="w-full h-auto rounded-2xl shadow-lg object-cover" loading="lazy" />
    </div>
  </div>
</section>""",
}

_HE3 = {
    "code": "HE3",
    "category_code": "HE",
    "name": "Hero tekst L + formularz R",
    "description": "Hero z formularzem kontaktowym po prawej. Swietny do lead generation i landing pages.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "L",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Tytul glowny", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": True},
        {"id": "checkmarks", "type": "list", "label": "Punkty", "item_fields": [
            {"id": "text", "type": "text", "label": "Tekst"},
        ]},
        {"id": "form_title", "type": "text", "label": "Tytul formularza", "max_length": 50, "required": True},
        {"id": "form_fields", "type": "list", "label": "Pola formularza", "item_fields": [
            {"id": "label", "type": "text", "label": "Etykieta"},
            {"id": "type", "type": "text", "label": "Typ (text/email/tel)"},
        ]},
    ],
    "html_template": """<section class="bg-gradient-to-br from-indigo-50 to-white py-20 px-8">
  <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
    <div>
      <h1 class="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight mb-6">{{title}}</h1>
      <p class="text-lg text-gray-600 mb-8">{{subtitle}}</p>
      {{#if checkmarks}}<ul class="space-y-3">
        {{#each checkmarks}}<li class="flex items-center gap-3 text-gray-700"><span class="text-green-500 text-lg">&#10003;</span> {{this.text}}</li>{{/each}}
      </ul>{{/if}}
    </div>
    <div class="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
      <h3 class="text-xl font-bold text-gray-900 mb-6">{{form_title}}</h3>
      <form class="space-y-4">
        {{#each form_fields}}<div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{this.label}}</label>
          <input type="{{this.type}}" class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:border-indigo-400 outline-none" />
        </div>{{/each}}
        <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold hover:bg-indigo-700">Wyslij</button>
      </form>
    </div>
  </div>
</section>""",
}

_HE4 = {
    "code": "HE4",
    "category_code": "HE",
    "name": "Hero video background",
    "description": "Hero z video w tle. Dynamiczny, nowoczesny. Wymaga video URL (YouTube/Vimeo embed).",
    "media_type": "video",
    "layout_type": "vid-full",
    "size": "L",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Tytul glowny", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": True},
        {"id": "cta", "type": "text", "label": "Przycisk", "max_length": 30, "required": True},
        {"id": "cta_url", "type": "url", "label": "Link", "required": True},
        {"id": "video_url", "type": "video", "label": "URL video", "required": True},
    ],
    "html_template": """<section class="relative bg-gray-900 text-white py-32 px-8 overflow-hidden min-h-[500px] flex items-center">
  <div class="absolute inset-0 bg-black/60 z-10"></div>
  <div class="relative z-20 max-w-4xl mx-auto text-center">
    <h1 class="text-4xl lg:text-6xl font-extrabold leading-tight mb-6">{{title}}</h1>
    <p class="text-xl text-gray-300 max-w-2xl mx-auto mb-10">{{subtitle}}</p>
    <a href="{{cta_url}}" class="bg-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700 inline-block">{{cta_text}}</a>
  </div>
</section>""",
}

_HE5 = {
    "code": "HE5",
    "category_code": "HE",
    "name": "Hero minimal centered",
    "description": "Minimalistyczny hero z tytulem i jednym CTA. Prosty, czysty, nowoczesny.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Tytul glowny", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": True},
        {"id": "cta", "type": "text", "label": "Przycisk", "max_length": 30, "required": True},
        {"id": "cta_url", "type": "url", "label": "Link", "required": True},
    ],
    "html_template": """<section class="bg-white py-24 px-8">
  <div class="max-w-3xl mx-auto text-center">
    <h1 class="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight mb-6">{{title}}</h1>
    <p class="text-lg text-gray-500 mb-10">{{subtitle}}</p>
    <a href="{{cta_url}}" class="bg-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700 inline-block">{{cta_text}}</a>
  </div>
</section>""",
}

# ============================================================================
# PERSWAZYJNE — Problem (3)
# ============================================================================

_PB1 = {
    "code": "PB1",
    "category_code": "PB",
    "name": "Problem — lista z opisem",
    "description": "Lista problemow klienta z ikonami i opisami. Buduje empatie i pokazuje zrozumienie.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "problems", "type": "list", "label": "Problemy", "item_fields": [
            {"id": "icon", "type": "icon", "label": "Ikona"},
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "description", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-4xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-4">{{title}}</h2>
    {{#if subtitle}}<p class="text-gray-500 text-center mb-12 max-w-2xl mx-auto">{{subtitle}}</p>{{/if}}
    <div class="space-y-6">
      {{#each problems}}<div class="bg-white rounded-xl p-6 border border-gray-100 flex gap-4">
        <div class="text-red-500 text-2xl flex-shrink-0 mt-1">&#9888;</div>
        <div>
          <h3 class="font-semibold text-gray-900 mb-1">{{this.title}}</h3>
          <p class="text-sm text-gray-600">{{this.description}}</p>
        </div>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_PB2 = {
    "code": "PB2",
    "category_code": "PB",
    "name": "Problem — pytania retoryczne",
    "description": "Seria pytan retorycznych ktore rezonuja z problemami klienta. Emocjonalny przekaz.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "questions", "type": "list", "label": "Pytania", "item_fields": [
            {"id": "text", "type": "text", "label": "Pytanie"},
        ]},
    ],
    "html_template": """<section class="bg-gray-900 text-white py-20 px-8">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold mb-12">{{title}}</h2>
    <div class="space-y-6">
      {{#each questions}}<p class="text-xl text-gray-300 italic">"{{this.text}}"</p>{{/each}}
    </div>
  </div>
</section>""",
}

_PB3 = {
    "code": "PB3",
    "category_code": "PB",
    "name": "Problem — statystyki",
    "description": "Problemy poparte statystykami/liczbami. Buduje wiarygodnosc argumentu.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "stats", "type": "list", "label": "Statystyki", "item_fields": [
            {"id": "value", "type": "text", "label": "Wartosc"},
            {"id": "label", "type": "text", "label": "Etykieta"},
            {"id": "description", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-red-50 py-20 px-8">
  <div class="max-w-5xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each stats}}<div class="text-center bg-white rounded-xl p-8 shadow-sm border border-red-100">
        <div class="text-4xl font-extrabold text-red-600 mb-2">{{this.value}}</div>
        <div class="font-semibold text-gray-900 mb-1">{{this.label}}</div>
        <p class="text-sm text-gray-500">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# PERSWAZYJNE — Rozwiazanie (2)
# ============================================================================

_RO1 = {
    "code": "RO1",
    "category_code": "RO",
    "name": "Rozwiazanie — karty",
    "description": "3 karty rozwiazania z ikonami. Jasny przekaz 'oto jak to rozwiazujemy'.",
    "media_type": "none",
    "layout_type": "info-title-text-3",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "features", "type": "list", "label": "Rozwiazania", "item_fields": [
            {"id": "icon", "type": "icon", "label": "Ikona"},
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "body", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-4">{{title}}</h2>
    {{#if subtitle}}<p class="text-gray-500 text-center mb-12 max-w-2xl mx-auto">{{subtitle}}</p>{{/if}}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each solutions}}<div class="bg-indigo-50 rounded-2xl p-8 text-center">
        <div class="text-indigo-600 text-3xl mb-4">&#10003;</div>
        <h3 class="font-bold text-gray-900 mb-2">{{this.title}}</h3>
        <p class="text-sm text-gray-600">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_RO2 = {
    "code": "RO2",
    "category_code": "RO",
    "name": "Rozwiazanie — split z obrazem",
    "description": "Tekst po lewej z lista cech, zdjecie po prawej. Dobry gdy masz screenshot/zdjecie produktu.",
    "media_type": "photo",
    "layout_type": "photo-full-2",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Opis", "max_length": 300, "required": True},
        {"id": "features", "type": "list", "label": "Cechy", "item_fields": [
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "body", "type": "text", "label": "Opis"},
        ]},
        {"id": "image", "type": "image", "label": "Zdjecie", "aspect_ratio": "4:3", "required": True},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
    <div>
      <h2 class="text-3xl font-bold text-gray-900 mb-4">{{title}}</h2>
      <p class="text-gray-600 mb-6">{{description}}</p>
      {{#if features}}<ul class="space-y-3">
        {{#each features}}<li class="flex items-center gap-3 text-gray-700"><span class="text-green-500">&#10003;</span> {{this.text}}</li>{{/each}}
      </ul>{{/if}}
    </div>
    <div>
      <img src="{{image}}" alt="" class="w-full h-auto rounded-2xl shadow-lg object-cover" loading="lazy" />
    </div>
  </div>
</section>""",
}

# ============================================================================
# PERSWAZYJNE — Korzysci (2)
# ============================================================================

_KR1 = {
    "code": "KR1",
    "category_code": "KR",
    "name": "Korzysci — ikony + opisy",
    "description": "Grid 2x3 korzysci z ikonami. Klasyczny uklad pokazujacy wartosci dla klienta.",
    "media_type": "none",
    "layout_type": "info-title-text-3",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "points", "type": "list", "label": "Korzysci", "item_fields": [
            {"id": "text", "type": "text", "label": "Korzysc"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {{#each benefits}}<div class="text-center p-6">
        <div class="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center mx-auto mb-4 text-indigo-600 text-2xl">&#9733;</div>
        <h3 class="font-bold text-gray-900 mb-2">{{this.title}}</h3>
        <p class="text-sm text-gray-600">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_KR2 = {
    "code": "KR2",
    "category_code": "KR",
    "name": "Korzysci — duze liczby",
    "description": "4 duze liczby z opisami. Idealny gdy masz twarde dane (% wzrost, ilosc klientow).",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "points", "type": "list", "label": "Korzysci", "item_fields": [
            {"id": "text", "type": "text", "label": "Korzysc"},
        ]},
    ],
    "html_template": """<section class="bg-indigo-600 text-white py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-8">
      {{#each benefits}}<div class="text-center">
        <div class="text-4xl font-extrabold mb-2">{{this.number}}</div>
        <div class="font-semibold text-indigo-200 mb-1">{{this.label}}</div>
        <p class="text-sm text-indigo-300">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# PERSWAZYJNE — Cechy (2)
# ============================================================================

_CF1 = {
    "code": "CF1",
    "category_code": "CF",
    "name": "Cechy — karty z ikonami",
    "description": "Grid 3 kart z ikonami i opisami cech produktu/uslugi.",
    "media_type": "none",
    "layout_type": "info-title-text-3",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "features", "type": "list", "label": "Cechy", "item_fields": [
            {"id": "icon", "type": "icon", "label": "Ikona"},
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "body", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each features}}<div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        <div class="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4 text-indigo-600 text-xl">&#9889;</div>
        <h3 class="font-bold text-gray-900 mb-2">{{this.title}}</h3>
        <p class="text-sm text-gray-600">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_CF2 = {
    "code": "CF2",
    "category_code": "CF",
    "name": "Cechy — checklist",
    "description": "Dwukolumnowa lista cech ze znacznikami. Czytelna, zwarta, bez dodatkowych grafik.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "features", "type": "list", "label": "Cechy", "item_fields": [
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "body", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-4xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-4">{{title}}</h2>
    {{#if subtitle}}<p class="text-gray-500 text-center mb-12">{{subtitle}}</p>{{/if}}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4">
      {{#each features_left}}<div class="flex items-center gap-3"><span class="text-green-500">&#10003;</span><span class="text-gray-700">{{this.text}}</span></div>{{/each}}
      {{#each features_right}}<div class="flex items-center gap-3"><span class="text-green-500">&#10003;</span><span class="text-gray-700">{{this.text}}</span></div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# PERSWAZYJNE — Obiekcje (1)
# ============================================================================

_OB1 = {
    "code": "OB1",
    "category_code": "OB",
    "name": "Obiekcje — FAQ style",
    "description": "Odpowiedzi na typowe obiekcje klientow w formacie pytanie-odpowiedz. Buduje zaufanie.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "objections", "type": "list", "label": "Obiekcje", "item_fields": [
            {"id": "question", "type": "text", "label": "Pytanie/Obiekcja"},
            {"id": "answer", "type": "text", "label": "Odpowiedz"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="space-y-6">
      {{#each objections}}<div class="border-b border-gray-200 pb-6">
        <h3 class="font-semibold text-gray-900 mb-2 text-lg">{{this.question}}</h3>
        <p class="text-gray-600">{{this.answer}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# TRESCIOWE — O firmie (4)
# ============================================================================

_FI1 = {
    "code": "FI1",
    "category_code": "FI",
    "name": "O firmie — tekst L + zdjecie R",
    "description": "Tekst o firmie po lewej, zdjecie po prawej. Klasyczny uklad 'o nas'.",
    "media_type": "photo",
    "layout_type": "photo-full-2",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "richtext", "label": "Opis firmy", "required": True},
        {"id": "points", "type": "list", "label": "Wyrozniki", "item_fields": [
            {"id": "text", "type": "text", "label": "Punkt"},
        ]},
        {"id": "image", "type": "image", "label": "Zdjecie", "aspect_ratio": "4:3", "required": True},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
    <div>
      <h2 class="text-3xl font-bold text-gray-900 mb-6">{{title}}</h2>
      <div class="text-gray-600 mb-6 space-y-3">{{description}}</div>
      {{#if highlights}}<ul class="space-y-2">
        {{#each highlights}}<li class="flex items-center gap-3 text-gray-700 font-medium"><span class="text-indigo-600">&#9679;</span> {{this.text}}</li>{{/each}}
      </ul>{{/if}}
    </div>
    <div>
      <img src="{{image}}" alt="" class="w-full h-auto rounded-2xl shadow-lg object-cover" loading="lazy" />
    </div>
  </div>
</section>""",
}

_FI2 = {
    "code": "FI2",
    "category_code": "FI",
    "name": "O firmie — zdjecie L + tekst R",
    "description": "Zdjecie po lewej, tekst po prawej. Odwrocony uklad FI1.",
    "media_type": "photo",
    "layout_type": "photo-full-2",
    "size": "M",
    "slots_definition": _FI1["slots_definition"],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
    <div>
      <img src="{{image}}" alt="" class="w-full h-auto rounded-2xl shadow-lg object-cover" loading="lazy" />
    </div>
    <div>
      <h2 class="text-3xl font-bold text-gray-900 mb-6">{{title}}</h2>
      <div class="text-gray-600 mb-6 space-y-3">{{description}}</div>
      {{#if highlights}}<ul class="space-y-2">
        {{#each highlights}}<li class="flex items-center gap-3 text-gray-700 font-medium"><span class="text-indigo-600">&#9679;</span> {{this.text}}</li>{{/each}}
      </ul>{{/if}}
    </div>
  </div>
</section>""",
}

_FI3 = {
    "code": "FI3",
    "category_code": "FI",
    "name": "O firmie — centered z cytatem",
    "description": "Opis firmy na srodku z wyroznionym cytatem zalozycieli. Osobisty, buduje zaufanie.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "richtext", "label": "Opis firmy", "required": True},
        {"id": "quote", "type": "text", "label": "Cytat", "max_length": 300, "required": False},
        {"id": "quote_author", "type": "text", "label": "Autor cytatu", "max_length": 60, "required": False},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold text-gray-900 mb-6">{{title}}</h2>
    <div class="text-gray-600 mb-10 space-y-3">{{description}}</div>
    {{#if quote}}<blockquote class="border-l-4 border-indigo-600 pl-6 text-left italic text-lg text-gray-700 my-8">
      "{{quote}}"
      {{#if quote_author}}<footer class="text-sm text-gray-500 mt-3 not-italic">— {{quote_author}}</footer>{{/if}}
    </blockquote>{{/if}}
  </div>
</section>""",
}

_FI4 = {
    "code": "FI4",
    "category_code": "FI",
    "name": "O firmie — timeline historia",
    "description": "Historia firmy w formie timeline. Idealna dla firm z dluga tradycja.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "L",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "points", "type": "list", "label": "Kamienie milowe (skrot)", "item_fields": [
            {"id": "text", "type": "text", "label": "Punkt"},
        ]},
        {"id": "timeline", "type": "list", "label": "Kamienie milowe (pelny)", "item_fields": [
            {"id": "year", "type": "text", "label": "Rok"},
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "description", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-4xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="space-y-8 relative before:absolute before:left-4 before:top-0 before:bottom-0 before:w-0.5 before:bg-indigo-200 md:before:left-1/2">
      {{#each timeline}}<div class="relative pl-12 md:pl-0 md:grid md:grid-cols-2 md:gap-8">
        <div class="md:text-right md:pr-8">
          <span class="text-indigo-600 font-bold text-lg">{{this.year}}</span>
        </div>
        <div class="md:pl-8">
          <div class="absolute left-2.5 md:left-[calc(50%-6px)] w-3 h-3 bg-indigo-600 rounded-full mt-2"></div>
          <h3 class="font-semibold text-gray-900 mb-1">{{this.title}}</h3>
          <p class="text-sm text-gray-600">{{this.description}}</p>
        </div>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# TRESCIOWE — Oferta (2)
# ============================================================================

_OF1 = {
    "code": "OF1",
    "category_code": "OF",
    "name": "Oferta — karty uslug 3-kol",
    "description": "Grid 3 kart z uslugami, cenami i opisami. Czysty przeglad oferty.",
    "media_type": "none",
    "layout_type": "info-title-text-3",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "tiers", "type": "list", "label": "Uslugi", "item_fields": [
            {"id": "icon", "type": "icon", "label": "Ikona"},
            {"id": "name", "type": "text", "label": "Nazwa"},
            {"id": "desc", "type": "text", "label": "Opis"},
            {"id": "price", "type": "text", "label": "Cena (opcj.)"},
            {"id": "items", "type": "list", "label": "Cechy", "item_fields": [
                {"id": "text", "type": "text", "label": "Cecha"},
            ]},
        ]},
    ],
    "html_template": """<section style="padding:var(--space-section-y) 0;">
  <div style="max-width:var(--max-width);margin:0 auto;padding:0 var(--space-section-x);">
    <h2 style="font-size:var(--font-size-h2);font-weight:var(--font-weight-bold);color:var(--color-text);text-align:center;margin-bottom:var(--space-heading-mb);">{{title}}</h2>
    {{#if subtitle}}<p style="color:var(--color-text-muted);text-align:center;margin-bottom:var(--space-subheading-mb);max-width:640px;margin-left:auto;margin-right:auto;">{{subtitle}}</p>{{/if}}
    <div style="display:grid;grid-template-columns:repeat(var(--grid-columns),1fr);gap:var(--grid-gap);">
      {{#each services}}<div style="background:var(--color-bg-muted);border-radius:var(--radius-card);padding:var(--space-card);border:1px solid var(--color-border-light);box-shadow:var(--shadow-card);transition:box-shadow 0.2s;">
        <div style="width:48px;height:48px;background:var(--color-primary-light);border-radius:var(--radius-card);display:flex;align-items:center;justify-content:center;margin-bottom:1rem;color:var(--color-primary);">{{this.icon}}</div>
        <h3 style="font-size:var(--font-size-h3);font-weight:var(--font-weight-semibold);color:var(--color-text);margin-bottom:0.5rem;">{{this.title}}</h3>
        <p style="font-size:var(--font-size-small);color:var(--color-text-muted);margin-bottom:1rem;">{{this.description}}</p>
        {{#if this.price}}<div style="color:var(--color-primary);font-weight:var(--font-weight-semibold);">{{this.price}}</div>{{/if}}
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_OF2 = {
    "code": "OF2",
    "category_code": "OF",
    "name": "Oferta — lista z ikonami",
    "description": "Lista uslug z ikonami. Prosty, jednoliniowy format.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "tiers", "type": "list", "label": "Uslugi", "item_fields": [
            {"id": "icon", "type": "icon", "label": "Ikona"},
            {"id": "name", "type": "text", "label": "Nazwa"},
            {"id": "desc", "type": "text", "label": "Opis"},
            {"id": "price", "type": "text", "label": "Cena (opcj.)"},
            {"id": "items", "type": "list", "label": "Cechy", "item_fields": [
                {"id": "text", "type": "text", "label": "Cecha"},
            ]},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-4xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="space-y-6">
      {{#each services}}<div class="bg-white rounded-xl p-6 flex items-start gap-4 border border-gray-100">
        <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 flex-shrink-0">&#9679;</div>
        <div>
          <h3 class="font-semibold text-gray-900 mb-1">{{this.title}}</h3>
          <p class="text-sm text-gray-600">{{this.description}}</p>
        </div>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# TRESCIOWE — Proces (2)
# ============================================================================

_PR1 = {
    "code": "PR1",
    "category_code": "PR",
    "name": "Proces — numbered steps",
    "description": "Ponumerowane kroki procesu. Jasno pokazuje 'jak dzialamy' krok po kroku.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "features", "type": "list", "label": "Kroki", "item_fields": [
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "body", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-5xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-4">{{title}}</h2>
    {{#if subtitle}}<p class="text-gray-500 text-center mb-12 max-w-2xl mx-auto">{{subtitle}}</p>{{/if}}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each steps}}<div class="text-center">
        <div class="w-14 h-14 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">{{this.number}}</div>
        <h3 class="font-bold text-gray-900 mb-2">{{this.title}}</h3>
        <p class="text-sm text-gray-600">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_PR2 = {
    "code": "PR2",
    "category_code": "PR",
    "name": "Proces — timeline",
    "description": "Proces w formacie timeline pionowego. Wizualnie pokazuje przebieg wspolpracy.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "features", "type": "list", "label": "Kroki", "item_fields": [
            {"id": "title", "type": "text", "label": "Tytul"},
            {"id": "body", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="space-y-8 relative before:absolute before:left-4 before:top-0 before:bottom-0 before:w-0.5 before:bg-indigo-200">
      {{#each steps}}<div class="relative pl-12">
        <div class="absolute left-2.5 w-3 h-3 bg-indigo-600 rounded-full mt-1.5"></div>
        <h3 class="font-semibold text-gray-900 mb-1">{{this.title}}</h3>
        <p class="text-sm text-gray-600">{{this.description}}</p>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# TRESCIOWE — Opinie (2)
# ============================================================================

_OP1 = {
    "code": "OP1",
    "category_code": "OP",
    "name": "Opinie — karty 3 obok",
    "description": "3 karty opinii obok siebie. Klasyczny social proof z avatarami i gwiazdkami.",
    "media_type": "opinion",
    "layout_type": "opin-top-3",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "testimonials", "type": "list", "label": "Opinie", "item_fields": [
            {"id": "quote", "type": "text", "label": "Cytat"},
            {"id": "author", "type": "text", "label": "Imie i nazwisko"},
            {"id": "role", "type": "text", "label": "Stanowisko"},
            {"id": "avatar", "type": "image", "label": "Avatar"},
            {"id": "company", "type": "text", "label": "Firma"},
            {"id": "rating", "type": "number", "label": "Ocena (1-5)"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-7xl mx-auto">
    <h2 class="text-3xl font-bold text-center text-gray-900 mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each testimonials}}<div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        {{#if this.rating}}<div class="flex items-center gap-1 mb-4"><span class="text-amber-400 text-lg">&#9733;&#9733;&#9733;&#9733;&#9733;</span></div>{{/if}}
        <p class="text-gray-700 mb-6 italic">"{{this.quote}}"</p>
        <div class="flex items-center gap-3">
          {{#if this.avatar}}<img src="{{this.avatar}}" alt="{{this.author}}" class="w-12 h-12 rounded-full object-cover" />{{/if}}
          <div>
            <div class="font-semibold text-sm">{{this.author}}</div>
            <div class="text-xs text-gray-500">{{this.role}}{{#if this.company}}, {{this.company}}{{/if}}</div>
          </div>
        </div>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_OP2 = {
    "code": "OP2",
    "category_code": "OP",
    "name": "Opinie — duzy cytat centered",
    "description": "Jedna duza opinia w centrum strony. Wyroznia kluczowa rekomendacje.",
    "media_type": "opinion",
    "layout_type": "opin-top-1",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": False},
        {"id": "testimonials", "type": "list", "label": "Opinie", "item_fields": [
            {"id": "quote", "type": "text", "label": "Cytat", "max_length": 500},
            {"id": "author", "type": "text", "label": "Imie i nazwisko"},
            {"id": "role", "type": "text", "label": "Stanowisko"},
            {"id": "avatar", "type": "image", "label": "Avatar"},
            {"id": "company", "type": "text", "label": "Firma"},
            {"id": "rating", "type": "number", "label": "Ocena (1-5)"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-3xl mx-auto text-center">
    {{#if rating}}<div class="flex justify-center gap-1 mb-6"><span class="text-amber-400 text-2xl">&#9733;&#9733;&#9733;&#9733;&#9733;</span></div>{{/if}}
    <blockquote class="text-2xl text-gray-800 italic leading-relaxed mb-8">"{{quote}}"</blockquote>
    <div class="flex items-center justify-center gap-4">
      {{#if avatar}}<img src="{{avatar}}" alt="{{author}}" class="w-16 h-16 rounded-full object-cover" />{{/if}}
      <div class="text-left">
        <div class="font-bold text-gray-900">{{author}}</div>
        <div class="text-sm text-gray-500">{{role}}{{#if company}}, {{company}}{{/if}}</div>
      </div>
    </div>
  </div>
</section>""",
}

# ============================================================================
# TRESCIOWE — Zespol (2)
# ============================================================================

_ZE1 = {
    "code": "ZE1",
    "category_code": "ZE",
    "name": "Zespol — grid z avatarami",
    "description": "Grid 4 czlonkow zespolu ze zdjeciami. Pokazuje ludzi za firma.",
    "media_type": "photo",
    "layout_type": "photo-top-4",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "points", "type": "list", "label": "Czlonkowie", "item_fields": [
            {"id": "text", "type": "text", "label": "Imie, stanowisko i opis"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-4">{{title}}</h2>
    {{#if subtitle}}<p class="text-gray-500 text-center mb-12 max-w-2xl mx-auto">{{subtitle}}</p>{{/if}}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      {{#each members}}<div class="text-center">
        {{#if this.photo}}<img src="{{this.photo}}" alt="{{this.name}}" class="w-32 h-32 rounded-full mx-auto mb-4 object-cover" />{{/if}}
        <h3 class="font-semibold text-gray-900">{{this.name}}</h3>
        <p class="text-sm text-indigo-600 mb-1">{{this.role}}</p>
        {{#if this.description}}<p class="text-xs text-gray-500">{{this.description}}</p>{{/if}}
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

_ZE2 = {
    "code": "ZE2",
    "category_code": "ZE",
    "name": "Zespol — lista ze zdjeciami",
    "description": "Lista czlonkow z wiekszymi zdjeciami i biografiami. Dla zespolow do ~6 osob.",
    "media_type": "photo",
    "layout_type": "photo-full-2",
    "size": "L",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "points", "type": "list", "label": "Czlonkowie", "item_fields": [
            {"id": "text", "type": "text", "label": "Imie, stanowisko i opis"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-5xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="space-y-12">
      {{#each members}}<div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
        <div>
          {{#if this.photo}}<img src="{{this.photo}}" alt="{{this.name}}" class="w-full h-auto rounded-2xl object-cover aspect-square" />{{/if}}
        </div>
        <div class="md:col-span-2">
          <h3 class="text-xl font-bold text-gray-900 mb-1">{{this.name}}</h3>
          <p class="text-indigo-600 font-medium mb-3">{{this.role}}</p>
          <p class="text-gray-600">{{this.bio}}</p>
        </div>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# KONWERSYJNE — Cennik (1)
# ============================================================================

_CE1 = {
    "code": "CE1",
    "category_code": "CE",
    "name": "Cennik — 3 pakiety",
    "description": "Klasyczny cennik z 3 pakietami. Srodkowy wyrozniony jako 'Polecany'.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "L",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "tiers", "type": "list", "label": "Pakiety", "item_fields": [
            {"id": "name", "type": "text", "label": "Nazwa pakietu"},
            {"id": "price", "type": "text", "label": "Cena"},
            {"id": "period", "type": "text", "label": "Okres (np. /msc)"},
            {"id": "desc", "type": "text", "label": "Opis pakietu"},
            {"id": "items", "type": "list", "label": "Cechy", "item_fields": [
                {"id": "text", "type": "text", "label": "Cecha"},
            ]},
            {"id": "cta_text", "type": "text", "label": "Przycisk"},
            {"id": "highlighted", "type": "text", "label": "Wyrozniony (true/false)"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each plans}}<div class="bg-white rounded-2xl p-8 border-2 {{#if this.highlighted}}border-indigo-600 shadow-lg relative{{/if}} border-gray-100">
        {{#if this.highlighted}}<div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs font-semibold px-4 py-1 rounded-full">Polecany</div>{{/if}}
        <h3 class="text-xl font-bold text-gray-900 mb-2">{{this.name}}</h3>
        <div class="mb-6"><span class="text-4xl font-extrabold text-gray-900">{{this.price}}</span>{{#if this.period}}<span class="text-gray-500 text-sm"> {{this.period}}</span>{{/if}}</div>
        <ul class="space-y-3 mb-8 text-sm text-gray-600">
          {{#each this.features}}<li class="flex items-center gap-2"><span class="text-green-500">&#10003;</span> {{this}}</li>{{/each}}
        </ul>
        <a href="#kontakt" class="block text-center py-3 rounded-xl font-semibold {{#if this.highlighted}}bg-indigo-600 text-white hover:bg-indigo-700{{/if}} bg-gray-100 text-gray-900 hover:bg-gray-200">{{this.cta_text}}</a>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# KONWERSYJNE — CTA (3)
# ============================================================================

_CT1 = {
    "code": "CT1",
    "category_code": "CT",
    "name": "CTA — ciemne tlo",
    "description": "Wezwanie do dzialania na ciemnym tle. Wyraziste, profesjonalne.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "cta", "type": "text", "label": "Przycisk", "max_length": 30, "required": True},
        {"id": "cta_url", "type": "url", "label": "Link", "required": True},
    ],
    "html_template": """<section class="bg-gray-900 py-20 px-8">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl font-bold text-white mb-4">{{title}}</h2>
    {{#if subtitle}}<p class="text-gray-400 mb-8 text-lg">{{subtitle}}</p>{{/if}}
    <a href="{{cta_url}}" class="bg-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700 inline-block">{{cta_text}}</a>
  </div>
</section>""",
}

_CT2 = {
    "code": "CT2",
    "category_code": "CT",
    "name": "CTA — kolorowe tlo z grafika",
    "description": "CTA na kolorowym tle z grafika po prawej. Dynamiczny, przyciagajacy uwage.",
    "media_type": "photo",
    "layout_type": "photo-full-2",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "cta", "type": "text", "label": "Przycisk", "max_length": 30, "required": True},
        {"id": "cta_url", "type": "url", "label": "Link", "required": True},
        {"id": "image", "type": "image", "label": "Grafika", "required": False},
    ],
    "html_template": """<section class="bg-indigo-600 py-16 px-8">
  <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
    <div>
      <h2 class="text-3xl font-bold text-white mb-4">{{title}}</h2>
      {{#if subtitle}}<p class="text-indigo-200 mb-8 text-lg">{{subtitle}}</p>{{/if}}
      <a href="{{cta_url}}" class="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-100 inline-block">{{cta_text}}</a>
    </div>
    {{#if image}}<div>
      <img src="{{image}}" alt="" class="w-full h-auto rounded-2xl object-cover" loading="lazy" />
    </div>{{/if}}
  </div>
</section>""",
}

_CT3 = {
    "code": "CT3",
    "category_code": "CT",
    "name": "CTA — minimalistyczny",
    "description": "Prosty CTA z jednym przyciskiem. Subtelny, nieinwazyjny.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "cta", "type": "text", "label": "Przycisk", "max_length": 30, "required": True},
        {"id": "cta_url", "type": "url", "label": "Link", "required": True},
    ],
    "html_template": """<section class="bg-gray-50 py-16 px-8">
  <div class="max-w-2xl mx-auto text-center">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">{{title}}</h2>
    <a href="{{cta_url}}" class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-indigo-700 inline-block">{{cta_text}}</a>
  </div>
</section>""",
}

# ============================================================================
# KONWERSYJNE — Kontakt (1)
# ============================================================================

_KO1 = {
    "code": "KO1",
    "category_code": "KO",
    "name": "Kontakt — formularz + dane",
    "description": "Formularz kontaktowy po lewej, dane firmy po prawej. Standardowa sekcja kontaktu.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "L",
    "slots_definition": [
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "address", "type": "text", "label": "Adres", "required": False},
        {"id": "phone", "type": "text", "label": "Telefon", "required": False},
        {"id": "email", "type": "text", "label": "Email", "required": False},
        {"id": "form_fields", "type": "list", "label": "Pola formularza", "item_fields": [
            {"id": "label", "type": "text", "label": "Etykieta"},
            {"id": "type", "type": "text", "label": "Typ"},
        ]},
        {"id": "map_embed", "type": "text", "label": "Google Maps embed URL", "required": False},
    ],
    "html_template": """<section class="bg-white py-20 px-8" id="kontakt">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
      <div>
        <form class="space-y-4">
          {{#each form_fields}}<div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{this.label}}</label>
            <input type="{{this.type}}" class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:border-indigo-400 outline-none" />
          </div>{{/each}}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Wiadomosc</label>
            <textarea rows="4" class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:border-indigo-400 outline-none resize-none"></textarea>
          </div>
          <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-indigo-700">Wyslij wiadomosc</button>
        </form>
      </div>
      <div class="space-y-6">
        {{#if address}}<div>
          <h3 class="font-semibold text-gray-900 mb-1">Adres</h3>
          <p class="text-gray-600">{{address}}</p>
        </div>{{/if}}
        {{#if phone}}<div>
          <h3 class="font-semibold text-gray-900 mb-1">Telefon</h3>
          <p class="text-gray-600">{{phone}}</p>
        </div>{{/if}}
        {{#if email}}<div>
          <h3 class="font-semibold text-gray-900 mb-1">Email</h3>
          <p class="text-gray-600">{{email}}</p>
        </div>{{/if}}
        {{#if map_embed}}<div class="rounded-xl overflow-hidden h-64">
          <iframe src="{{map_embed}}" width="100%" height="100%" style="border:0" allowfullscreen loading="lazy"></iframe>
        </div>{{/if}}
      </div>
    </div>
  </div>
</section>""",
}

# ============================================================================
# WSPIERAJACE — FAQ (1)
# ============================================================================

_FA1 = {
    "code": "FA1",
    "category_code": "FA",
    "name": "FAQ — accordion",
    "description": "Pytania i odpowiedzi w formacie listy. SEO-friendly, buduje zaufanie.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "body", "type": "text", "label": "Podtytul", "max_length": 200, "required": False},
        {"id": "items", "type": "list", "label": "Pytania", "item_fields": [
            {"id": "question", "type": "text", "label": "Pytanie"},
            {"id": "answer", "type": "text", "label": "Odpowiedz"},
        ]},
    ],
    "html_template": """<section class="bg-gray-50 py-20 px-8">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="space-y-4">
      {{#each items}}<details class="bg-white rounded-xl border border-gray-200 group">
        <summary class="flex items-center justify-between p-6 cursor-pointer font-semibold text-gray-900">{{this.question}}<span class="text-gray-400 text-xl ml-4">+</span></summary>
        <div class="px-6 pb-6 text-gray-600 text-sm">{{this.answer}}</div>
      </details>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# WSPIERAJACE — Realizacje (1)
# ============================================================================

_RE1 = {
    "code": "RE1",
    "category_code": "RE",
    "name": "Realizacje — grid kart",
    "description": "Grid projektow/realizacji ze zdjeciami i opisami. Portfolio firmowe.",
    "media_type": "photo",
    "layout_type": "photo-top-3",
    "size": "L",
    "slots_definition": [
        {"id": "eyebrow", "type": "text", "label": "Nad-tytul", "max_length": 60, "required": False},
        {"id": "heading", "type": "text", "label": "Tytul", "max_length": 80, "required": True},
        {"id": "testimonials", "type": "list", "label": "Realizacje", "item_fields": [
            {"id": "quote", "type": "text", "label": "Opis realizacji"},
            {"id": "author", "type": "text", "label": "Klient / projekt"},
            {"id": "role", "type": "text", "label": "Wyniki"},
        ]},
    ],
    "html_template": """<section class="bg-white py-20 px-8">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-12">{{title}}</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {{#each cases}}<div class="bg-gray-50 rounded-2xl overflow-hidden border border-gray-100">
        {{#if this.image}}<img src="{{this.image}}" alt="{{this.title}}" class="w-full h-48 object-cover" loading="lazy" />{{/if}}
        <div class="p-6">
          <h3 class="font-bold text-gray-900 mb-2">{{this.title}}</h3>
          <p class="text-sm text-gray-600 mb-3">{{this.description}}</p>
          {{#if this.results}}<p class="text-sm text-indigo-600 font-medium">{{this.results}}</p>{{/if}}
        </div>
      </div>{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# WSPIERAJACE — Loga klientow (1)
# ============================================================================

_LO1 = {
    "code": "LO1",
    "category_code": "LO",
    "name": "Loga klientow — 1 rzad",
    "description": "Rzad log klientow/partnerow. Szybki social proof bez zajmowania miejsca.",
    "media_type": "logo",
    "layout_type": "logo-1",
    "size": "S",
    "slots_definition": [
        {"id": "title", "type": "text", "label": "Tytul", "max_length": 80, "required": False},
        {"id": "logos", "type": "list", "label": "Loga", "item_fields": [
            {"id": "image", "type": "image", "label": "Logo"},
            {"id": "name", "type": "text", "label": "Nazwa firmy"},
        ]},
    ],
    "html_template": """<section class="bg-white py-12 px-8">
  <div class="max-w-6xl mx-auto">
    {{#if title}}<p class="text-sm text-gray-400 text-center mb-8 uppercase tracking-wide font-medium">{{title}}</p>{{/if}}
    <div class="flex items-center justify-center gap-12 flex-wrap">
      {{#each logos}}<img src="{{this.image}}" alt="{{this.name}}" class="h-8 w-auto grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all" />{{/each}}
    </div>
  </div>
</section>""",
}

# ============================================================================
# WSPIERAJACE — Statystyki (1)
# ============================================================================

_ST1 = {
    "code": "ST1",
    "category_code": "ST",
    "name": "Statystyki — duze liczby 4-kol",
    "description": "4 duze liczby w rzedzie. Szybki pokaz skali firmy (klienci, projekty, lata).",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "S",
    "slots_definition": [
        {"id": "stats", "type": "list", "label": "Statystyki", "item_fields": [
            {"id": "value", "type": "text", "label": "Wartosc"},
            {"id": "label", "type": "text", "label": "Opis"},
        ]},
    ],
    "html_template": """<section class="bg-gray-900 text-white py-16 px-8">
  <div class="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
    {{#each stats}}<div>
      <div class="text-4xl font-extrabold mb-1">{{this.value}}</div>
      <div class="text-sm text-gray-400">{{this.label}}</div>
    </div>{{/each}}
  </div>
</section>""",
}

# ============================================================================
# WSPIERAJACE — Stopka (1)
# ============================================================================

_FO1 = {
    "code": "FO1",
    "category_code": "FO",
    "name": "Stopka — 4 kolumny + copyright",
    "description": "Klasyczna stopka z 4 kolumnami linkow, logo i copyright.",
    "media_type": "none",
    "layout_type": "text-only",
    "size": "M",
    "slots_definition": [
        {"id": "logo_url", "type": "image", "label": "Logo obrazek", "required": False},
        {"id": "logo", "type": "text", "label": "Nazwa firmy", "required": True},
        {"id": "desc", "type": "text", "label": "Krotki opis", "max_length": 200, "required": False},
        {"id": "cols", "type": "list", "label": "Kolumny linkow", "item_fields": [
            {"id": "title", "type": "text", "label": "Tytul kolumny"},
            {"id": "links", "type": "list", "label": "Linki", "item_fields": [
                {"id": "text", "type": "text", "label": "Tekst linku"},
            ]},
        ]},
        {"id": "copyright", "type": "text", "label": "Copyright", "required": True},
        {"id": "socials", "type": "list", "label": "Social media", "item_fields": [
            {"id": "name", "type": "text", "label": "Nazwa"},
            {"id": "url", "type": "url", "label": "Link"},
        ]},
    ],
    "html_template": """<footer class="bg-gray-950 text-gray-400 py-16 px-8">
  <div class="max-w-7xl mx-auto">
    <div class="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
      <div class="col-span-2 md:col-span-1">
        <div class="flex items-center gap-2 mb-4">
          {{#if logo}}<img src="{{logo}}" alt="{{logo_text}}" class="h-8 w-auto" />{{/if}}
          <span class="text-white font-bold text-lg">{{logo_text}}</span>
        </div>
        {{#if description}}<p class="text-sm">{{description}}</p>{{/if}}
        {{#if socials}}<div class="flex gap-4 mt-4">
          {{#each socials}}<a href="{{this.url}}" class="hover:text-white transition-colors text-sm">{{this.name}}</a>{{/each}}
        </div>{{/if}}
      </div>
      {{#each columns}}<div>
        <h4 class="text-white font-semibold text-sm mb-4">{{this.title}}</h4>
        <ul class="space-y-2 text-sm">
          {{#each this.links}}<li><a href="#" class="hover:text-white transition-colors">{{this}}</a></li>{{/each}}
        </ul>
      </div>{{/each}}
    </div>
    <div class="border-t border-gray-800 pt-8 text-sm text-center">
      {{copyright}}
    </div>
  </div>
</footer>""",
}

# ============================================================================
# MASTER LIST
# ============================================================================

BLOCK_SEEDS: list[dict] = [
    # Nawigacja
    _NA1, _NA2, _NA3,
    # Hero
    _HE1, _HE2, _HE3, _HE4, _HE5,
    # Perswazyjne — Problem
    _PB1, _PB2, _PB3,
    # Perswazyjne — Rozwiazanie
    _RO1, _RO2,
    # Perswazyjne — Korzysci
    _KR1, _KR2,
    # Perswazyjne — Cechy
    _CF1, _CF2,
    # Perswazyjne — Obiekcje
    _OB1,
    # Tresciowe — O firmie
    _FI1, _FI2, _FI3, _FI4,
    # Tresciowe — Oferta
    _OF1, _OF2,
    # Tresciowe — Proces
    _PR1, _PR2,
    # Tresciowe — Opinie
    _OP1, _OP2,
    # Tresciowe — Zespol
    _ZE1, _ZE2,
    # Konwersyjne — Cennik
    _CE1,
    # Konwersyjne — CTA
    _CT1, _CT2, _CT3,
    # Konwersyjne — Kontakt
    _KO1,
    # Wspierajace
    _FA1, _RE1, _LO1, _ST1, _FO1,
]


async def seed_block_templates(db: AsyncSession) -> int:
    """Seed block templates (idempotent). Returns number created."""
    created = 0
    for block_data in BLOCK_SEEDS:
        result = await db.execute(
            select(BlockTemplate).where(BlockTemplate.code == block_data["code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Update template if changed
            for k, v in block_data.items():
                setattr(existing, k, v)
        else:
            db.add(BlockTemplate(**block_data))
            created += 1
    await db.commit()
    return created
