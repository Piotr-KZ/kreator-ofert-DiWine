"""
AI prompts for offer module — email parsing + text personalization.
"""

PARSE_EMAIL_PROMPT = """Przeanalizuj email od klienta z zapytaniem o prezenty firmowe.
Wyciągnij WSZYSTKIE informacje i zwróć JSON.

Email:
---
{email_text}
---

Zwróć JSON:
{{
  "client": {{
    "company_name": "nazwa firmy lub null",
    "contact_person": "imię i nazwisko lub null",
    "contact_role": "stanowisko lub null",
    "email": "adres email lub null",
    "phone": "telefon lub null",
    "website": "strona www lub null",
    "nip": "NIP jeśli podany lub null"
  }},
  "order": {{
    "quantity": null,
    "budget_per_unit": null,
    "occasion": "christmas|easter|birthday|universal|other|null",
    "deadline": "YYYY-MM-DD lub null",
    "delivery_address": "adres lub null"
  }},
  "requested_items": ["życzenie 1", "życzenie 2"],
  "specific_products": ["konkretny produkt"],
  "vague_requests": ["nieprecyzyjne życzenie"],
  "personalization": {{
    "logo_on_packaging": true|false|null,
    "engraving_on_cork": true|false|null,
    "logo_attached": true|false
  }},
  "missing_info": ["brakująca informacja"],
  "confidence": 85
}}

Odpowiedz WYŁĄCZNIE poprawnym JSON-em.
"""

PERSONALIZE_TEXT_PROMPT = """Spersonalizuj tekst ofertowy.

Tekst bazowy:
---
{template_text}
---

Dane: firma={company_name}, kontakt={contact_person} ({contact_role}),
okazja={occasion_name}, ilość={quantity}, zestawy={sets_summary}

ZASADY:
- Wypełnij placeholdery
- Możesz lekko dopasować ton, dodać 1 zdanie o branży
- NIE zmieniaj głównego przekazu, NIE dodawaj cen/obietnic
- Zachowaj zbliżoną długość

Zwróć JSON: {{"personalized_text": "tekst"}}
Odpowiedz WYŁĄCZNIE poprawnym JSON-em.
"""
