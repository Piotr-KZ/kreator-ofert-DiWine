"""
AI prompts for offer module — email parsing + text personalization.
"""

PARSE_EMAIL_PROMPT = """Przeanalizuj email od klienta z zapytaniem o prezenty firmowe.
Wyciągnij WSZYSTKIE informacje i zwróć JSON.

WAŻNE ZASADY:
1. company_name: TYLKO nazwa firmy BEZ formy prawnej (np. "FirmaTech" a nie "FirmaTech Sp. z o.o.")
2. legal_form: forma prawna OSOBNO — MUSI być jedna z: "Sp. z o.o.", "S.A.", "Sp.j.", "Sp.k.", "Sp. komandytowa", "Spółka jawna", "JDG", "S.C.", "Fundacja", "Stowarzyszenie" lub null
3. website: ZAWSZE spróbuj wyciągnąć stronę www:
   - Jeśli jest podana wprost — użyj jej
   - Jeśli jest email firmowy (np. anna@firmatech.pl) — domena to strona www → "https://firmatech.pl"
   - NIE twórz strony z domen popularnych (gmail.com, wp.pl, onet.pl, o2.pl, interia.pl, yahoo.com, outlook.com, hotmail.com)
4. Adres z emaila → wpisz w client.address (to adres korespondencyjny/biura)
5. Adres dostawy (delivery) — rozbij na osobne pola. WAŻNE:
   - Jeśli adres dostawy = adres firmy z emaila → recipient_name = osoba kontaktowa, company_name = nazwa firmy
   - Jeśli adres dostawy jest INNY niż adres firmy → wypełnij oddzielne pola
   - Jeśli adres dostawy jest podany bez pełnych danych (np. samo "Warszawa") → dodaj do missing_info np. "Potrzebny pełny adres dostawy (ulica, numer)"
   - Jeśli dostawa ma iść do INNEJ firmy niż zamawiająca → dodaj do missing_info: "Dostawa do innej firmy — potrzebne pełne dane odbiorcy (nazwa firmy, osoba kontaktowa, adres)"
6. Rozdziel ulicę od numeru: "ul. Marszałkowska 10" → street: "Marszałkowska", number: "10"
7. Jeśli adres dostawy nie jest podany wcale → dodaj do missing_info: "Brak adresu dostawy"

Email:
---
{email_text}
---

Zwróć JSON:
{{
  "client": {{
    "company_name": "nazwa firmy BEZ formy prawnej lub null",
    "legal_form": "Sp. z o.o.|S.A.|Sp.j.|Sp.k.|JDG|S.C.|null",
    "contact_person": "imię i nazwisko lub null",
    "contact_role": "stanowisko lub null",
    "email": "adres email lub null",
    "phone": "telefon lub null",
    "website": "https://domena.pl lub null",
    "nip": "NIP jeśli podany lub null",
    "address": {{
      "street": "ulica BEZ numeru lub null",
      "number": "numer budynku/lokalu lub null",
      "city": "miasto lub null",
      "postal_code": "kod pocztowy lub null"
    }}
  }},
  "order": {{
    "quantity": null,
    "budget_per_unit": null,
    "occasion": "christmas|easter|birthday|universal|other|null",
    "deadline": "YYYY-MM-DD lub null"
  }},
  "delivery": {{
    "recipient_name": "imię i nazwisko odbiorcy lub null",
    "company_name": "nazwa firmy odbiorcy lub null",
    "street": "ulica BEZ numeru lub null",
    "number": "numer lub null",
    "city": "miasto lub null",
    "postal_code": "kod pocztowy lub null"
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

FIND_WEBSITE_PROMPT = """Podaj adres strony internetowej firmy "{company_name}" (polska firma).

Jeśli znasz lub potrafisz wywnioskować adres strony www tej firmy, podaj go.
Jeśli nie znasz — zwróć null.

Zwróć JSON: {{"website": "https://domena.pl" lub null}}
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
