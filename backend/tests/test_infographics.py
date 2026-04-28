"""Tests for infographics (20 templates) and illustrations (30 SVGs)."""
import pytest


def test_all_20_templates_exist():
    from app.services.creator.infographics import get_available_templates
    templates = get_available_templates()
    assert len(templates) == 20


def test_template_has_slots():
    from app.services.creator.infographics import get_infographic_template
    tmpl = get_infographic_template("steps_horizontal")
    assert "{{#each steps}}" in tmpl
    assert "{{this.title}}" in tmpl


def test_categories_cover_all():
    from app.services.creator.infographics import get_template_categories, get_available_templates
    cats = get_template_categories()
    all_in_cats = [t for templates in cats.values() for t in templates]
    assert set(all_in_cats) == set(get_available_templates())


def test_all_30_illustrations_exist():
    from app.services.creator.illustrations import get_available_illustrations
    illustrations = get_available_illustrations()
    assert len(illustrations) == 30


def test_illustration_svg_returns_svg():
    from app.services.creator.illustrations import get_illustration_svg
    svg = get_illustration_svg("target")
    assert svg.startswith("<svg")
    assert 'stroke="currentColor"' in svg


def test_illustration_color_override():
    from app.services.creator.illustrations import get_illustration_svg
    svg = get_illustration_svg("shield", color="#FF0000")
    assert 'stroke="#FF0000"' in svg
    assert 'stroke="currentColor"' not in svg


def test_illustration_not_found_returns_empty():
    from app.services.creator.illustrations import get_illustration_svg
    svg = get_illustration_svg("nonexistent")
    assert svg == ""


def test_illustration_case_insensitive():
    from app.services.creator.illustrations import get_illustration_svg
    assert get_illustration_svg("Chart-Up") != ""
    assert get_illustration_svg("chart_up") != ""
    assert get_illustration_svg("CHART-UP") != ""
