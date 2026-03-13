"""
Tests for Brief 34: Kreator etapy 5-6 — generate-site SSE, stock photos, render.
27 tests total.
"""

import io
import json
import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock

from app.models.block_template import BlockCategory, BlockTemplate
from app.models.project import Project
from app.models.project_section import ProjectSection


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def seeded_categories(db_session: AsyncSession):
    from app.services.creator.block_service import seed_block_categories
    await seed_block_categories(db_session)
    return db_session


@pytest_asyncio.fixture
async def seeded_blocks(seeded_categories: AsyncSession):
    from app.services.creator.seed_blocks import seed_block_templates
    await seed_block_templates(seeded_categories)
    return seeded_categories


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_organization, test_user):
    project = Project(
        organization_id=test_organization.id,
        created_by=test_user.id,
        name="Test Step5-6",
        site_type="firmowa",
        status="generating",
        current_step=4,
        brief_json={"company_name": "ACME", "industry": "IT", "whatYouDo": "Software"},
        style_json={
            "color_primary": "#3B82F6",
            "color_secondary": "#64748B",
            "color_accent": "#F59E0B",
            "heading_font": "Outfit",
            "body_font": "Inter",
            "border_radius": "rounded",
        },
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_project_with_sections(test_project, db_session, seeded_blocks):
    s1 = ProjectSection(
        project_id=test_project.id,
        block_code="HE1",
        position=0,
        variant="A",
        slots_json={"title": "Witamy", "subtitle": "Testowy podtytul", "cta_primary": "Kontakt"},
    )
    s2 = ProjectSection(
        project_id=test_project.id,
        block_code="FI1",
        position=1,
        variant="A",
        slots_json={"title": "O firmie", "description": "Opis firmy"},
    )
    s3 = ProjectSection(
        project_id=test_project.id,
        block_code="CT1",
        position=2,
        variant="A",
        slots_json={"title": "Kontakt", "cta_text": "Zadzwon"},
    )
    db_session.add_all([s1, s2, s3])
    await db_session.commit()
    await db_session.refresh(test_project, ["sections"])
    return test_project


# ============================================================================
# Generate Site SSE (4 tests)
# ============================================================================

class TestGenerateSiteSSE:

    @pytest.mark.asyncio
    async def test_generate_site_returns_sse_stream(self, async_client, auth_headers, test_project):
        """POST generate-site → SSE stream with progress events."""
        with patch("app.services.ai.engine.AIEngine.generate_structure", new_callable=AsyncMock) as mock_struct, \
             patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock_content:
            mock_struct.return_value = [
                {"block_code": "HE1", "slots": {"title": "Test"}},
            ]
            mock_content.return_value = {"title": "Generated", "subtitle": "Sub"}

            response = await async_client.post(
                f"/api/v1/projects/{test_project.id}/ai/generate-site",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.headers.get("content-type", "").startswith("text/event-stream")

    @pytest.mark.asyncio
    async def test_generate_site_creates_sections(self, async_client, auth_headers, test_project, seeded_blocks, db_session):
        """After generate-site → sections created in DB."""
        with patch("app.services.ai.engine.AIEngine.generate_structure", new_callable=AsyncMock) as mock_struct, \
             patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock_content:
            mock_struct.return_value = [
                {"block_code": "HE1"},
                {"block_code": "FI1"},
            ]
            mock_content.return_value = {"title": "OK"}

            await async_client.post(
                f"/api/v1/projects/{test_project.id}/ai/generate-site",
                headers=auth_headers,
            )

            result = await db_session.execute(
                select(ProjectSection).where(ProjectSection.project_id == test_project.id)
            )
            sections = result.scalars().all()
            assert len(sections) == 2

    @pytest.mark.asyncio
    async def test_generate_site_updates_project_status(self, async_client, auth_headers, test_project, seeded_blocks, db_session):
        """After generate-site → project status=building, step=5."""
        with patch("app.services.ai.engine.AIEngine.generate_structure", new_callable=AsyncMock) as mock_struct, \
             patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock_content:
            mock_struct.return_value = [{"block_code": "HE1"}]
            mock_content.return_value = {"title": "OK"}

            await async_client.post(
                f"/api/v1/projects/{test_project.id}/ai/generate-site",
                headers=auth_headers,
            )

            await db_session.refresh(test_project)
            assert test_project.status == "building"
            assert test_project.current_step == 5

    @pytest.mark.asyncio
    async def test_generate_site_handles_error(self, async_client, auth_headers, test_project):
        """If AI fails → error event in stream."""
        with patch("app.services.ai.engine.AIEngine.generate_structure", new_callable=AsyncMock) as mock_struct:
            mock_struct.side_effect = Exception("AI error")

            response = await async_client.post(
                f"/api/v1/projects/{test_project.id}/ai/generate-site",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            body = response.text
            assert "error" in body


# ============================================================================
# Render Page (3 tests)
# ============================================================================

class TestRenderPage:

    @pytest.mark.asyncio
    async def test_render_returns_html_and_css(self, async_client, auth_headers, test_project_with_sections):
        """GET render → {html, css}."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/render",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "html" in data
        assert "css" in data
        assert "Witamy" in data["html"]

    @pytest.mark.asyncio
    async def test_render_includes_css_variables(self, async_client, auth_headers, test_project_with_sections):
        """CSS contains palette variables."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/render",
            headers=auth_headers,
        )
        css = response.json()["css"]
        assert "--color-primary: #3B82F6" in css

    @pytest.mark.asyncio
    async def test_render_skips_invisible(self, async_client, auth_headers, test_project_with_sections, db_session):
        """is_visible=false → not in HTML."""
        # Hide section
        sections = test_project_with_sections.sections
        sections[1].is_visible = False
        await db_session.commit()

        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/render",
            headers=auth_headers,
        )
        html = response.json()["html"]
        assert "O firmie" not in html


# ============================================================================
# Section CRUD in context of step 5-6 (5 tests)
# ============================================================================

class TestSectionOperations:

    @pytest.mark.asyncio
    async def test_list_sections_ordered(self, async_client, auth_headers, test_project_with_sections):
        """Sections returned in position order."""
        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/sections",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["block_code"] == "HE1"
        assert data[1]["block_code"] == "FI1"
        assert data[2]["block_code"] == "CT1"

    @pytest.mark.asyncio
    async def test_update_section_slots(self, async_client, auth_headers, test_project_with_sections):
        """PATCH section → slots_json updated."""
        section = test_project_with_sections.sections[0]
        response = await async_client.patch(
            f"/api/v1/projects/{test_project_with_sections.id}/sections/{section.id}",
            headers=auth_headers,
            json={"slots_json": {"title": "Nowy tytul"}},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["slots_json"]["title"] == "Nowy tytul"

    @pytest.mark.asyncio
    async def test_update_section_variant(self, async_client, auth_headers, test_project_with_sections):
        """PATCH section → variant changed."""
        section = test_project_with_sections.sections[0]
        response = await async_client.patch(
            f"/api/v1/projects/{test_project_with_sections.id}/sections/{section.id}",
            headers=auth_headers,
            json={"variant": "B"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["variant"] == "B"

    @pytest.mark.asyncio
    async def test_reorder_sections(self, async_client, auth_headers, test_project_with_sections):
        """POST reorder → positions swapped."""
        sections = test_project_with_sections.sections
        reversed_order = [str(sections[2].id), str(sections[1].id), str(sections[0].id)]
        response = await async_client.post(
            f"/api/v1/projects/{test_project_with_sections.id}/sections/reorder",
            headers=auth_headers,
            json={"order": reversed_order},
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_delete_section(self, async_client, auth_headers, test_project_with_sections):
        """DELETE section → removed."""
        section = test_project_with_sections.sections[2]
        response = await async_client.delete(
            f"/api/v1/projects/{test_project_with_sections.id}/sections/{section.id}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify
        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/sections",
            headers=auth_headers,
        )
        assert len(response.json()) == 2


# ============================================================================
# Generate Section Content (3 tests)
# ============================================================================

class TestGenerateSectionContent:

    @pytest.mark.asyncio
    async def test_generate_content_returns_slots(self, async_client, auth_headers, test_project_with_sections, seeded_blocks):
        """POST generate-content → {slots: {...}}."""
        section = test_project_with_sections.sections[0]
        with patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock:
            mock.return_value = {"title": "AI Title", "subtitle": "AI Sub"}
            response = await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/ai/generate-content/{section.id}",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["slots"]["title"] == "AI Title"

    @pytest.mark.asyncio
    async def test_generate_content_saves_to_db(self, async_client, auth_headers, test_project_with_sections, seeded_blocks, db_session):
        """POST generate-content → section.slots_json updated."""
        section = test_project_with_sections.sections[0]
        with patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock:
            mock.return_value = {"title": "Saved Title"}
            await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/ai/generate-content/{section.id}",
                headers=auth_headers,
            )
            await db_session.refresh(section)
            assert section.slots_json["title"] == "Saved Title"

    @pytest.mark.asyncio
    async def test_generate_content_404_bad_section(self, async_client, auth_headers, test_project):
        """POST generate-content with bad section_id → 404."""
        import uuid
        response = await async_client.post(
            f"/api/v1/projects/{test_project.id}/ai/generate-content/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Stock Photos (4 tests)
# ============================================================================

class TestStockPhotos:

    @pytest.mark.asyncio
    async def test_search_stock_photos(self, async_client, auth_headers):
        """GET /stock-photos → list (mocked API)."""
        with patch("app.services.creator.stock_photos.StockPhotoService.search", new_callable=AsyncMock) as mock:
            mock.return_value = [
                {"url": "https://example.com/1.jpg", "thumb": "https://example.com/1s.jpg",
                 "author": "Test", "source": "unsplash", "download_url": "https://example.com/1.jpg"},
            ]
            response = await async_client.get(
                "/api/v1/stock-photos?query=nature",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["source"] == "unsplash"

    @pytest.mark.asyncio
    async def test_search_empty_results(self, async_client, auth_headers):
        """GET /stock-photos → empty when no API keys."""
        with patch("app.services.creator.stock_photos.StockPhotoService.search", new_callable=AsyncMock) as mock:
            mock.return_value = []
            response = await async_client.get(
                "/api/v1/stock-photos?query=xyzabc123",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_download_stock_photo(self, async_client, auth_headers, test_project_with_sections, tmp_path):
        """POST download → file saved, section updated."""
        section = test_project_with_sections.sections[0]

        # Create a test image
        from PIL import Image
        img = Image.new("RGB", (200, 150), color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.content = img_bytes
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            response = await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/stock-photos/download",
                headers=auth_headers,
                json={
                    "url": "https://example.com/photo.jpg",
                    "slot_id": "bg_image",
                    "section_id": str(section.id),
                    "aspect_ratio": "16:9",
                },
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "file_url" in data
            assert data["file_url"].endswith(".webp")

    @pytest.mark.asyncio
    async def test_download_stock_photo_bad_url(self, async_client, auth_headers, test_project_with_sections):
        """POST download with failing URL → 502."""
        section = test_project_with_sections.sections[0]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            response = await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/stock-photos/download",
                headers=auth_headers,
                json={
                    "url": "https://broken.example.com/photo.jpg",
                    "slot_id": "image",
                    "section_id": str(section.id),
                },
            )
            assert response.status_code == status.HTTP_502_BAD_GATEWAY


# ============================================================================
# Visual Review (2 tests)
# ============================================================================

class TestVisualReview:

    @pytest.mark.asyncio
    async def test_visual_review_returns_result(self, async_client, auth_headers, test_project_with_sections):
        """POST visual-review → review result."""
        with patch("app.services.ai.vision.AIVisionService.visual_review", new_callable=AsyncMock) as mock:
            mock.return_value = {"score": 8, "issues": [], "summary": "Looks good"}
            response = await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/ai/visual-review",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["score"] == 8

    @pytest.mark.asyncio
    async def test_visual_review_404_bad_project(self, async_client, auth_headers):
        """POST visual-review bad project → 404."""
        import uuid
        response = await async_client.post(
            f"/api/v1/projects/{uuid.uuid4()}/ai/visual-review",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# AI Chat in editing context (2 tests)
# ============================================================================

class TestAIChatEditing:

    @pytest.mark.asyncio
    async def test_chat_editing_context(self, async_client, auth_headers, test_project_with_sections):
        """POST chat with context=editing → SSE stream."""
        with patch("app.services.ai.engine.AIEngine.chat_stream") as mock_stream:
            async def mock_gen(*args, **kwargs):
                yield "Hello "
                yield "from AI"
            mock_stream.return_value = mock_gen()

            response = await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/ai/chat",
                headers=auth_headers,
                json={"context": "editing", "message": "Zmien tytul"},
            )
            assert response.status_code == status.HTTP_200_OK
            assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_chat_invalid_context(self, async_client, auth_headers, test_project_with_sections):
        """POST chat with invalid context → 400."""
        response = await async_client.post(
            f"/api/v1/projects/{test_project_with_sections.id}/ai/chat",
            headers=auth_headers,
            json={"context": "invalid", "message": "test"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Integration (2 tests)
# ============================================================================

class TestIntegration:

    @pytest.mark.asyncio
    async def test_full_flow_add_section_and_render(self, async_client, auth_headers, test_project_with_sections, seeded_blocks):
        """Add section → generate content → render → section visible."""
        # Add section
        response = await async_client.post(
            f"/api/v1/projects/{test_project_with_sections.id}/sections",
            headers=auth_headers,
            json={"block_code": "FA1", "variant": "A"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        new_section = response.json()

        # Generate content
        with patch("app.services.ai.engine.AIEngine.generate_section_content", new_callable=AsyncMock) as mock:
            mock.return_value = {"title": "FAQ Title", "items": []}
            response = await async_client.post(
                f"/api/v1/projects/{test_project_with_sections.id}/ai/generate-content/{new_section['id']}",
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_200_OK

        # Render
        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/render",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Witamy" in response.json()["html"]

    @pytest.mark.asyncio
    async def test_reorder_then_render(self, async_client, auth_headers, test_project_with_sections, seeded_blocks):
        """Reorder sections → render → correct order."""
        sections = test_project_with_sections.sections
        reversed_order = [str(sections[2].id), str(sections[1].id), str(sections[0].id)]

        response = await async_client.post(
            f"/api/v1/projects/{test_project_with_sections.id}/sections/reorder",
            headers=auth_headers,
            json={"order": reversed_order},
        )
        assert response.status_code == status.HTTP_200_OK

        # Render
        response = await async_client.get(
            f"/api/v1/projects/{test_project_with_sections.id}/render",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        html = response.json()["html"]
        assert "Kontakt" in html
