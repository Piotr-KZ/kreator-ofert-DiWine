"""
Tests for offer page templates and builder.
"""

import pytest
from app.services.offer.page_templates import list_templates, get_template


class TestPageTemplates:
    def test_list_templates_returns_4(self):
        templates = list_templates()
        assert len(templates) == 4

    def test_list_templates_has_names(self):
        templates = list_templates()
        names = [t["name"] for t in templates]
        assert "Standard" in names
        assert "Premium" in names
        assert "Szybka wycena" in names
        assert "Prezentacyjna" in names

    def test_get_template_standard(self):
        tpl = get_template("standard")
        assert tpl is not None
        assert tpl["name"] == "Standard"
        assert len(tpl["blocks"]) >= 5

    def test_get_template_unknown(self):
        assert get_template("nonexistent") is None

    def test_standard_has_required_blocks(self):
        tpl = get_template("standard")
        codes = [b["block_code"] for b in tpl["blocks"]]
        assert "NO1" in codes  # header
        assert "DW1" in codes  # set (repeated)
        assert "CTA1" in codes  # CTA

    def test_quick_is_shortest(self):
        quick = get_template("quick")
        standard = get_template("standard")
        assert len(quick["blocks"]) < len(standard["blocks"])

    def test_premium_has_fun_facts(self):
        tpl = get_template("premium")
        text_sources = []
        for b in tpl["blocks"]:
            for v in (b.get("slots_map") or {}).values():
                if isinstance(v, str) and "fun_fact" in v:
                    text_sources.append(v)
        assert len(text_sources) >= 1

    def test_all_templates_have_cta(self):
        for tid in ["standard", "premium", "quick", "presentation"]:
            tpl = get_template(tid)
            codes = [b["block_code"] for b in tpl["blocks"]]
            assert "CTA1" in codes, f"{tid} brakuje CTA"
