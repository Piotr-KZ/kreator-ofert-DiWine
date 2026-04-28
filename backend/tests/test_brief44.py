"""
Tests for Brief 44 — infrastructure: ProjectContext, Unsplash, Canva, Lucide icons, validation.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import Response

from app.services.ai.context import ProjectContext
from app.services.creator.icons import LUCIDE_ICONS, get_icon_svg
from app.services.media.canva import CanvaService
from app.services.media.unsplash import UnsplashService


# ─── Mock Project for ProjectContext tests ───

def _make_mock_section(id, block_code, position, slots_json=None):
    s = MagicMock()
    s.id = id
    s.block_code = block_code
    s.position = position
    s.slots_json = slots_json
    return s


def _make_mock_project(sections=None, brief=None, style=None, site_type="company_card"):
    p = MagicMock()
    p.brief_json = brief or {
        "description": "Firma szkoleniowa outdoor",
        "target_audience": "Menedzerowie firm",
        "usp": "Unikatowe poligony szkoleniowe",
        "tone": "profesjonalny",
    }
    p.style_json = style or {"primary_color": "#2563EB", "secondary_color": "#F59E0B"}
    p.site_type = site_type
    p.sections = sections or []
    p.visual_concept_json = {}
    return p


# ─── ProjectContext Tests (4) ───

class TestProjectContext:

    def test_context_for_validation_has_brief(self):
        """Context for validation contains description, audience, USP, tone."""
        project = _make_mock_project()
        ctx = ProjectContext(project)
        result = ctx.for_validation()
        assert "Firma szkoleniowa outdoor" in result
        assert "Menedzerowie firm" in result
        assert "Unikatowe poligony" in result
        assert "profesjonalny" in result

    def test_context_for_content_has_neighbors(self):
        """Content context contains previous and next section info."""
        sections = [
            _make_mock_section("s1", "NA1", 0),
            _make_mock_section("s2", "HE1", 1, {"heading": "Hero naglowek"}),
            _make_mock_section("s3", "OF1", 2),
        ]
        project = _make_mock_project(sections=sections)
        ctx = ProjectContext(project)
        result = ctx.for_content(sections[1])  # HE1

        assert "NA1" in result  # previous section
        assert "OF1" in result  # next section
        assert "pozycja 2 z 3" in result

    def test_context_for_content_has_visual_hints(self):
        """Content context contains visual hints for AI."""
        sections = [_make_mock_section("s1", "OF1", 0)]
        project = _make_mock_project(sections=sections)
        ctx = ProjectContext(project)
        result = ctx.for_content(sections[0])

        assert "ikony Lucide" in result
        assert "OPIS zdjecia" in result

    def test_context_for_visual_has_content_counts(self):
        """Visual context contains item counts per section."""
        sections = [
            _make_mock_section("s1", "OF1", 0, {
                "heading": "Oferta",
                "services": [{"title": "A"}, {"title": "B"}, {"title": "C"}],
            }),
        ]
        project = _make_mock_project(sections=sections)
        ctx = ProjectContext(project)
        result = ctx.for_visual()

        assert '"items_count": 3' in result
        assert "Oferta" in result


# ─── Unsplash Tests (3) ───

class TestUnsplash:

    @pytest.fixture(autouse=True)
    def _clear_unsplash_cache(self):
        """Clear persistent cache before each test to avoid cross-contamination."""
        import app.services.media.unsplash as unsplash_mod
        unsplash_mod._persistent_cache.clear()
        yield
        unsplash_mod._persistent_cache.clear()

    def _mock_photo_result(self, photo_id: str, raw_url: str) -> dict:
        return {
            "id": photo_id,
            "urls": {"raw": raw_url},
            "user": {
                "name": "Test Photographer",
                "links": {"html": "https://unsplash.com/@test"},
            },
            "links": {"html": f"https://unsplash.com/photos/{photo_id}"},
        }

    @pytest.mark.asyncio
    async def test_unsplash_search_returns_url(self):
        """Search returns full photo dict with url and attribution (mocked API)."""
        service = UnsplashService()
        service.enabled = True
        service.api_key = "test_key"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"X-Ratelimit-Remaining": "49"}
        mock_response.json.return_value = {
            "results": [self._mock_photo_result("photo-123", "https://images.unsplash.com/photo-123")]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.media.unsplash.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await service.search_photo("business team professional")
            assert result is not None
            assert "images.unsplash.com" in result["url"]
            assert "w=1200" in result["url"]
            assert result["photo_id"] == "photo-123"
            assert result["photographer_name"] == "Test Photographer"
            assert "utm_source=lab_creator" in result["photographer_url"]

    @pytest.mark.asyncio
    async def test_unsplash_photo_for_section_wide(self):
        """photo_wide → landscape orientation, 1600px width."""
        service = UnsplashService()
        service.enabled = True
        service.api_key = "test_key"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"X-Ratelimit-Remaining": "48"}
        mock_response.json.return_value = {
            "results": [self._mock_photo_result("photo-456", "https://images.unsplash.com/photo-456")]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.media.unsplash.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await service.get_photo_for_section("office", "photo_wide")
            assert result is not None
            assert "w=1600" in result["url"]
            assert result["photo_id"] == "photo-456"

            # Verify the API was called with correct orientation
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["orientation"] == "landscape"

    @pytest.mark.asyncio
    async def test_unsplash_photo_for_section_avatar(self):
        """avatars → squarish orientation, 200px width."""
        service = UnsplashService()
        service.enabled = True
        service.api_key = "test_key"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"X-Ratelimit-Remaining": "47"}
        mock_response.json.return_value = {
            "results": [self._mock_photo_result("photo-789", "https://images.unsplash.com/photo-789")]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.media.unsplash.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await service.get_photo_for_section("person portrait", "avatars")
            assert result is not None
            assert "w=200" in result["url"]
            assert result["photo_id"] == "photo-789"
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["orientation"] == "squarish"


# ─── Canva Tests (2) ───

class TestCanva:

    @pytest.mark.asyncio
    async def test_canva_disabled_returns_none(self):
        """When CANVA_MCP_ENABLED=false, returns None."""
        service = CanvaService()
        service.enabled = False

        result = await service.create_design(
            template_type="banner",
            text_content={"title": "Test"},
            brand_colors=["#2563eb"],
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_canva_create_design_interface(self):
        """create_design accepts correct parameters."""
        service = CanvaService()
        service.enabled = False

        result = await service.create_infographic(
            infographic_type="steps",
            data={"steps": [{"title": "Step 1"}]},
            brand_colors=["#2563eb"],
        )
        assert result is None  # stub always returns None


# ─── Lucide Icons Tests (2) ───

class TestLucideIcons:

    def test_get_icon_svg_known(self):
        """get_icon_svg('Target') returns valid SVG string."""
        svg = get_icon_svg("Target")
        assert svg.startswith("<svg")
        assert "circle" in svg.lower()
        assert 'width="24"' in svg

    def test_get_icon_svg_unknown_fallback(self):
        """get_icon_svg('NonExistent') returns Circle fallback."""
        svg = get_icon_svg("NieIstniejaca")
        fallback = LUCIDE_ICONS["Circle"]
        assert svg == fallback

    def test_get_icon_svg_custom_size(self):
        """get_icon_svg with custom size replaces width/height."""
        svg = get_icon_svg("Target", size=32)
        assert 'width="32"' in svg
        assert 'height="32"' in svg

    def test_get_icon_svg_custom_color(self):
        """get_icon_svg with custom color replaces stroke."""
        svg = get_icon_svg("Target", color="#FF0000")
        assert 'stroke="#FF0000"' in svg

    def test_get_icon_svg_case_insensitive(self):
        """get_icon_svg('users') matches 'Users' (case-insensitive)."""
        svg_lower = get_icon_svg("users")
        svg_pascal = get_icon_svg("Users")
        assert svg_lower == svg_pascal
        assert svg_lower.startswith("<svg")

    def test_get_icon_svg_case_insensitive_multi_word(self):
        """get_icon_svg('barchart') matches 'BarChart'."""
        svg = get_icon_svg("barchart")
        expected = get_icon_svg("BarChart")
        assert svg == expected
        assert "line" in svg.lower()


# ─── Validation Endpoint Test (1) ───

class TestValidationEndpoint:

    @pytest.mark.asyncio
    async def test_validate_brief_endpoint(self, client, sample_project, mock_claude_json):
        """POST /validate-brief returns list of items with type/message."""
        # First patch complete_json for validation response
        from app.services.ai.types import ClaudeJsonResponse
        mock_items = [
            {"type": "ok", "message": "Opis jest konkretny"},
            {"type": "warning", "message": "Grupa docelowa za ogolna", "field": "target_audience", "suggestion": "Lepszy opis"},
        ]

        async def mock_validate(self, system, user_message, max_retries=3):
            return ClaudeJsonResponse(
                data=mock_items,
                raw_text=json.dumps(mock_items),
                tokens_in=100, tokens_out=200,
                model="test", duration_ms=100,
            )

        with patch("app.services.ai.claude_client.ClaudeClient.complete_json", mock_validate):
            resp = await client.post(f"/api/v1/projects/{sample_project.id}/validate-brief")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            items = data["items"]
            assert len(items) == 2
            assert items[0]["type"] == "ok"
            assert items[1]["type"] == "warning"
            assert items[1]["field"] == "target_audience"
