"""
Tests for Brief 42: ReadinessChecker per-type behavior.
8 unit tests (no DB needed, uses mock Project).
"""

import pytest
from unittest.mock import MagicMock

from app.services.creator.readiness_checker import ReadinessChecker


def _make_project(site_type="firmowa", sections=None, config_json=None,
                  style_json=None, brief_json=None, ai_visibility=None):
    """Create a mock Project with given attributes."""
    project = MagicMock()
    project.site_type = site_type
    project.sections = sections or []
    project.config_json = config_json or {}
    project.style_json = style_json or {"color_primary": "#4F46E5", "color_secondary": "#64748B"}
    project.brief_json = brief_json or {"company_name": "Test Firma"}
    project.ai_visibility = ai_visibility or {}
    return project


def _make_section(block_code="HE1", visible=True, slots=None):
    """Create a mock section."""
    s = MagicMock()
    s.block_code = block_code
    s.is_visible = visible
    s.slots_json = slots or {}
    s.position = 0
    return s


class TestReadinessPerType:
    """Tests for per-type readiness check behavior."""

    def test_wizytowka_skips_ai_visibility(self):
        """Wizytowka readiness has no AI Visibility checks in active list."""
        checker = ReadinessChecker()
        project = _make_project(
            site_type="wizytowka",
            sections=[_make_section("HE1", slots={"title": "Test"})],
        )
        result = checker.check(project)

        active_keys = {c["key"] for c in result["checks"]}
        skipped_keys = {c["key"] for c in result["skipped"]}

        # AI visibility keys should be in skipped, not in active
        ai_keys = {"llms_txt_ready", "schema_sameas", "schema_person", "schema_service_product", "schema_faq"}
        assert ai_keys.issubset(skipped_keys), f"Expected AI keys in skipped, got: {skipped_keys}"
        assert not ai_keys.intersection(active_keys), f"AI keys should not be in active: {ai_keys & active_keys}"

    def test_wizytowka_skips_analytics(self):
        """Wizytowka skips analytics check."""
        checker = ReadinessChecker()
        project = _make_project(site_type="wizytowka")
        result = checker.check(project)

        skipped_keys = {c["key"] for c in result["skipped"]}
        assert "analytics" in skipped_keys

    def test_lp_produkt_warns_single_cta(self):
        """LP with only 1 CTA gets a warning."""
        checker = ReadinessChecker()
        project = _make_project(
            site_type="lp-produkt",
            sections=[
                _make_section("HE1", slots={"title": "Test", "cta_text": "Kup teraz"}),
                _make_section("OF1", slots={"title": "Oferta"}),
            ],
        )
        result = checker.check(project)

        cta_check = next((c for c in result["checks"] if c["key"] == "cta_present"), None)
        assert cta_check is not None
        assert cta_check["status"] == "warn"
        assert "minimum 2" in cta_check["message"].lower()

    def test_lp_produkt_passes_with_2_cta(self):
        """LP with 2+ CTAs passes."""
        checker = ReadinessChecker()
        project = _make_project(
            site_type="lp-produkt",
            sections=[
                _make_section("HE1", slots={"title": "Test", "cta_text": "Kup teraz"}),
                _make_section("CT1", slots={"title": "CTA", "button_text": "Zamów"}),
            ],
        )
        result = checker.check(project)

        cta_check = next((c for c in result["checks"] if c["key"] == "cta_present"), None)
        assert cta_check is not None
        assert cta_check["status"] == "pass"
        assert "2x" in cta_check["message"]

    def test_cv_skips_form_email_check(self):
        """CV readiness does not flag missing form email."""
        checker = ReadinessChecker()
        project = _make_project(site_type="cv")
        result = checker.check(project)

        skipped_keys = {c["key"] for c in result["skipped"]}
        assert "form_email" in skipped_keys

    def test_firmowa_runs_all_checks(self):
        """Firmowa gets all checks, nothing skipped."""
        checker = ReadinessChecker()
        project = _make_project(
            site_type="firmowa",
            sections=[_make_section("HE1", slots={"title": "Test"})],
        )
        result = checker.check(project)

        assert len(result["skipped"]) == 0
        assert len(result["checks"]) > 15  # All 21+ checks

    def test_skipped_checks_have_correct_format(self):
        """Skipped checks have key, status='skip', message."""
        checker = ReadinessChecker()
        project = _make_project(site_type="wizytowka")
        result = checker.check(project)

        for s in result["skipped"]:
            assert "key" in s
            assert s["status"] == "skip"
            assert "message" in s
            assert "Wizyt" in s["message"]

    def test_can_publish_respects_filtered_checks(self):
        """can_publish only considers non-skipped checks."""
        checker = ReadinessChecker()
        # CV with privacy policy (the only error check for CV after skipping)
        project = _make_project(
            site_type="cv",
            sections=[_make_section("HE1", slots={"title": "Test"})],
            config_json={"legal": {"privacy_policy": {"source": "ai", "html": "<p>OK</p>"}}},
        )
        result = checker.check(project)

        # Should be publishable since privacy_policy is present
        assert result["can_publish"] is True
