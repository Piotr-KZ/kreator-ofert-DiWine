"""
Integrations catalog — static data for 9 categories, 30+ integrations.
"""

INTEGRATIONS_CATALOG = [
    {
        "category": "analytics",
        "category_name": "Analityka i monitoring",
        "items": [
            {"provider": "google_analytics", "name": "Google Analytics", "description": "Sledz odwiedzajacych, zrodla ruchu i konwersje", "difficulty": "1-klik", "price": "Darmowy", "fields": [{"id": "tracking_id", "label": "Measurement ID", "placeholder": "G-XXXXXXXXXX"}]},
            {"provider": "hotjar", "name": "Hotjar", "description": "Heatmapy — zobacz gdzie klienci klikaja", "difficulty": "prosty", "price": "Darmowy do 35 sesji/dzien", "fields": [{"id": "site_id", "label": "Site ID", "placeholder": "1234567"}]},
            {"provider": "clarity", "name": "Microsoft Clarity", "description": "Darmowe nagrania sesji i mapy ciepla", "difficulty": "1-klik", "price": "Darmowy", "fields": [{"id": "project_id", "label": "Project ID", "placeholder": "abcdefghij"}]},
            {"provider": "plausible", "name": "Plausible", "description": "Lekka, RODO-friendly alternatywa Analytics", "difficulty": "1-klik", "price": "Od 9 EUR/mies", "fields": [{"id": "domain", "label": "Domena", "placeholder": "twojafirma.pl"}]},
        ],
    },
    {
        "category": "email_marketing",
        "category_name": "Email marketing",
        "items": [
            {"provider": "mailchimp", "name": "Mailchimp", "description": "Zbieraj leady i wysylaj newslettery", "difficulty": "prosty", "price": "Darmowy do 500 kontaktow", "fields": [{"id": "api_key", "label": "API Key"}, {"id": "list_id", "label": "List ID"}], "v2": True},
            {"provider": "getresponse", "name": "GetResponse", "description": "Polskie narzedzie do email marketingu", "difficulty": "prosty", "price": "Od 59 zl/mies", "fields": [{"id": "api_key", "label": "API Key"}], "v2": True},
            {"provider": "mailerlite", "name": "MailerLite", "description": "Prosty email marketing z automatyzacjami", "difficulty": "prosty", "price": "Darmowy do 1000 sub.", "fields": [{"id": "api_key", "label": "API Key"}], "v2": True},
        ],
    },
    {
        "category": "crm",
        "category_name": "CRM i sprzedaz",
        "items": [
            {"provider": "hubspot", "name": "HubSpot", "description": "Darmowy CRM — leady z formularzy", "difficulty": "prosty", "price": "Darmowy", "fields": [], "v2": True},
            {"provider": "pipedrive", "name": "Pipedrive", "description": "CRM dla handlowcow — pipeline", "difficulty": "prosty", "price": "Od 14 EUR/mies", "fields": [], "v2": True},
        ],
    },
    {
        "category": "chat",
        "category_name": "Chat i obsluga klienta",
        "items": [
            {"provider": "tidio", "name": "Tidio", "description": "Chat na stronie w czasie rzeczywistym", "difficulty": "1-klik", "price": "Darmowy", "fields": [{"id": "public_key", "label": "Public Key"}]},
            {"provider": "crisp", "name": "Crisp", "description": "Chat + baza wiedzy + CRM", "difficulty": "prosty", "price": "Darmowy do 2 operatorow", "fields": [{"id": "website_id", "label": "Website ID"}]},
            {"provider": "livechat", "name": "LiveChat", "description": "Profesjonalny chat dla firm", "difficulty": "prosty", "price": "Od 20 USD/mies", "fields": [{"id": "license_id", "label": "License ID"}]},
        ],
    },
    {
        "category": "social_ads",
        "category_name": "Social media i reklama",
        "items": [
            {"provider": "fb_pixel", "name": "Facebook Pixel", "description": "Konwersje z reklam Facebook/Instagram", "difficulty": "prosty", "price": "Darmowy", "fields": [{"id": "pixel_id", "label": "Pixel ID"}]},
            {"provider": "linkedin_insight", "name": "LinkedIn Insight Tag", "description": "Remarketing B2B na LinkedIn", "difficulty": "prosty", "price": "Darmowy", "fields": [{"id": "partner_id", "label": "Partner ID"}]},
            {"provider": "google_ads", "name": "Google Ads", "description": "Konwersje z Google Ads", "difficulty": "prosty", "price": "Darmowy tag", "fields": [{"id": "conversion_id", "label": "Conversion ID"}, {"id": "conversion_label", "label": "Conversion Label"}]},
        ],
    },
    {
        "category": "reservations",
        "category_name": "Rezerwacje i kalendarze",
        "items": [
            {"provider": "calendly", "name": "Calendly", "description": "Klienci sami umawiaja spotkania", "difficulty": "1-klik", "price": "Darmowy", "fields": [{"id": "embed_url", "label": "Link do kalendarza"}]},
            {"provider": "cal_com", "name": "Cal.com", "description": "Open-source alternatywa Calendly", "difficulty": "prosty", "price": "Darmowy", "fields": [{"id": "embed_url", "label": "Link"}]},
        ],
    },
    {
        "category": "automation",
        "category_name": "Automatyzacja",
        "items": [
            {"provider": "autoflow", "name": "AutoFlow", "description": "Nasza platforma — 130+ systemow w automatyczne procesy", "difficulty": "1-klik", "price": "W pakiecie", "fields": [{"id": "api_key", "label": "API Key"}]},
            {"provider": "zapier", "name": "Zapier", "description": "5000+ aplikacji bez kodowania", "difficulty": "prosty", "price": "Darmowy do 100 zadan", "fields": [{"id": "webhook_url", "label": "Webhook URL"}]},
            {"provider": "make", "name": "Make", "description": "Zaawansowana automatyzacja wizualna", "difficulty": "zaawansowany", "price": "Darmowy do 1000 op.", "fields": [{"id": "api_key", "label": "API Key"}, {"id": "webhook_url", "label": "Webhook URL"}]},
        ],
    },
    {
        "category": "payments",
        "category_name": "Platnosci",
        "items": [
            {"provider": "stripe", "name": "Stripe", "description": "Platnosci karta na stronie", "difficulty": "prosty", "price": "1.5% + 1 zl", "fields": [{"id": "publishable_key", "label": "Publishable Key"}, {"id": "secret_key", "label": "Secret Key"}], "v2": True},
            {"provider": "p24", "name": "Przelewy24", "description": "Polskie platnosci — BLIK, przelewy", "difficulty": "prosty", "price": "1.2-1.9%", "fields": [{"id": "merchant_id", "label": "Merchant ID"}, {"id": "crc_key", "label": "CRC Key"}], "v2": True},
        ],
    },
    {
        "category": "other",
        "category_name": "Inne",
        "items": [
            {"provider": "gtm", "name": "Google Tag Manager", "description": "Zarzadzaj tagami z jednego miejsca", "difficulty": "prosty", "price": "Darmowy", "fields": [{"id": "container_id", "label": "Container ID (GTM-XXXXXXX)"}]},
        ],
    },
]

AUTOMATION_TEMPLATES = [
    {
        "group": "forms_leads",
        "group_name": "Formularze i leady",
        "templates": [
            {"id": "lead_welcome_email", "name": "Nowy lead -> wyslij email powitalny", "description": "Automatycznie wyslij email po zgloszeniu", "native": True},
            {"id": "lead_mailchimp", "name": "Nowy lead -> dodaj do Mailchimp", "description": "Zapisz kontakt w liscie Mailchimp", "native": False},
            {"id": "lead_notification", "name": "Nowy lead -> powiadomienie na email", "description": "Dostaniesz powiadomienie o nowym zgloszeniu", "native": True},
            {"id": "lead_hubspot", "name": "Nowy lead -> dodaj do HubSpot CRM", "description": "Automatycznie dodaj kontakt do CRM", "native": False},
            {"id": "lead_slack", "name": "Nowy lead -> powiadomienie Slack", "description": "Powiadomienie na kanale Slack", "native": False},
        ],
    },
    {
        "group": "newsletter",
        "group_name": "Newsletter",
        "templates": [
            {"id": "newsletter_welcome_sequence", "name": "Zapis -> sekwencja 3 maili powitalnych", "description": "3 emaile w 7 dni po zapisie", "native": False},
            {"id": "newsletter_mailchimp_tag", "name": "Zapis -> tag w Mailchimp", "description": "Automatyczne tagowanie subskrybentow", "native": False},
        ],
    },
    {
        "group": "reservations",
        "group_name": "Rezerwacje",
        "templates": [
            {"id": "reservation_email", "name": "Nowa rezerwacja Calendly -> email potwierdzenie", "description": "Wyslij potwierdzenie spotkania", "native": False},
            {"id": "reservation_gcal", "name": "Nowa rezerwacja -> Google Calendar", "description": "Dodaj wydarzenie do kalendarza", "native": False},
        ],
    },
]


def get_catalog() -> list[dict]:
    """Return full integrations catalog."""
    return INTEGRATIONS_CATALOG


def get_automation_templates() -> list[dict]:
    """Return automation templates."""
    return AUTOMATION_TEMPLATES


def get_category(code: str) -> dict | None:
    """Return specific category by code."""
    return next((c for c in INTEGRATIONS_CATALOG if c["category"] == code), None)
