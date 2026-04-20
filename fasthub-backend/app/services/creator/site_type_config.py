"""
Site Type Config — single source of truth for per-type customization.
Brief 42: centralizes all per-site-type logic (blocks, prompts, readiness, style).
"""

from dataclasses import dataclass, field


@dataclass
class SiteTypeConfig:
    """Complete configuration for a single site type."""

    site_type: str
    label: str
    category: str  # "firma" | "osoba"

    # Block recommendations
    recommended_blocks: list[str]
    min_sections: int = 4
    max_sections: int = 14
    allowed_block_categories: list[str] = field(default_factory=list)  # empty = all

    # AI prompt hints per stage
    prompt_hints: dict[str, str] = field(default_factory=dict)

    # Readiness overrides
    readiness_skip_checks: list[str] = field(default_factory=list)
    readiness_modify_checks: dict[str, dict] = field(default_factory=dict)

    # Config defaults (Step 7)
    config_defaults: dict = field(default_factory=dict)

    # Style presets (Step 3)
    style_presets: list[dict] = field(default_factory=list)

    # Brief sections visible (migrated from frontend getSectionsForType)
    brief_sections: list[str] = field(default_factory=list)

    # Brief content options visible in S8 "Co ma zawierac strona?" (empty = all)
    brief_content: list[str] = field(default_factory=list)


# ============================================================================
# Configurations per site type
# ============================================================================

SITE_TYPE_CONFIGS: dict[str, SiteTypeConfig] = {
    # ─── FIRMA ───

    "firmowa": SiteTypeConfig(
        site_type="firmowa",
        label="Strona firmowa",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "OF", "RE", "OP", "FA", "CT", "KO", "FO"],
        min_sections=6,
        max_sections=14,
        prompt_hints={
            "generate_structure": (
                "Pełna strona firmowa. Ścieżka perswazji: Hero → O firmie → Oferta → "
                "Realizacje → Opinie → FAQ → CTA → Kontakt. Uwzględnij sekcje budujące zaufanie."
            ),
            "generate_section_content": (
                "Ton profesjonalny, dopasowany do briefu. Podkreślaj doświadczenie i kompetencje firmy."
            ),
            "validate_consistency": (
                "Sprawdź kompletność prezentacji firmy — oferta, zespół, realizacje."
            ),
        },
        style_presets=[
            {"id": "corporate-navy", "label": "Korporacyjny granat", "colors": ["#1E3A5F", "#64748B", "#E0E7FF"]},
            {"id": "professional-indigo", "label": "Profesjonalny indigo", "colors": ["#4F46E5", "#64748B", "#E0E7FF"]},
        ],
        brief_sections=["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"],
    ),

    "korporacyjna": SiteTypeConfig(
        site_type="korporacyjna",
        label="Korporacyjna",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "OF", "ZE", "ST", "OP", "FA", "CT", "KO", "FO"],
        min_sections=8,
        max_sections=14,
        prompt_hints={
            "generate_structure": (
                "Duża firma, wiele działów. Rozbudowana struktura: Hero → O firmie → "
                "Oferta → Zespół → Statystyki → Opinie → FAQ → CTA → Kontakt. "
                "Więcej sekcji, profesjonalny układ."
            ),
            "generate_section_content": (
                "Ton korporacyjny, formalny. Liczby i dane. Skala działalności, stabilność."
            ),
            "validate_consistency": (
                "Korporacja — sprawdź czy są sekcje zespołu, statystyk, pełnej oferty."
            ),
        },
        style_presets=[
            {"id": "corp-dark", "label": "Korporacyjny ciemny", "colors": ["#0F172A", "#475569", "#F1F5F9"]},
            {"id": "corp-blue", "label": "Korporacyjny niebieski", "colors": ["#1E40AF", "#64748B", "#DBEAFE"]},
        ],
        brief_sections=["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"],
    ),

    "blog": SiteTypeConfig(
        site_type="blog",
        label="Blog firmowy",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "RE", "CT", "KO", "FO"],
        min_sections=4,
        max_sections=10,
        allowed_block_categories=["NA", "HE", "FI", "RE", "CT", "KO", "FO", "OP", "GA", "FA"],
        prompt_hints={
            "generate_structure": (
                "Blog firmowy — czytelność i treść. Hero z nagłówkiem bloga → O blogu/autorze → "
                "Wyróżnione artykuły → CTA (subskrypcja) → Kontakt. Prosta struktura."
            ),
            "generate_section_content": (
                "Ton publicystyczny, angażujący. Skupienie na wartości merytorycznej."
            ),
            "validate_consistency": (
                "Blog — sprawdź czy jest jasny temat, kategorie, CTA subskrypcji."
            ),
        },
        readiness_skip_checks=["schema_person"],
        style_presets=[
            {"id": "blog-clean", "label": "Czysty czytelny", "colors": ["#111827", "#6B7280", "#FFFFFF"]},
            {"id": "blog-warm", "label": "Ciepły blogowy", "colors": ["#92400E", "#78716C", "#FFFBEB"]},
        ],
        brief_sections=["s1", "s2", "s5", "s7", "s8", "s11"],
    ),

    "firmowa-blog": SiteTypeConfig(
        site_type="firmowa-blog",
        label="Firma + Blog",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "OF", "RE", "OP", "FA", "CT", "KO", "FO"],
        min_sections=7,
        max_sections=14,
        prompt_hints={
            "generate_structure": (
                "Strona firmowa z sekcją blogową. Pełna prezentacja firmy + sekcja artykułów. "
                "Hero → O firmie → Oferta → Blog/Artykuły → Opinie → FAQ → CTA → Kontakt."
            ),
            "generate_section_content": (
                "Ton profesjonalny z elementami edukacyjnymi. Firma + ekspertyza."
            ),
            "validate_consistency": (
                "Firma + Blog — sprawdź pełność oferty i sekcję artykułów."
            ),
        },
        style_presets=[
            {"id": "corporate-navy", "label": "Korporacyjny granat", "colors": ["#1E3A5F", "#64748B", "#E0E7FF"]},
            {"id": "professional-indigo", "label": "Profesjonalny indigo", "colors": ["#4F46E5", "#64748B", "#E0E7FF"]},
        ],
        brief_sections=["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"],
    ),

    "korporacyjna-blog": SiteTypeConfig(
        site_type="korporacyjna-blog",
        label="Korporacja + Blog",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "OF", "ZE", "ST", "RE", "OP", "FA", "CT", "KO", "FO"],
        min_sections=8,
        max_sections=14,
        prompt_hints={
            "generate_structure": (
                "Korporacja z bazą wiedzy. Rozbudowana struktura + sekcja artykułów. "
                "Hero → O firmie → Oferta → Zespół → Statystyki → Artykuły → Opinie → FAQ → CTA → Kontakt."
            ),
            "generate_section_content": (
                "Ton korporacyjny z elementami thought leadership. Dane + ekspertyza."
            ),
            "validate_consistency": (
                "Korporacja + Blog — sprawdź zespół, statystyki, bazę wiedzy."
            ),
        },
        style_presets=[
            {"id": "corp-dark", "label": "Korporacyjny ciemny", "colors": ["#0F172A", "#475569", "#F1F5F9"]},
            {"id": "corp-blue", "label": "Korporacyjny niebieski", "colors": ["#1E40AF", "#64748B", "#DBEAFE"]},
        ],
        brief_sections=["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"],
    ),

    "lp-produkt": SiteTypeConfig(
        site_type="lp-produkt",
        label="LP produktowa",
        category="firma",
        recommended_blocks=["NA", "HE", "PB", "RO", "CF", "KR", "OP", "OB", "CT", "FO"],
        min_sections=7,
        max_sections=12,
        allowed_block_categories=["NA", "HE", "PB", "RO", "CF", "KR", "OP", "OB", "CT", "FO", "ST", "GA", "CE"],
        prompt_hints={
            "generate_structure": (
                "Landing page produktowa — agresywna konwersja. Schemat: Hero z CTA → Problem → "
                "Rozwiązanie (produkt) → Cechy → Korzyści → Opinie → Obiekcje → CTA finalne. "
                "CTA co 3 sekcje. Każda sekcja prowadzi do konwersji."
            ),
            "generate_section_content": (
                "Język perswazyjny, konwersja. Krótkie zdania, mocne czasowniki. "
                "Korzyści > Cechy. Każda sekcja kończy micro-CTA."
            ),
            "validate_consistency": (
                "LP produktowa — sprawdź ścieżkę konwersji. Problem → rozwiązanie? CTA widoczny?"
            ),
        },
        readiness_skip_checks=["schema_person"],
        readiness_modify_checks={
            "cta_present": {
                "min_cta_count": 2,
                "fail_message": "Landing page wymaga minimum 2 przycisków CTA (u góry i na dole)",
            },
        },
        config_defaults={
            "forms": {"send_email_notification": True},
            "legal": {"cookie_banner": {"enabled": True, "style": "bar"}},
        },
        style_presets=[
            {"id": "conversion-orange", "label": "Konwersyjny pomarańcz", "colors": ["#EA580C", "#78716C", "#FFF7ED"]},
            {"id": "trust-blue", "label": "Zaufanie niebieski", "colors": ["#2563EB", "#475569", "#EFF6FF"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "Produkty / katalog", "Cennik", "Opinie klientow",
            "FAQ / pytania", "Kontakt / formularz", "Proces / jak dzialamy",
            "Korzysci / dlaczego my",
        ],
    ),

    "lp-usluga": SiteTypeConfig(
        site_type="lp-usluga",
        label="LP usługowa",
        category="firma",
        recommended_blocks=["NA", "HE", "PB", "RO", "PR", "KR", "OP", "FA", "CT", "FO"],
        min_sections=7,
        max_sections=12,
        allowed_block_categories=["NA", "HE", "PB", "RO", "PR", "KR", "OP", "FA", "OB", "CT", "FO", "ST", "CE"],
        prompt_hints={
            "generate_structure": (
                "Landing page usługowa — konwersja na usługę. Hero z CTA → Problem → "
                "Rozwiązanie (usługa) → Proces → Korzyści → Opinie → FAQ → CTA. "
                "Pokaż proces współpracy krok po kroku."
            ),
            "generate_section_content": (
                "Język perswazyjny. Pokaż wartość usługi, nie cechy. "
                "Proces: jak to wygląda krok po kroku. Buduj zaufanie."
            ),
            "validate_consistency": (
                "LP usługowa — sprawdź czy jest jasny proces, korzyści, CTA."
            ),
        },
        readiness_skip_checks=["schema_person"],
        readiness_modify_checks={
            "cta_present": {
                "min_cta_count": 2,
                "fail_message": "Landing page wymaga minimum 2 przycisków CTA (u góry i na dole)",
            },
        },
        config_defaults={
            "forms": {"send_email_notification": True},
            "legal": {"cookie_banner": {"enabled": True, "style": "bar"}},
        },
        style_presets=[
            {"id": "service-teal", "label": "Usługowy morski", "colors": ["#0D9488", "#64748B", "#CCFBF1"]},
            {"id": "trust-blue", "label": "Zaufanie niebieski", "colors": ["#2563EB", "#475569", "#EFF6FF"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "Oferta uslug", "Cennik", "Opinie klientow",
            "FAQ / pytania", "Kontakt / formularz", "Proces / jak dzialamy",
            "Korzysci / dlaczego my",
        ],
    ),

    "lp-wydarzenie": SiteTypeConfig(
        site_type="lp-wydarzenie",
        label="LP wydarzenie",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "PR", "ZE", "GA", "CT", "KO", "FO"],
        min_sections=6,
        max_sections=12,
        allowed_block_categories=["NA", "HE", "FI", "PR", "ZE", "GA", "CT", "KO", "FO", "OP", "ST", "FA"],
        prompt_hints={
            "generate_structure": (
                "Landing page eventowa — rejestracja na wydarzenie. Hero z datą i CTA → "
                "O wydarzeniu → Program/Agenda → Prelegenci → Galeria (z poprzednich edycji) → "
                "CTA rejestracji → Kontakt. Kluczowe: data, miejsce, CTA."
            ),
            "generate_section_content": (
                "Ton zapraszający, energiczny. Data i miejsce prominentne. "
                "FOMO — ograniczone miejsca. Prelegenci z tytułami."
            ),
            "validate_consistency": (
                "LP wydarzenie — sprawdź datę, miejsce, program, CTA rejestracji."
            ),
        },
        readiness_skip_checks=["schema_person", "schema_service_product"],
        readiness_modify_checks={
            "cta_present": {
                "min_cta_count": 2,
                "fail_message": "Landing page wymaga minimum 2 przycisków CTA (u góry i na dole)",
            },
        },
        config_defaults={
            "forms": {"send_email_notification": True},
            "legal": {"cookie_banner": {"enabled": True, "style": "bar"}},
        },
        style_presets=[
            {"id": "event-vibrant", "label": "Eventowy żywy", "colors": ["#7C3AED", "#475569", "#EDE9FE"]},
            {"id": "event-dark", "label": "Eventowy ciemny", "colors": ["#111827", "#9CA3AF", "#F3F4F6"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "O firmie / o mnie", "Zespol / ludzie", "FAQ / pytania",
            "Kontakt / formularz", "Mapa dojazdu", "Partnerzy / klienci",
        ],
    ),

    "lp-webinar": SiteTypeConfig(
        site_type="lp-webinar",
        label="LP webinar",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "KR", "ZE", "OP", "FA", "CT", "FO"],
        min_sections=6,
        max_sections=10,
        allowed_block_categories=["NA", "HE", "FI", "KR", "ZE", "OP", "FA", "CT", "FO", "PR", "ST"],
        prompt_hints={
            "generate_structure": (
                "Landing page webinaru. Hero z tematem i CTA → Czego się nauczysz (korzyści) → "
                "Prowadzący → Opinie uczestników → FAQ → CTA rejestracji. "
                "Krótko, konkretnie, konwersja na zapis."
            ),
            "generate_section_content": (
                "Ton edukacyjny + perswazyjny. Co uczestnik zyska. "
                "Prowadzący jako ekspert. Limitowane miejsca."
            ),
            "validate_consistency": (
                "LP webinar — sprawdź temat, korzyści, prowadzącego, CTA."
            ),
        },
        readiness_skip_checks=["schema_person", "schema_service_product"],
        readiness_modify_checks={
            "cta_present": {
                "min_cta_count": 2,
                "fail_message": "Landing page wymaga minimum 2 przycisków CTA (u góry i na dole)",
            },
        },
        config_defaults={
            "forms": {"send_email_notification": True},
            "legal": {"cookie_banner": {"enabled": True, "style": "bar"}},
        },
        style_presets=[
            {"id": "edu-blue", "label": "Edukacyjny niebieski", "colors": ["#1D4ED8", "#64748B", "#DBEAFE"]},
            {"id": "webinar-green", "label": "Webinarowy zielony", "colors": ["#059669", "#475569", "#D1FAE5"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "O firmie / o mnie", "Opinie klientow",
            "FAQ / pytania", "Kontakt / formularz", "Korzysci / dlaczego my",
        ],
    ),

    "lp-wizerunkowa": SiteTypeConfig(
        site_type="lp-wizerunkowa",
        label="LP wizerunkowa",
        category="firma",
        recommended_blocks=["NA", "HE", "FI", "KR", "RE", "OP", "GA", "CT", "FO"],
        min_sections=6,
        max_sections=12,
        allowed_block_categories=["NA", "HE", "FI", "KR", "RE", "OP", "GA", "CT", "FO", "ST", "ZE"],
        prompt_hints={
            "generate_structure": (
                "Landing page wizerunkowa — budowanie marki. Hero z hasłem → "
                "O marce/firmie → Wartości/Korzyści → Realizacje → Opinie → Galeria → CTA. "
                "Emocjonalna, wizualna, premium."
            ),
            "generate_section_content": (
                "Ton aspiracyjny, emocjonalny. Wartości marki > cechy produktu. "
                "Wizualnie bogata treść. Storytelling."
            ),
            "validate_consistency": (
                "LP wizerunkowa — sprawdź spójność marki, ton emocjonalny, wizualność."
            ),
        },
        readiness_skip_checks=["schema_person"],
        readiness_modify_checks={
            "cta_present": {
                "min_cta_count": 2,
                "fail_message": "Landing page wymaga minimum 2 przycisków CTA (u góry i na dole)",
            },
        },
        style_presets=[
            {"id": "brand-elegant", "label": "Elegancki markowy", "colors": ["#1F2937", "#9CA3AF", "#F9FAFB"]},
            {"id": "brand-bold", "label": "Odważny markowy", "colors": ["#7C3AED", "#475569", "#F5F3FF"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "O firmie / o mnie", "Opinie klientow", "Portfolio / realizacje",
            "Kontakt / formularz", "Korzysci / dlaczego my", "Partnerzy / klienci",
        ],
    ),

    "lp-lead": SiteTypeConfig(
        site_type="lp-lead",
        label="LP lead magnet",
        category="firma",
        recommended_blocks=["NA", "HE", "KR", "PB", "RO", "OP", "CT", "FO"],
        min_sections=5,
        max_sections=10,
        allowed_block_categories=["NA", "HE", "KR", "PB", "RO", "OP", "CT", "FO", "FA", "OB", "ST"],
        prompt_hints={
            "generate_structure": (
                "Landing page lead magnet — zbieranie kontaktów. Hero z formularzem/CTA → "
                "Co dostajesz (korzyści) → Problem → Rozwiązanie → Opinie → CTA. "
                "Maksymalna konwersja, formularz widoczny od razu."
            ),
            "generate_section_content": (
                "Treść skoncentrowana na ofercie (e-book, raport, demo). "
                "Co użytkownik zyska. Krótko, konkretnie, CTA."
            ),
            "validate_consistency": (
                "LP lead magnet — sprawdź formularz, ofertę, CTA. Konwersja > estetyka."
            ),
        },
        readiness_skip_checks=["schema_person", "schema_service_product"],
        readiness_modify_checks={
            "cta_present": {
                "min_cta_count": 2,
                "fail_message": "Landing page wymaga minimum 2 przycisków CTA (u góry i na dole)",
            },
        },
        config_defaults={
            "forms": {"send_email_notification": True},
            "legal": {"cookie_banner": {"enabled": True, "style": "bar"}},
        },
        style_presets=[
            {"id": "lead-orange", "label": "Konwersyjny pomarańcz", "colors": ["#EA580C", "#78716C", "#FFF7ED"]},
            {"id": "lead-green", "label": "Zaufanie zielony", "colors": ["#059669", "#64748B", "#D1FAE5"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "Opinie klientow", "FAQ / pytania",
            "Kontakt / formularz", "Korzysci / dlaczego my",
        ],
    ),

    "wizytowka": SiteTypeConfig(
        site_type="wizytowka",
        label="Wizytówka",
        category="firma",
        recommended_blocks=["NA", "HE", "KO", "FO"],
        min_sections=3,
        max_sections=6,
        allowed_block_categories=["NA", "HE", "FI", "KO", "FO", "CT", "GA"],
        prompt_hints={
            "generate_structure": (
                "Minimalna strona wizytówkowa. 3-6 sekcji. Tylko kluczowe informacje: "
                "kto, co, kontakt. Bez FAQ, bez cennika, bez opinii."
            ),
            "generate_section_content": (
                "Treść minimalistyczna, zwięzła. Każde zdanie musi nieść wartość. Zero wypełniaczy."
            ),
            "validate_consistency": (
                "Wizytówka — sprawdź czy nie jest przeładowana. Prostota to zaleta."
            ),
        },
        readiness_skip_checks=[
            "llms_txt_ready", "schema_sameas", "schema_person",
            "schema_service_product", "schema_faq", "analytics",
        ],
        config_defaults={
            "legal": {"cookie_banner": {"enabled": False}},
        },
        style_presets=[
            {"id": "clean-mono", "label": "Czysty monochromatyczny", "colors": ["#1F2937", "#6B7280", "#F3F4F6"]},
            {"id": "minimal-blue", "label": "Minimalny niebieski", "colors": ["#2563EB", "#94A3B8", "#EFF6FF"]},
        ],
        brief_sections=["s1", "s2", "s8", "s11"],
        brief_content=[
            "Oferta uslug", "O firmie / o mnie", "Kontakt / formularz", "Mapa dojazdu",
        ],
    ),

    # ─── OSOBA ───

    "ekspert": SiteTypeConfig(
        site_type="ekspert",
        label="Ekspert / Freelancer",
        category="osoba",
        recommended_blocks=["NA", "HE", "FI", "OF", "RE", "OP", "CT", "KO", "FO"],
        min_sections=6,
        max_sections=12,
        prompt_hints={
            "generate_structure": (
                "Osobista marka ekspercka. Hero z imieniem i specjalizacją → O mnie → "
                "Oferta usług → Realizacje/Case studies → Opinie klientów → CTA → Kontakt. "
                "Buduj autorytet i zaufanie."
            ),
            "generate_section_content": (
                "Ton ekspercki ale przystępny. Pierwsza osoba ('Pomagam...', 'Specjalizuję się...'). "
                "Konkretne rezultaty, liczby, case studies."
            ),
            "validate_consistency": (
                "Ekspert — sprawdź specjalizację, ofertę, dowody kompetencji."
            ),
        },
        style_presets=[
            {"id": "expert-dark", "label": "Ekspercki ciemny", "colors": ["#0F172A", "#94A3B8", "#F8FAFC"]},
            {"id": "expert-warm", "label": "Ekspercki ciepły", "colors": ["#92400E", "#78716C", "#FFFBEB"]},
        ],
        brief_sections=["s1", "s2", "s3", "s5", "s6", "s7", "s8", "s9", "s11"],
        brief_content=[
            "Oferta uslug", "O firmie / o mnie", "Opinie klientow",
            "Portfolio / realizacje", "FAQ / pytania", "Kontakt / formularz",
            "Proces / jak dzialamy", "Korzysci / dlaczego my", "Certyfikaty / nagrody",
        ],
    ),

    "portfolio": SiteTypeConfig(
        site_type="portfolio",
        label="Portfolio",
        category="osoba",
        recommended_blocks=["NA", "HE", "FI", "RE", "GA", "OP", "KO", "FO"],
        min_sections=5,
        max_sections=10,
        allowed_block_categories=["NA", "HE", "FI", "RE", "GA", "OP", "KO", "FO", "CT", "PR"],
        prompt_hints={
            "generate_structure": (
                "Portfolio — wizualna prezentacja prac. Hero z imieniem → Krótko o mnie → "
                "Realizacje/Galeria (główna sekcja) → Opinie → Kontakt. "
                "Priorytet: projekty, zdjęcia, efekty pracy."
            ),
            "generate_section_content": (
                "Minimalna ilość tekstu, mocne nagłówki. Pozwól pracom mówić za siebie. "
                "Opisy projektów: krótkie — klient + efekt."
            ),
            "validate_consistency": (
                "Portfolio — czy realizacje są podkreślone? Czy jest kontakt?"
            ),
        },
        readiness_skip_checks=["schema_faq", "form_email"],
        style_presets=[
            {"id": "creative-bold", "label": "Kreatywny odważny", "colors": ["#7C3AED", "#1F2937", "#F5F3FF"]},
            {"id": "gallery-dark", "label": "Galeria ciemna", "colors": ["#111827", "#D1D5DB", "#1F2937"]},
        ],
        brief_sections=["s1", "s2", "s5", "s7", "s8", "s9", "s11"],
        brief_content=[
            "O firmie / o mnie", "Portfolio / realizacje", "Opinie klientow",
            "Kontakt / formularz", "Proces / jak dzialamy",
        ],
    ),

    "cv": SiteTypeConfig(
        site_type="cv",
        label="CV online",
        category="osoba",
        recommended_blocks=["NA", "HE", "FI", "RE", "CT", "KO", "FO"],
        min_sections=4,
        max_sections=8,
        allowed_block_categories=["NA", "HE", "FI", "RE", "KO", "FO", "CT", "ST", "PR"],
        prompt_hints={
            "generate_structure": (
                "CV online — przejrzysta prezentacja kwalifikacji. Hero z imieniem i stanowiskiem → "
                "O mnie → Doświadczenie/Realizacje → Umiejętności → Kontakt. Chronologicznie, czytelnie."
            ),
            "generate_section_content": (
                "Ton profesjonalny, konkretny. Liczby i fakty zamiast przymiotników. "
                "Doświadczenie: firma + okres + osiągnięcia."
            ),
            "validate_consistency": (
                "CV — czy dane kontaktowe kompletne? Czy jest doświadczenie?"
            ),
        },
        readiness_skip_checks=[
            "schema_faq", "form_email", "schema_service_product",
            "analytics", "cookie_banner",
        ],
        config_defaults={
            "legal": {"cookie_banner": {"enabled": False}},
        },
        style_presets=[
            {"id": "cv-classic", "label": "Klasyczny czarno-biały", "colors": ["#111827", "#6B7280", "#FFFFFF"]},
            {"id": "cv-modern", "label": "Nowoczesny minimalizm", "colors": ["#0F172A", "#94A3B8", "#F8FAFC"]},
        ],
        brief_sections=["s1", "s2", "s5", "s8", "s11"],
        brief_content=[
            "O firmie / o mnie", "Portfolio / realizacje",
            "Kontakt / formularz", "Certyfikaty / nagrody",
        ],
    ),

    "blog-osoba": SiteTypeConfig(
        site_type="blog-osoba",
        label="Blog osobisty",
        category="osoba",
        recommended_blocks=["NA", "HE", "FI", "RE", "CT", "KO", "FO"],
        min_sections=4,
        max_sections=10,
        allowed_block_categories=["NA", "HE", "FI", "RE", "CT", "KO", "FO", "OP", "GA"],
        prompt_hints={
            "generate_structure": (
                "Blog osobisty — treść i osobowość. Hero z imieniem → O mnie/blogu → "
                "Wyróżnione posty → CTA (subskrypcja) → Kontakt."
            ),
            "generate_section_content": (
                "Ton osobisty, autentyczny. Pierwsza osoba. Pasja i ekspertyza."
            ),
            "validate_consistency": (
                "Blog osobisty — sprawdź temat bloga, CTA subskrypcji."
            ),
        },
        readiness_skip_checks=["schema_service_product"],
        style_presets=[
            {"id": "blog-clean", "label": "Czysty czytelny", "colors": ["#111827", "#6B7280", "#FFFFFF"]},
            {"id": "blog-warm", "label": "Ciepły osobisty", "colors": ["#92400E", "#78716C", "#FFFBEB"]},
        ],
        brief_sections=["s1", "s2", "s5", "s7", "s8", "s11"],
        brief_content=[
            "O firmie / o mnie", "Blog / aktualnosci",
            "Kontakt / formularz", "Opinie klientow",
        ],
    ),

    "wizytowka-osoba": SiteTypeConfig(
        site_type="wizytowka-osoba",
        label="Wizytówka osobista",
        category="osoba",
        recommended_blocks=["NA", "HE", "KO", "FO"],
        min_sections=3,
        max_sections=6,
        allowed_block_categories=["NA", "HE", "FI", "KO", "FO", "CT"],
        prompt_hints={
            "generate_structure": (
                "Minimalna wizytówka osobista. 3-6 sekcji. Imię, co robię, kontakt. "
                "Bez FAQ, bez cennika, bez opinii."
            ),
            "generate_section_content": (
                "Treść minimalistyczna. Imię, specjalizacja, kontakt. Zero zbędnego tekstu."
            ),
            "validate_consistency": (
                "Wizytówka osobista — sprawdź prostotę i kompletność danych kontaktowych."
            ),
        },
        readiness_skip_checks=[
            "llms_txt_ready", "schema_sameas", "schema_person",
            "schema_service_product", "schema_faq", "analytics",
        ],
        config_defaults={
            "legal": {"cookie_banner": {"enabled": False}},
        },
        style_presets=[
            {"id": "clean-mono", "label": "Czysty monochromatyczny", "colors": ["#1F2937", "#6B7280", "#F3F4F6"]},
            {"id": "minimal-blue", "label": "Minimalny niebieski", "colors": ["#2563EB", "#94A3B8", "#EFF6FF"]},
        ],
        brief_sections=["s1", "s2", "s8", "s11"],
        brief_content=[
            "O firmie / o mnie", "Kontakt / formularz", "Mapa dojazdu",
        ],
    ),
}


# ============================================================================
# Helper functions
# ============================================================================

_FALLBACK_TYPE = "firmowa"


def get_site_type_config(site_type: str | None) -> SiteTypeConfig:
    """Get config for a site type. Falls back to 'firmowa' defaults."""
    if not site_type:
        return SITE_TYPE_CONFIGS[_FALLBACK_TYPE]
    return SITE_TYPE_CONFIGS.get(site_type, SITE_TYPE_CONFIGS[_FALLBACK_TYPE])


def get_prompt_hint(site_type: str | None, stage: str) -> str:
    """Get prompt hint for a specific stage, empty string if none."""
    config = get_site_type_config(site_type)
    return config.prompt_hints.get(stage, "")


def get_all_site_types() -> list[dict]:
    """List all site types with basic info."""
    return [
        {"site_type": c.site_type, "label": c.label, "category": c.category}
        for c in SITE_TYPE_CONFIGS.values()
    ]


def to_api_dict(config: SiteTypeConfig) -> dict:
    """Serialize SiteTypeConfig to dict for API response."""
    from dataclasses import asdict
    return asdict(config)
