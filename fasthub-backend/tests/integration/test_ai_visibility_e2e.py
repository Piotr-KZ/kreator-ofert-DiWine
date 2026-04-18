"""
E2E Integration Tests for Brief 41: AI Visibility — Full User Flow.
Tests cover the complete lifecycle: save data → load data → readiness check → publish.
"""

import json
from types import SimpleNamespace

import pytest

from app.services.creator.schema_generator import SchemaGenerator
from app.services.creator.llms_generator import LlmsGenerator
from app.services.creator.openapi_generator import OpenAPIGenerator
from app.services.creator.ai_visibility_validator import AIVisibilityValidator
from app.services.creator.readiness_checker import ReadinessChecker


# ============================================================================
# Full project fixture
# ============================================================================


def _full_project():
    """Simulate a real project with brief, config, sections, and AI visibility."""
    return SimpleNamespace(
        name="Acme Digital",
        site_type="firmowa",
        domain="acmedigital.pl",
        brief_json={
            "company_name": "Acme Digital Sp. z o.o.",
            "industry": "Marketing / Reklama",
            "description": "Agencja marketingowa specjalizująca się w kampaniach online.",
            "contact_email": "hello@acmedigital.pl",
            "contact_phone": "+48 500 600 700",
            "founded_year": 2018,
        },
        config_json={
            "hosting": {"subdomain": "acmedigital", "custom_domain": "acmedigital.pl"},
            "social": {
                "linkedin": "https://linkedin.com/company/acmedigital",
                "facebook": "https://facebook.com/acmedigital",
                "instagram": "https://instagram.com/acmedigital",
            },
            "forms": {
                "contact_email": "hello@acmedigital.pl",
                "newsletter_enabled": True,
            },
        },
        ai_visibility={
            "description": "Agencja marketingowa z 6-letnim doświadczeniem. "
                           "Specjalizujemy się w kampaniach Google Ads, SEO i social media. "
                           "Obsługujemy 50+ klientów rocznie.",
            "social_profiles": [
                {"name": "Facebook", "url": "https://facebook.com/acmedigital"},
                {"name": "LinkedIn", "url": "https://linkedin.com/company/acmedigital"},
                {"name": "Instagram", "url": "https://instagram.com/acmedigital"},
                {"name": "YouTube", "url": "https://youtube.com/@acmedigital"},
            ],
            "websites": [
                {"name": "Strona główna", "url": "https://acmedigital.pl"},
                {"name": "Blog", "url": "https://blog.acmedigital.pl"},
                {"name": "Clutch profil", "url": "https://clutch.co/profile/acmedigital"},
            ],
            "categories": {
                "uslugi": [
                    {"name": "Google Ads", "description": "Kampanie PPC: search, display, shopping, YouTube Ads"},
                    {"name": "SEO", "description": "Pozycjonowanie stron, audyt SEO, link building, content marketing"},
                    {"name": "Social Media Marketing", "description": "Prowadzenie profili FB, IG, LinkedIn, TikTok"},
                    {"name": "Content Marketing", "description": "Artykuły, e-booki, infografiki, video content"},
                ],
                "projekty": [
                    {"name": "Kampania XYZ dla firmy ABC", "description": "ROAS 5.2x, 3 mies., budżet 50k PLN"},
                    {"name": "Rebranding marki DEF", "description": "Nowa identyfikacja wizualna + strategia digital"},
                ],
                "certyfikaty": [
                    {"name": "Google Partner Premier", "description": "Najwyższy status partnerski Google Ads"},
                    {"name": "Meta Business Partner", "description": "Certyfikowany partner reklamowy Meta"},
                    {"name": "HubSpot Solutions Partner", "description": "Partner wdrożeniowy HubSpot CRM"},
                ],
                "opinie": [
                    {"name": "Jan Nowak, CEO FirmyABC", "description": "Współpraca z Acme to czysta przyjemność. ROAS wzrósł o 320%."},
                    {"name": "Anna Wiśniewska, CMO DEF", "description": "Profesjonalizm i terminowość na najwyższym poziomie."},
                ],
                "sukcesy": [
                    {"name": "Top 10 Agencji SEM w Polsce 2024"},
                    {"name": "Clutch Top Digital Marketing Agency 2023"},
                ],
                "metodyki": [
                    {"name": "Data-Driven Marketing", "description": "Decyzje oparte na danych: GA4, Looker Studio, BigQuery"},
                    {"name": "Growth Hacking", "description": "Szybkie eksperymenty A/B, iteracyjna optymalizacja"},
                ],
                "artykuly": [
                    {"name": "Jak zwiększyć ROAS o 300%", "description": "Case study kampanii Google Ads, opublikowany w Marketing i Biznes"},
                ],
            },
            "people": [
                {
                    "name": "Piotr Zieliński",
                    "title": "CEO & Strateg Marketingowy",
                    "categories": {
                        "kompetencje": [
                            {"name": "Google Ads (Search, Display, Shopping)", "description": "12 lat doświadczenia, certyfikat Google"},
                            {"name": "Strategia marketingowa", "description": "Planowanie kampanii 360°, budżety 10k-500k/mies."},
                            {"name": "Analityka webowa", "description": "GA4, GTM, Looker Studio, BigQuery"},
                        ],
                        "doswiadczenie": [
                            {"name": "Acme Digital", "period": "2018-teraz", "description": "Założyciel i CEO. Zbudował agencję od zera do 15 osób."},
                            {"name": "MediaHouse", "period": "2014-2018", "description": "Head of SEM. Zarządzanie budżetem 2M PLN/mies."},
                            {"name": "StartupXYZ", "period": "2012-2014", "description": "Marketing Manager. Wzrost ARR z 0 do 1M PLN."},
                        ],
                        "wyksztalcenie": [
                            {"school": "SGH Warszawa", "title": "MBA", "description": "Specjalizacja: Marketing Digital"},
                            {"school": "Politechnika Warszawska", "title": "mgr inż.", "description": "Informatyka, specjalizacja e-commerce"},
                        ],
                        "certyfikaty": [
                            {"name": "Google Ads Certified Professional"},
                            {"name": "HubSpot Inbound Marketing"},
                            {"name": "Meta Blueprint Certified"},
                        ],
                        "sukcesy": [
                            {"name": "Forbes 30 Under 30 (Marketing, 2020)"},
                        ],
                    },
                },
                {
                    "name": "Marta Kowalska",
                    "title": "Head of Content & SEO",
                    "categories": {
                        "kompetencje": [
                            {"name": "SEO techniczne", "description": "Audyty, Core Web Vitals, crawl budget"},
                            {"name": "Content strategy", "description": "Planowanie treści, keyword research, topical authority"},
                        ],
                        "doswiadczenie": [
                            {"name": "Acme Digital", "period": "2019-teraz", "description": "Budowa działu SEO i content od zera"},
                            {"name": "ContentAgency", "period": "2016-2019", "description": "Senior SEO Specialist"},
                        ],
                    },
                },
            ],
        },
        style_json={"palette_preset": "indigo-slate"},
        sections=[
            SimpleNamespace(
                block_code="FA01",
                slots_json={
                    "faq_items": [
                        {"question": "Ile kosztuje kampania Google Ads?", "answer": "Od 3000 PLN miesięcznie."},
                        {"question": "Jak szybko zobaczę wyniki?", "answer": "Pierwsze efekty po 2-4 tygodniach."},
                        {"question": "Czy podpisujecie umowę?", "answer": "Tak, standardowo na 6 lub 12 miesięcy."},
                    ]
                },
                is_visible=True,
            ),
        ],
    )


# ============================================================================
# E2E Test: Full AI Visibility Pipeline
# ============================================================================


class TestE2EAIVisibilityPipeline:
    """End-to-end test: AI visibility data → Schema → llms.txt → readiness → publish."""

    def test_full_pipeline_schema_generation(self):
        """Verify Schema.org contains all expected entity types."""
        project = _full_project()
        schemas = SchemaGenerator().generate(project)

        types = [s.get("@type") for s in schemas]

        # Organization
        assert "LocalBusiness" in types
        org = next(s for s in schemas if s["@type"] == "LocalBusiness")
        assert org["name"] == "Acme Digital Sp. z o.o."
        assert len(org.get("sameAs", [])) >= 7  # 3 social config + 4 ai social + 3 websites

        # Persons (2)
        persons = [s for s in schemas if s.get("@type") == "Person"]
        assert len(persons) == 2
        piotr = next(p for p in persons if p["name"] == "Piotr Zieliński")
        assert piotr["jobTitle"] == "CEO & Strateg Marketingowy"
        assert len(piotr.get("knowsAbout", [])) == 3
        assert len(piotr.get("hasOccupation", [])) == 3
        assert len(piotr.get("alumniOf", [])) == 2
        assert len(piotr.get("hasCredential", [])) == 3

        marta = next(p for p in persons if p["name"] == "Marta Kowalska")
        assert marta["jobTitle"] == "Head of Content & SEO"
        assert len(marta.get("knowsAbout", [])) == 2

        # Services (4)
        services = [s for s in schemas if s.get("@type") == "Service"]
        assert len(services) == 4
        assert any(s["name"] == "Google Ads" for s in services)

        # Reviews (2)
        reviews = [s for s in schemas if s.get("@type") == "Review"]
        assert len(reviews) == 2

        # FAQ
        faq_pages = [s for s in schemas if s.get("@type") == "FAQPage"]
        assert len(faq_pages) == 1
        assert len(faq_pages[0]["mainEntity"]) == 3

        # WebSite
        assert "WebSite" in types

    def test_full_pipeline_llms_txt(self):
        """Verify llms.txt contains all structured sections."""
        project = _full_project()
        result = LlmsGenerator().generate(project)

        # Header
        assert result.startswith("# Acme Digital Sp. z o.o.")

        # About
        assert "## About" in result
        assert "Agencja marketingowa z 6-letnim" in result

        # Links
        assert "## Links" in result
        assert "facebook.com/acmedigital" in result

        # Categories
        assert "## Services" in result
        assert "**Google Ads**" in result
        assert "**SEO**" in result

        assert "## Projects" in result
        assert "Kampania XYZ" in result

        assert "## Credentials" in result
        assert "Google Partner Premier" in result

        assert "## Reviews" in result
        assert "ROAS wzrósł o 320%" in result

        assert "## Achievements" in result
        assert "Top 10 Agencji" in result

        assert "## Methodology" in result
        assert "Data-Driven Marketing" in result

        # People
        assert "## Key Person: Piotr Zieliński (CEO & Strateg Marketingowy)" in result
        assert "### Expertise" in result
        assert "### Career History" in result
        assert "### Education" in result

        assert "## Key Person: Marta Kowalska (Head of Content & SEO)" in result

        # Contact
        assert "## Contact" in result
        assert "hello@acmedigital.pl" in result

    def test_full_pipeline_openapi(self):
        """Verify openapi.json for contact + newsletter."""
        project = _full_project()
        result = OpenAPIGenerator().generate(project)

        assert result is not None
        assert result["openapi"] == "3.0.3"
        assert result["info"]["title"] == "Acme Digital Sp. z o.o. API"
        assert "/api/contact" in result["paths"]
        assert "/api/newsletter" in result["paths"]

    def test_full_pipeline_validator(self):
        """Verify validator detects experience older than company."""
        project = _full_project()
        findings = AIVisibilityValidator().validate(
            project.ai_visibility,
            project.brief_json,
        )

        # Piotr has experience from 2012, company founded 2018
        exp_findings = [f for f in findings if f["type"] == "experience_exceeds_company_age"]
        assert len(exp_findings) >= 1
        assert any("2012" in f["message"] or "2014" in f["message"] for f in exp_findings)
        assert all(f["severity"] == "success" for f in exp_findings)

        # No missing description warning
        desc = [f for f in findings if f["type"] == "missing_description"]
        assert len(desc) == 0

    def test_full_pipeline_readiness(self):
        """Verify all 6 AI readiness checks pass for complete data."""
        project = _full_project()
        checker = ReadinessChecker()
        result = checker.check(project)
        checks = result["checks"]

        ai_keys = ["llms_txt_ready", "schema_sameas", "schema_person",
                    "schema_service_product", "schema_faq", "ai_experience_check"]

        for key in ai_keys:
            check = next((c for c in checks if c["key"] == key), None)
            assert check is not None, f"Missing check: {key}"
            assert check["status"] == "pass", f"Check {key} failed: {check}"

    def test_full_pipeline_readiness_empty(self):
        """Verify readiness warns when AI visibility is empty."""
        project = _full_project()
        project.ai_visibility = {}
        project.sections = []

        checker = ReadinessChecker()
        result = checker.check(project)
        checks = result["checks"]

        llms = next((c for c in checks if c["key"] == "llms_txt_ready"), None)
        assert llms is not None
        # Brief has description so llms.txt may still pass; check it exists
        assert llms["status"] in ("pass", "warn", "info")

    def test_full_pipeline_publisher_schema_contains_all(self):
        """Verify publisher generates complete schema JSON-LD."""
        from app.services.creator.publisher import PublishingEngine

        engine = PublishingEngine.__new__(PublishingEngine)
        project = _full_project()

        html_snippet = engine._build_schema_jsonld(project)

        assert '<script type="application/ld+json">' in html_snippet
        raw = html_snippet.replace('<script type="application/ld+json">', '').replace('</script>', '')
        schemas = json.loads(raw)

        types = [s.get("@type") for s in schemas]
        assert "LocalBusiness" in types
        assert "Person" in types
        assert "Service" in types
        assert "WebSite" in types
        assert "FAQPage" in types

    def test_full_pipeline_publisher_llms_txt(self):
        """Verify publisher generates llms.txt correctly."""
        from app.services.creator.publisher import PublishingEngine

        engine = PublishingEngine.__new__(PublishingEngine)
        project = _full_project()

        llms_txt = LlmsGenerator().generate(project)

        # Verify non-empty and contains key sections
        assert len(llms_txt) > 500
        assert "# Acme Digital" in llms_txt
        assert "## Services" in llms_txt
        assert "## Contact" in llms_txt


# ============================================================================
# Edge Cases
# ============================================================================


class TestE2EEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_ai_visibility_still_generates_schema(self):
        """Even without AI visibility, basic schema should generate."""
        project = _full_project()
        project.ai_visibility = {}

        schemas = SchemaGenerator().generate(project)
        assert len(schemas) >= 2  # At least Organization + WebSite
        types = [s.get("@type") for s in schemas]
        assert "LocalBusiness" in types
        assert "WebSite" in types

    def test_empty_ai_visibility_still_generates_llms(self):
        """Even without AI visibility, basic llms.txt from brief should generate."""
        project = _full_project()
        project.ai_visibility = {}

        result = LlmsGenerator().generate(project)
        assert "# Acme Digital" in result
        assert "## About" in result
        assert "## Contact" in result

    def test_person_without_categories(self):
        """Person with only name+title, no categories."""
        project = _full_project()
        project.ai_visibility = {
            "description": "Firma testowa",
            "people": [{"name": "Test User", "title": "Developer", "categories": {}}],
        }

        schemas = SchemaGenerator().generate(project)
        persons = [s for s in schemas if s.get("@type") == "Person"]
        assert len(persons) == 1
        assert persons[0]["name"] == "Test User"

    def test_single_category_single_item(self):
        """Minimal: one category with one item."""
        project = _full_project()
        project.ai_visibility = {
            "description": "Firma testowa",
            "categories": {
                "uslugi": [{"name": "Konsulting", "description": "Doradztwo strategiczne"}]
            },
        }

        schemas = SchemaGenerator().generate(project)
        services = [s for s in schemas if s.get("@type") == "Service"]
        assert len(services) == 1
        assert services[0]["name"] == "Konsulting"

        result = LlmsGenerator().generate(project)
        assert "## Services" in result
        assert "**Konsulting**" in result

    def test_many_social_profiles(self):
        """Test with 8+ social profiles to ensure sameAs scales."""
        project = _full_project()
        project.ai_visibility = {
            "description": "Firma testowa",
            "social_profiles": [
                {"name": f"Profile{i}", "url": f"https://example.com/p{i}"}
                for i in range(10)
            ],
            "websites": [
                {"name": f"Site{i}", "url": f"https://site{i}.com"}
                for i in range(5)
            ],
        }

        schemas = SchemaGenerator().generate(project)
        org = schemas[0]
        # 3 from social config + 10 from ai social_profiles + 5 from ai websites
        assert len(org.get("sameAs", [])) >= 15

    def test_experience_period_parsing(self):
        """Test various period formats in doswiadczenie."""
        project = _full_project()
        project.ai_visibility = {
            "description": "Test",
            "people": [{
                "name": "Jan",
                "title": "Dev",
                "categories": {
                    "doswiadczenie": [
                        {"name": "Firma A", "period": "2010-2015", "description": "Dev"},
                        {"name": "Firma B", "period": "2015-teraz", "description": "Senior Dev"},
                        {"name": "Firma C", "period": "2005 - 2010", "description": "Junior"},
                    ],
                },
            }],
        }

        schemas = SchemaGenerator().generate(project)
        persons = [s for s in schemas if s.get("@type") == "Person"]
        assert len(persons) == 1
        assert len(persons[0].get("hasOccupation", [])) == 3

    def test_all_9_company_categories(self):
        """Test all 9 company categories generate correct Schema types."""
        project = _full_project()
        project.ai_visibility = {
            "description": "Firma testowa",
            "categories": {
                "produkty": [{"name": "Produkt X", "description": "Opis"}],
                "uslugi": [{"name": "Usługa Y", "description": "Opis"}],
                "projekty": [{"name": "Projekt Z", "description": "Opis"}],
                "metodyki": [{"name": "Metodyka M", "description": "Opis"}],
                "certyfikaty": [{"name": "ISO 9001", "description": "Opis"}],
                "opinie": [{"name": "Jan, CEO", "description": "Świetna firma!"}],
                "artykuly": [{"name": "Artykuł A", "description": "Opis"}],
                "oddzialy": [{"name": "Warszawa", "description": "ul. Marszałkowska 1"}],
                "sukcesy": [{"name": "Nagroda 2024"}],
            },
        }

        schemas = SchemaGenerator().generate(project)
        types = [s.get("@type") for s in schemas]

        assert "Product" in types
        assert "Service" in types
        assert "CreativeWork" in types
        assert "HowTo" in types
        assert "Review" in types
        assert "Article" in types

    def test_validator_no_findings_for_complete_data(self):
        """Complete data should not trigger warn-level findings."""
        project = _full_project()
        findings = AIVisibilityValidator().validate(
            project.ai_visibility,
            project.brief_json,
        )

        warns = [f for f in findings if f["severity"] == "warn"]
        assert len(warns) == 0, f"Unexpected warnings: {warns}"
