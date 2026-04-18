"""
Tests for Brief 41: AI Visibility — SchemaGenerator, LlmsGenerator, OpenAPIGenerator,
AIVisibilityValidator, publisher integration, readiness checker.
12 integration tests.
"""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.services.creator.schema_generator import SchemaGenerator
from app.services.creator.llms_generator import LlmsGenerator
from app.services.creator.openapi_generator import OpenAPIGenerator
from app.services.creator.ai_visibility_validator import AIVisibilityValidator
from app.services.creator.readiness_checker import ReadinessChecker


# ============================================================================
# Helpers
# ============================================================================


def _make_project(**kwargs):
    """Create a mock project with defaults."""
    defaults = {
        "name": "Test Corp",
        "site_type": "firmowa",
        "domain": "testcorp.pl",
        "brief_json": {
            "company_name": "Test Corp Sp. z o.o.",
            "industry": "IT",
            "description": "Firma technologiczna zajmująca się rozwojem oprogramowania.",
            "contact_email": "kontakt@testcorp.pl",
            "contact_phone": "+48 123 456 789",
            "founded_year": 2015,
        },
        "config_json": {
            "hosting": {"subdomain": "testcorp", "custom_domain": "testcorp.pl"},
            "social": {
                "linkedin": "https://linkedin.com/company/testcorp",
                "facebook": "https://facebook.com/testcorp",
            },
            "forms": {"contact_email": "kontakt@testcorp.pl"},
        },
        "ai_visibility": {},
        "style_json": {},
        "sections": [],
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_section(block_code, slots_json=None, is_visible=True):
    """Create a mock section."""
    return SimpleNamespace(block_code=block_code, slots_json=slots_json, is_visible=is_visible)


FULL_AI_VISIBILITY = {
    "description": "Lider w tworzeniu oprogramowania na miarę — 10 lat doświadczenia.",
    "social_profiles": [
        {"name": "GitHub", "url": "https://github.com/testcorp"},
    ],
    "websites": [
        {"name": "Blog", "url": "https://blog.testcorp.pl"},
    ],
    "categories": {
        "uslugi": [
            {"name": "Tworzenie stron WWW", "description": "Nowoczesne strony responsywne"},
            {"name": "Aplikacje mobilne", "description": "iOS i Android"},
        ],
        "produkty": [
            {"name": "FastCRM", "description": "System CRM dla MŚP"},
        ],
        "certyfikaty": [
            {"name": "ISO 27001", "description": "Bezpieczeństwo informacji"},
        ],
        "sukcesy": [
            {"name": "Top 10 Software House 2024"},
        ],
    },
    "people": [
        {
            "name": "Jan Kowalski",
            "title": "CEO & Founder",
            "categories": {
                "kompetencje": [
                    {"name": "Python"},
                    {"name": "Cloud Architecture"},
                ],
                "doswiadczenie": [
                    {"name": "Software Engineer", "period": "2010-2015", "description": "Google"},
                    {"name": "CTO", "period": "2015-2020", "description": "StartupXYZ"},
                ],
                "wyksztalcenie": [
                    {"name": "Informatyka", "school": "Politechnika Warszawska", "title": "mgr inż."},
                ],
                "certyfikaty": [
                    {"name": "AWS Solutions Architect"},
                ],
                "sukcesy": [
                    {"name": "Forbes 30 Under 30"},
                ],
            },
        },
    ],
}


# ============================================================================
# SchemaGenerator Tests (5)
# ============================================================================


class TestSchemaGenerator:
    """Test rich Schema.org JSON-LD generation."""

    def test_basic_organization(self):
        """Test basic Organization schema from brief."""
        project = _make_project()
        schemas = SchemaGenerator().generate(project)

        org = schemas[0]
        assert org["@type"] == "LocalBusiness"
        assert org["name"] == "Test Corp Sp. z o.o."
        assert org["url"] == "https://testcorp.pl"
        assert "IT" in (org.get("industry") or "")

    def test_person_with_categories(self):
        """Test Person schema with kompetencje, doswiadczenie, wyksztalcenie."""
        project = _make_project(ai_visibility=FULL_AI_VISIBILITY)
        schemas = SchemaGenerator().generate(project)

        persons = [s for s in schemas if s.get("@type") == "Person"]
        assert len(persons) == 1

        person = persons[0]
        assert person["name"] == "Jan Kowalski"
        assert person["jobTitle"] == "CEO & Founder"
        assert "Python" in person["knowsAbout"]
        assert len(person["hasOccupation"]) == 2
        assert len(person["alumniOf"]) == 1
        assert person["alumniOf"][0]["name"] == "Politechnika Warszawska"
        assert "Forbes 30 Under 30" in person["award"]

    def test_categories_service_product(self):
        """Test Service and Product schemas from categories."""
        project = _make_project(ai_visibility=FULL_AI_VISIBILITY)
        schemas = SchemaGenerator().generate(project)

        services = [s for s in schemas if s.get("@type") == "Service"]
        products = [s for s in schemas if s.get("@type") == "Product"]

        assert len(services) == 2
        assert services[0]["name"] == "Tworzenie stron WWW"
        assert len(products) == 1
        assert products[0]["name"] == "FastCRM"

    def test_faq_page(self):
        """Test FAQPage schema from FAQ sections."""
        faq_section = _make_section("FA01", slots_json={
            "faq_items": [
                {"question": "Ile kosztuje strona?", "answer": "Od 2000 zł."},
                {"question": "Jak długo trwa realizacja?", "answer": "2-4 tygodnie."},
            ]
        })
        project = _make_project(sections=[faq_section])
        schemas = SchemaGenerator().generate(project)

        faq_schemas = [s for s in schemas if s.get("@type") == "FAQPage"]
        assert len(faq_schemas) == 1
        assert len(faq_schemas[0]["mainEntity"]) == 2
        assert faq_schemas[0]["mainEntity"][0]["name"] == "Ile kosztuje strona?"

    def test_sameas_combined(self):
        """Test sameAs combines social config + ai_visibility links."""
        project = _make_project(ai_visibility=FULL_AI_VISIBILITY)
        schemas = SchemaGenerator().generate(project)

        org = schemas[0]
        same_as = org.get("sameAs", [])

        # From social config
        assert "https://linkedin.com/company/testcorp" in same_as
        assert "https://facebook.com/testcorp" in same_as
        # From ai_visibility
        assert "https://github.com/testcorp" in same_as
        assert "https://blog.testcorp.pl" in same_as


# ============================================================================
# LlmsGenerator Tests (3)
# ============================================================================


class TestLlmsGenerator:
    """Test llms.txt generation."""

    def test_basic_llms_txt(self):
        """Test basic llms.txt with company name and description."""
        project = _make_project(ai_visibility={
            "description": "Firma technologiczna.",
        })
        result = LlmsGenerator().generate(project)

        assert result.startswith("# Test Corp Sp. z o.o.")
        assert "## About" in result
        assert "Firma technologiczna." in result
        assert "> Industry: IT" in result

    def test_dynamic_categories(self):
        """Test llms.txt with dynamic categories and people."""
        project = _make_project(ai_visibility=FULL_AI_VISIBILITY)
        result = LlmsGenerator().generate(project)

        assert "## Services" in result
        assert "**Tworzenie stron WWW**" in result
        assert "## Products" in result
        assert "**FastCRM**" in result
        assert "## Key Person: Jan Kowalski (CEO & Founder)" in result
        assert "### Expertise" in result
        assert "**Python**" in result
        assert "### Career History" in result

    def test_empty_fallback(self):
        """Test llms.txt with minimal data (no ai_visibility)."""
        project = _make_project(ai_visibility={})
        result = LlmsGenerator().generate(project)

        # Should still have title and description from brief
        assert "# Test Corp Sp. z o.o." in result
        assert "## About" in result
        assert "Firma technologiczna" in result
        assert "## Contact" in result
        assert "kontakt@testcorp.pl" in result


# ============================================================================
# OpenAPIGenerator Tests (1)
# ============================================================================


class TestOpenAPIGenerator:
    """Test openapi.json generation."""

    def test_generates_spec_with_form(self):
        """Test OpenAPI spec generation when contact form is configured."""
        project = _make_project(config_json={
            "hosting": {"subdomain": "testcorp"},
            "forms": {
                "contact_email": "kontakt@testcorp.pl",
                "newsletter_enabled": True,
            },
            "social": {},
        })
        result = OpenAPIGenerator().generate(project)

        assert result is not None
        assert result["openapi"] == "3.0.3"
        assert "/api/contact" in result["paths"]
        assert "/api/newsletter" in result["paths"]
        assert result["info"]["title"] == "Test Corp Sp. z o.o. API"

    def test_returns_none_without_forms(self):
        """Test returns None when no forms configured."""
        project = _make_project(config_json={
            "hosting": {"subdomain": "testcorp"},
            "forms": {},
            "social": {},
        })
        result = OpenAPIGenerator().generate(project)
        assert result is None


# ============================================================================
# AIVisibilityValidator Tests (1)
# ============================================================================


class TestAIVisibilityValidator:
    """Test AI Visibility cross-validation."""

    def test_experience_exceeds_company_age(self):
        """Test detection of person experience older than company founding."""
        ai_data = FULL_AI_VISIBILITY
        brief_data = {"founded_year": 2015}

        findings = AIVisibilityValidator().validate(ai_data, brief_data)

        # Jan Kowalski has experience from 2010, company founded 2015
        exp_findings = [f for f in findings if f["type"] == "experience_exceeds_company_age"]
        assert len(exp_findings) == 1
        assert "2010" in exp_findings[0]["message"]
        assert exp_findings[0]["severity"] == "success"

    def test_missing_description_warning(self):
        """Test warning when description is missing."""
        findings = AIVisibilityValidator().validate({}, {})
        desc_findings = [f for f in findings if f["type"] == "missing_description"]
        assert len(desc_findings) == 1
        assert desc_findings[0]["severity"] == "warn"


# ============================================================================
# Publisher Integration Tests (1)
# ============================================================================


class TestPublisherIntegration:
    """Test publisher generates llms.txt and Schema."""

    def test_schema_jsonld_uses_schema_generator(self):
        """Test _build_schema_jsonld delegates to SchemaGenerator."""
        from app.services.creator.publisher import PublishingEngine

        engine = PublishingEngine.__new__(PublishingEngine)
        project = _make_project(ai_visibility=FULL_AI_VISIBILITY)

        result = engine._build_schema_jsonld(project)

        assert '<script type="application/ld+json">' in result
        parsed = json.loads(result.replace('<script type="application/ld+json">', '').replace('</script>', ''))
        assert isinstance(parsed, list)
        types = [s.get("@type") for s in parsed]
        assert "LocalBusiness" in types
        assert "Person" in types


# ============================================================================
# ReadinessChecker Tests (1)
# ============================================================================


class TestReadinessCheckerAI:
    """Test AI Visibility checks in readiness checker."""

    def test_ai_visibility_checks(self):
        """Test all 6 AI Visibility checks."""
        project = _make_project(
            ai_visibility=FULL_AI_VISIBILITY,
            sections=[
                _make_section("FA01", slots_json={
                    "faq_items": [{"question": "Q?", "answer": "A."}]
                }),
            ],
        )

        checker = ReadinessChecker()
        result = checker.check(project)
        checks = result["checks"]
        keys = [c["key"] for c in checks]

        # All 6 AI Visibility checks present
        assert "llms_txt_ready" in keys
        assert "schema_sameas" in keys
        assert "schema_person" in keys
        assert "schema_service_product" in keys
        assert "schema_faq" in keys
        assert "ai_experience_check" in keys

        # Specific statuses
        llms = next(c for c in checks if c["key"] == "llms_txt_ready")
        assert llms["status"] == "pass"

        sameas = next(c for c in checks if c["key"] == "schema_sameas")
        assert sameas["status"] == "pass"

        person = next(c for c in checks if c["key"] == "schema_person")
        assert person["status"] == "pass"

        sp = next(c for c in checks if c["key"] == "schema_service_product")
        assert sp["status"] == "pass"

        faq = next(c for c in checks if c["key"] == "schema_faq")
        assert faq["status"] == "pass"

        exp = next(c for c in checks if c["key"] == "ai_experience_check")
        assert exp["status"] == "pass"
