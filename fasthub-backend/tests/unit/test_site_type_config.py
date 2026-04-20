"""
Tests for Brief 42: site_type_config module — per-type customization.
15 unit tests (no DB needed).
"""

import pytest
from app.services.creator.site_type_config import (
    SITE_TYPE_CONFIGS,
    SiteTypeConfig,
    get_all_site_types,
    get_prompt_hint,
    get_site_type_config,
    to_api_dict,
)

# Known check keys from ReadinessChecker
VALID_CHECK_KEYS = {
    "sections_filled", "headings", "alt_texts", "cta_present",
    "mobile_responsive", "form_email", "sitemap_possible", "page_speed",
    "privacy_policy", "cookie_banner", "rodo",
    "meta_title", "meta_description", "og_tags", "analytics",
    "wcag_contrast", "wcag_alt_texts", "schema_markup", "wcag_heading_hierarchy",
    "wcag_form_accessibility", "wcag_secondary_contrast",
    "llms_txt_ready", "schema_sameas", "schema_person",
    "schema_service_product", "schema_faq", "ai_experience_check",
}

# Valid block category codes
VALID_BLOCK_CATEGORIES = {
    "NA", "HE", "FI", "OF", "CE", "ZE", "OP", "FA", "CT", "KO", "FO",
    "GA", "RE", "PR", "PB", "RO", "KR", "CF", "OB", "LO", "ST",
}

VALID_PROMPT_STAGES = {
    "generate_structure", "generate_section_content", "validate_consistency",
}


class TestSiteTypeConfigRegistry:
    """Tests for the SITE_TYPE_CONFIGS dictionary."""

    def test_all_frontend_types_have_config(self):
        """Every type from SITE_TYPES_FIRMA + SITE_TYPES_OSOBA has a config entry."""
        expected_firma = [
            "firmowa", "korporacyjna", "blog", "firmowa-blog", "korporacyjna-blog",
            "lp-produkt", "lp-usluga", "lp-wydarzenie", "lp-webinar",
            "lp-wizerunkowa", "lp-lead", "wizytowka",
        ]
        expected_osoba = ["ekspert", "portfolio", "cv", "wizytowka-osoba"]

        for t in expected_firma:
            assert t in SITE_TYPE_CONFIGS, f"Missing config for firma type: {t}"
        for t in expected_osoba:
            # blog-osoba maps to "blog-osoba" in config (not "blog" from frontend SITE_TYPES_OSOBA)
            if t == "blog":
                continue
            assert t in SITE_TYPE_CONFIGS, f"Missing config for osoba type: {t}"

    def test_config_count(self):
        """Should have at least 16 site type configs."""
        assert len(SITE_TYPE_CONFIGS) >= 16

    def test_get_unknown_type_returns_fallback(self):
        """Unknown type returns firmowa defaults."""
        config = get_site_type_config("nieznany-typ")
        assert config.site_type == "firmowa"

    def test_get_none_returns_fallback(self):
        """None type returns firmowa defaults."""
        config = get_site_type_config(None)
        assert config.site_type == "firmowa"

    def test_get_known_type(self):
        """Known type returns correct config."""
        config = get_site_type_config("wizytowka")
        assert config.site_type == "wizytowka"
        assert config.label == "Wizytówka"


class TestSiteTypeConfigStructure:
    """Tests for the structure of each SiteTypeConfig."""

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_recommended_blocks_start_with_NA_end_with_FO(self, site_type):
        """Every type's recommended blocks start with NA and end with FO."""
        config = SITE_TYPE_CONFIGS[site_type]
        assert config.recommended_blocks[0] == "NA", f"{site_type}: should start with NA"
        assert config.recommended_blocks[-1] == "FO", f"{site_type}: should end with FO"

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_min_sections_lte_max_sections(self, site_type):
        """min_sections <= max_sections for all types."""
        config = SITE_TYPE_CONFIGS[site_type]
        assert config.min_sections <= config.max_sections

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_brief_sections_always_include_s1(self, site_type):
        """All types show s1 (type picker)."""
        config = SITE_TYPE_CONFIGS[site_type]
        assert "s1" in config.brief_sections

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_allowed_categories_subset_of_valid(self, site_type):
        """All allowed category codes are valid block categories."""
        config = SITE_TYPE_CONFIGS[site_type]
        if config.allowed_block_categories:
            invalid = set(config.allowed_block_categories) - VALID_BLOCK_CATEGORIES
            assert not invalid, f"{site_type}: invalid categories: {invalid}"

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_readiness_skip_checks_are_valid_keys(self, site_type):
        """Skip check keys match real check keys."""
        config = SITE_TYPE_CONFIGS[site_type]
        if config.readiness_skip_checks:
            invalid = set(config.readiness_skip_checks) - VALID_CHECK_KEYS
            assert not invalid, f"{site_type}: invalid skip checks: {invalid}"

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_prompt_hints_keys_are_valid_stages(self, site_type):
        """Prompt hint keys match valid engine stages."""
        config = SITE_TYPE_CONFIGS[site_type]
        if config.prompt_hints:
            invalid = set(config.prompt_hints.keys()) - VALID_PROMPT_STAGES
            assert not invalid, f"{site_type}: invalid prompt stages: {invalid}"

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_style_presets_have_3_colors(self, site_type):
        """Each style preset has exactly 3 colors."""
        config = SITE_TYPE_CONFIGS[site_type]
        for preset in config.style_presets:
            assert len(preset["colors"]) == 3, f"{site_type}/{preset['id']}: should have 3 colors"

    @pytest.mark.parametrize("site_type", list(SITE_TYPE_CONFIGS.keys()))
    def test_category_is_firma_or_osoba(self, site_type):
        """Category is 'firma' or 'osoba'."""
        config = SITE_TYPE_CONFIGS[site_type]
        assert config.category in ("firma", "osoba")


class TestSiteTypeConfigHelpers:
    """Tests for helper functions."""

    def test_get_prompt_hint_existing(self):
        """Returns hint for existing stage."""
        hint = get_prompt_hint("lp-produkt", "generate_structure")
        assert "konwersj" in hint.lower()

    def test_get_prompt_hint_missing_stage(self):
        """Returns empty string for unknown stage."""
        hint = get_prompt_hint("firmowa", "nonexistent_stage")
        assert hint == ""

    def test_get_all_site_types_returns_list(self):
        """Returns list of dicts with expected keys."""
        types = get_all_site_types()
        assert len(types) >= 16
        for t in types:
            assert "site_type" in t
            assert "label" in t
            assert "category" in t

    def test_to_api_dict_serialization(self):
        """Serializes SiteTypeConfig to dict correctly."""
        config = get_site_type_config("wizytowka")
        d = to_api_dict(config)
        assert isinstance(d, dict)
        assert d["site_type"] == "wizytowka"
        assert d["min_sections"] == 3
        assert isinstance(d["recommended_blocks"], list)
        assert isinstance(d["style_presets"], list)


class TestSiteTypeSpecificRules:
    """Tests for specific type rules."""

    def test_wizytowka_minimal_blocks(self):
        """Wizytowka has exactly 4 blocks, max 6 sections."""
        config = get_site_type_config("wizytowka")
        assert len(config.recommended_blocks) == 4
        assert config.max_sections == 6

    def test_lp_types_have_cta_modify_rule(self):
        """All lp-* types have cta_present override with min 2."""
        lp_types = [k for k in SITE_TYPE_CONFIGS if k.startswith("lp-")]
        assert len(lp_types) >= 6
        for t in lp_types:
            config = SITE_TYPE_CONFIGS[t]
            assert "cta_present" in config.readiness_modify_checks, f"{t}: missing cta_present rule"
            assert config.readiness_modify_checks["cta_present"]["min_cta_count"] == 2

    def test_cv_skips_form_email(self):
        """CV type skips form_email check."""
        config = get_site_type_config("cv")
        assert "form_email" in config.readiness_skip_checks

    def test_wizytowka_skips_ai_visibility(self):
        """Wizytowka skips all AI Visibility checks."""
        config = get_site_type_config("wizytowka")
        ai_checks = {"llms_txt_ready", "schema_sameas", "schema_person", "schema_service_product", "schema_faq"}
        skipped = set(config.readiness_skip_checks)
        assert ai_checks.issubset(skipped), f"Wizytowka should skip AI checks, missing: {ai_checks - skipped}"

    def test_firmowa_has_no_skip_checks(self):
        """Firmowa runs all checks — no skips."""
        config = get_site_type_config("firmowa")
        assert config.readiness_skip_checks == []
