"""
Testy serwisow — Renderer, Separators, Infographics, SiteStructure.
"""

import pytest

from app.services.creator.renderer import BlockRenderer, _build_section_style, _get_bg_color
from app.services.creator.separators import get_separator_svg, SEPARATORS
from app.services.creator.infographics import get_infographic_template, get_available_templates
from app.services.creator.site_structure import get_structure_config, STRUCTURE_CONFIG, SITE_TYPES


# ─── BlockRenderer ───

class TestBlockRenderer:

    def setup_method(self):
        self.renderer = BlockRenderer()

    def test_simple_slot_replacement(self):
        template = "<h1>{{heading}}</h1><p>{{body}}</p>"
        result = self.renderer.render_block(template, {"heading": "Witaj", "body": "Opis"})
        assert "<h1>Witaj</h1>" in result
        assert "<p>Opis</p>" in result

    def test_html_escape(self):
        template = "<p>{{text}}</p>"
        result = self.renderer.render_block(template, {"text": '<script>alert("XSS")</script>'})
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_loop_rendering(self):
        template = '<ul>{{#each items}}<li>{{this.name}}</li>{{/each}}</ul>'
        result = self.renderer.render_block(template, {
            "items": [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        })
        assert "<li>A</li>" in result
        assert "<li>B</li>" in result
        assert "<li>C</li>" in result

    def test_loop_empty(self):
        template = '<ul>{{#each items}}<li>{{this.name}}</li>{{/each}}</ul>'
        result = self.renderer.render_block(template, {"items": []})
        assert "<li>" not in result

    def test_condition_true(self):
        template = '{{#if cta_text}}<a>{{cta_text}}</a>{{/if}}'
        result = self.renderer.render_block(template, {"cta_text": "Kliknij"})
        assert "<a>Kliknij</a>" in result

    def test_condition_false(self):
        template = '{{#if cta_text}}<a>{{cta_text}}</a>{{/if}}'
        result = self.renderer.render_block(template, {})
        assert "<a>" not in result

    def test_unrealized_slots_cleaned(self):
        template = "<p>{{text}} {{missing_slot}}</p>"
        result = self.renderer.render_block(template, {"text": "Hello"})
        assert "Hello" in result
        assert "{{missing_slot}}" not in result

    def test_nested_loop_with_condition(self):
        template = '{{#each items}}{{#if this.active}}<span>{{this.name}}</span>{{/if}}{{/each}}'
        result = self.renderer.render_block(template, {
            "items": [
                {"name": "Aktywny", "active": "true"},
                {"name": "Nieaktywny", "active": ""},
            ]
        })
        assert "Aktywny" in result
        assert "Nieaktywny" not in result

    def test_numeric_slot(self):
        template = "<span>{{count}}</span>"
        result = self.renderer.render_block(template, {"count": 42})
        assert "<span>42</span>" in result


# ─── Visual Concept Styles ───

class TestVisualConceptStyles:

    def test_bg_color_white(self):
        assert _get_bg_color({"bg_type": "white"}) == "#ffffff"

    def test_bg_color_light_gray(self):
        assert _get_bg_color({"bg_type": "light_gray"}) == "#f3f4f6"

    def test_bg_color_dark(self):
        assert _get_bg_color({"bg_type": "dark"}) == "#1a1a2e"

    def test_bg_color_custom(self):
        assert _get_bg_color({"bg_type": "brand_color", "bg_value": "#FF0000"}) == "#FF0000"

    def test_build_style_white(self):
        style = _build_section_style({"bg_type": "white"})
        assert "background-color:#ffffff" in style

    def test_build_style_brand_color(self):
        style = _build_section_style({"bg_type": "brand_color", "bg_value": "#4F46E5"})
        assert "#4F46E5" in style

    def test_build_style_gradient(self):
        style = _build_section_style({"bg_type": "brand_gradient", "bg_value": "#4F46E5"})
        assert "linear-gradient" in style

    def test_build_style_dark_overlay_with_photo(self):
        style = _build_section_style({
            "bg_type": "dark_photo_overlay",
            "bg_value": "#4F46E5CC",
            "photo_query": "business team",
            "resolved_photo_url": "https://images.unsplash.com/photo-123?w=1600",
        })
        assert "url(" in style
        assert "images.unsplash.com" in style

    def test_build_style_dark_overlay_no_photo(self):
        style = _build_section_style({"bg_type": "dark_photo_overlay"})
        assert "#1a1a2e" in style


# ─── Separators ───

class TestSeparators:

    def test_all_separator_types_exist(self):
        for stype in ["wave", "diagonal", "curve", "zigzag", "triangle"]:
            assert stype in SEPARATORS

    def test_get_separator_svg(self):
        svg = get_separator_svg("wave", "#ffffff", "#f3f4f6")
        assert svg != ""
        assert "<svg" in svg
        assert "#ffffff" in svg
        assert "#f3f4f6" in svg

    def test_get_separator_colors_replaced(self):
        svg = get_separator_svg("diagonal", "#FF0000", "#00FF00")
        assert "#FF0000" in svg
        assert "#00FF00" in svg
        assert "var(--color-top" not in svg

    def test_get_separator_unknown_type(self):
        svg = get_separator_svg("nonexistent", "#fff", "#000")
        assert svg == ""

    def test_each_separator_has_svg_tag(self):
        for name, svg in SEPARATORS.items():
            assert "<svg" in svg, f"Separator '{name}' brak <svg>"
            assert "</svg>" in svg, f"Separator '{name}' brak </svg>"


# ─── Infographics ───

class TestInfographics:

    def test_all_templates_available(self):
        templates = get_available_templates()
        expected = [
            "steps_horizontal", "steps_vertical",
            "numbers_row", "numbers_cards",
            "before_after", "timeline",
            "icons_grid", "process_circle",
        ]
        for t in expected:
            assert t in templates, f"Brak template: {t}"

    def test_get_template(self):
        html = get_infographic_template("steps_horizontal")
        assert html != ""
        assert "{{#each steps}}" in html

    def test_get_template_unknown(self):
        assert get_infographic_template("nonexistent") == ""

    def test_numbers_row_has_slots(self):
        html = get_infographic_template("numbers_row")
        assert "{{this.value}}" in html
        assert "{{this.label}}" in html

    def test_before_after_has_slots(self):
        html = get_infographic_template("before_after")
        assert "{{before_title}}" in html
        assert "{{after_title}}" in html

    def test_timeline_has_slots(self):
        html = get_infographic_template("timeline")
        assert "{{this.year}}" in html
        assert "{{this.title}}" in html


# ─── Site Structure Config ───

class TestSiteStructure:

    def test_all_site_types(self):
        for st in ["company_card", "company", "lp_product", "lp_service", "expert"]:
            assert st in STRUCTURE_CONFIG

    def test_company_card_limits(self):
        config = get_structure_config("company_card")
        assert config["max_sections"] == 6
        assert "NA" in config["required"]
        assert "HE" in config["required"]
        assert "KO" in config["required"]
        assert "FA" in config["forbidden"]

    def test_company_no_forbidden(self):
        config = get_structure_config("company")
        assert config["forbidden"] == []
        assert config["max_sections"] == 12

    def test_lp_forbidden_ze(self):
        config = get_structure_config("lp_product")
        assert "ZE" in config["forbidden"]

    def test_site_types_list(self):
        assert len(SITE_TYPES) >= 5
        values = [t["value"] for t in SITE_TYPES]
        assert "company_card" in values
        assert "expert" in values

    def test_get_config_fallback(self):
        config = get_structure_config("unknown_type")
        assert config["max_sections"] == 12  # falls back to "company"
