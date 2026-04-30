"""
Tests for offer AI — prompts, GUS client, text templates, personalization.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.offer.ai_prompts import PARSE_EMAIL_PROMPT, PERSONALIZE_TEXT_PROMPT
from app.services.offer.ai_service import OfferAIService
from app.services.offer.gus_client import _extract_xml_value, lookup_by_nip


class TestPrompts:
    def test_parse_email_prompt(self):
        result = PARSE_EMAIL_PROMPT.format(email_text="Test email")
        assert "Test email" in result
        assert "confidence" in result

    def test_personalize_prompt(self):
        result = PERSONALIZE_TEXT_PROMPT.format(
            template_text="Hej", company_name="X", contact_person="Y",
            contact_role="Z", occasion_name="BN", quantity=100, sets_summary="a",
        )
        assert "X" in result


class TestGusXml:
    def test_extract_tag(self):
        assert _extract_xml_value("<r><Regon>123</Regon></r>", "Regon") == "123"

    def test_extract_missing(self):
        assert _extract_xml_value("<r><Other>x</Other></r>", "Regon") is None

    def test_extract_empty(self):
        assert _extract_xml_value("<r><Regon></Regon></r>", "Regon") is None


class TestGusValidation:
    @pytest.mark.asyncio
    async def test_invalid_nip(self):
        result = await lookup_by_nip("123")
        assert result["found"] is False

    @pytest.mark.asyncio
    async def test_nip_non_digits(self):
        result = await lookup_by_nip("abcdefghij")
        assert result["found"] is False


class TestSetsSummary:
    def test_with_data(self):
        sets = [{"name": "A", "unit_price": 100, "items": [{"product_id": "w1"}]}]
        products = {"w1": {"name": "Wino", "category": "wine"}}
        result = OfferAIService.build_sets_summary(sets, products)
        assert "A" in result and "Wino" in result

    def test_empty(self):
        assert "Brak" in OfferAIService.build_sets_summary([], {})


class TestPersonalize:
    @pytest.mark.asyncio
    async def test_simple_replacement(self):
        service = OfferAIService.__new__(OfferAIService)
        result = await service.personalize_text(
            template_text="Oferta dla {company_name}, {quantity} szt.",
            company_name="TestCorp", quantity=100,
        )
        assert "TestCorp" in result
        assert "100" in result

    @pytest.mark.asyncio
    async def test_defaults_when_empty(self):
        service = OfferAIService.__new__(OfferAIService)
        result = await service.personalize_text(
            template_text="Dla {company_name}.", company_name="",
        )
        assert "Państwa firma" in result


class TestParseEmailMocked:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_resp = MagicMock()
        mock_resp.data = {"client": {"company_name": "FC"}, "confidence": 90}
        service = OfferAIService.__new__(OfferAIService)
        with patch.object(service, 'claude', create=True) as mc:
            mc.complete_json = AsyncMock(return_value=mock_resp)
            result = await service.parse_email("Test")
        assert result["confidence"] == 90
