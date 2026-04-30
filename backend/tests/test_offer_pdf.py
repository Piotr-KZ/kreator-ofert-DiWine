"""
Tests for offer PDF generation.
"""

import pytest
from app.services.offer.pdf_template import render_offer_pdf_html, _format_price


class TestPdfTemplate:
    def test_format_price(self):
        assert _format_price(1234.50) == "1 234,50"
        assert _format_price(0) == "0,00"
        assert _format_price(99.99) == "99,99"

    def test_render_basic_html(self):
        """Render minimal offer and check HTML contains key elements."""
        html = render_offer_pdf_html(
            offer={
                "offer_number": "OF/2026/05/0001",
                "quantity": 100,
                "occasion_code": "christmas",
                "deadline": "2026-11-20",
                "delivery_address": "Warszawa",
                "expires_at": "2026-06-15",
            },
            client={
                "company_name": "TestCorp",
                "nip": "1234567890",
                "contact_person": "Jan Testowy",
                "email": "jan@test.pl",
            },
            sets=[
                {
                    "name": "Wariant Premium",
                    "packaging_id": "pkg1",
                    "budget_per_unit": 150,
                    "unit_price": 120.50,
                    "total_price": 12050.00,
                    "items": [
                        {"product_id": "w1", "item_type": "wine", "color_code": "czerwone", "unit_price": 76.48},
                        {"product_id": "s1", "item_type": "sweet", "color_code": "red", "unit_price": 8.50},
                    ],
                },
            ],
            products={
                "w1": {"id": "w1", "name": "Jagoda Kamczacka", "category": "wine", "base_price": 80.50, "wine_color": "czerwone", "wine_type": "półsłodkie"},
                "s1": {"id": "s1", "name": "Pierniczek", "category": "sweet", "base_price": 8.50},
            },
            packagings={
                "pkg1": {"id": "pkg1", "name": "Pudełko czarne Premium", "price": 26.00, "bottles": 1, "sweet_slots": 5},
            },
            colors=[
                {"code": "red", "name": "Czerwony", "hex_value": "#DC2626"},
            ],
            occasion_name="Boże Narodzenie",
            wine_discount_percent=5.0,
        )

        # Check key content is present
        assert "OFERTA" in html
        assert "OF/2026/05/0001" in html
        assert "TestCorp" in html
        assert "1234567890" in html
        assert "Wariant Premium" in html
        assert "Jagoda Kamczacka" in html
        assert "Pierniczek" in html
        assert "Boże Narodzenie" in html
        assert "100 szt." in html
        assert "jan@test.pl" in html

    def test_render_multiple_sets(self):
        """Multiple sets should all appear in HTML."""
        html = render_offer_pdf_html(
            offer={"offer_number": "OF/2026/05/0002", "quantity": 50},
            client={"company_name": "MultiCorp"},
            sets=[
                {"name": "Set A", "unit_price": 100, "total_price": 5000, "items": []},
                {"name": "Set B", "unit_price": 80, "total_price": 4000, "items": []},
                {"name": "Set C", "unit_price": 60, "total_price": 3000, "items": []},
            ],
            products={},
            packagings={},
            colors=[],
            occasion_name="Wielkanoc",
            wine_discount_percent=10.0,
        )

        assert "Set A" in html
        assert "Set B" in html
        assert "Set C" in html
        assert "MultiCorp" in html

    def test_render_empty_offer(self):
        """Empty offer (no sets) should still render valid HTML."""
        html = render_offer_pdf_html(
            offer={"offer_number": "OF/2026/05/0003", "quantity": 1},
            client={"company_name": "EmptyCorp"},
            sets=[],
            products={},
            packagings={},
            colors=[],
            occasion_name="Uniwersalny",
            wine_discount_percent=0,
        )

        assert "<!DOCTYPE html>" in html
        assert "OFERTA" in html
        assert "EmptyCorp" in html
