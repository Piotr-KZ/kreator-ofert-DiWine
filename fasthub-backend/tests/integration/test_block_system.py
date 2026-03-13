"""
Tests for Brief 33: Block System — Renderer, Image Processing, Seed, Matching, API.
25 tests total.
"""

import io
import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block_template import BlockCategory, BlockTemplate
from app.models.project import Project
from app.models.project_section import ProjectSection
from app.services.creator.renderer import BlockRenderer, PageRenderer


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def seeded_categories(db_session: AsyncSession):
    """Seed all block categories."""
    from app.services.creator.block_service import seed_block_categories
    await seed_block_categories(db_session)
    return db_session


@pytest_asyncio.fixture
async def seeded_blocks(seeded_categories: AsyncSession):
    """Seed all block templates (requires categories first)."""
    from app.services.creator.seed_blocks import seed_block_templates
    await seed_block_templates(seeded_categories)
    return seeded_categories


@pytest_asyncio.fixture
async def test_project_with_sections(
    db_session: AsyncSession, test_organization, test_user, seeded_blocks
):
    """Create a project with sections for rendering tests."""
    project = Project(
        organization_id=test_organization.id,
        created_by=test_user.id,
        name="Render Test",
        site_type="firmowa",
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

    s1 = ProjectSection(
        project_id=project.id,
        block_code="HE1",
        position=0,
        slots_json={
            "title": "Witamy",
            "subtitle": "Testowy podtytul",
            "cta_primary": "Kontakt",
        },
    )
    s2 = ProjectSection(
        project_id=project.id,
        block_code="CT1",
        position=1,
        slots_json={
            "title": "Gotowy?",
            "cta_text": "Zadzwon",
            "cta_url": "#tel",
        },
    )
    s3 = ProjectSection(
        project_id=project.id,
        block_code="HE5",
        position=2,
        is_visible=False,
        slots_json={"title": "Ukryty"},
    )
    db_session.add_all([s1, s2, s3])
    await db_session.commit()
    await db_session.refresh(project, ["sections"])
    return project


# ============================================================================
# BlockRenderer (6 tests)
# ============================================================================

class TestBlockRenderer:

    def test_render_simple_slots(self):
        """{{title}} → value."""
        renderer = BlockRenderer()
        html = renderer.render_block(
            "<h1>{{title}}</h1><p>{{subtitle}}</p>",
            {"title": "Hello", "subtitle": "World"},
        )
        assert "<h1>Hello</h1>" in html
        assert "<p>World</p>" in html

    def test_render_loop(self):
        """{{#each items}} → N elements."""
        renderer = BlockRenderer()
        html = renderer.render_block(
            "<ul>{{#each items}}<li>{{this.name}}</li>{{/each}}</ul>",
            {"items": [{"name": "A"}, {"name": "B"}, {"name": "C"}]},
        )
        assert html.count("<li>") == 3
        assert "A" in html
        assert "C" in html

    def test_render_condition_true(self):
        """{{#if x}}...{{/if}} → content when truthy."""
        renderer = BlockRenderer()
        html = renderer.render_block(
            "{{#if pre_title}}<span>{{pre_title}}</span>{{/if}}",
            {"pre_title": "Hey"},
        )
        assert "<span>Hey</span>" in html

    def test_render_condition_false(self):
        """{{#if x}}...{{/if}} → empty when falsy."""
        renderer = BlockRenderer()
        html = renderer.render_block(
            "{{#if pre_title}}<span>{{pre_title}}</span>{{/if}}",
            {},
        )
        assert "<span>" not in html

    def test_cleanup_unrealized_slots(self):
        """{{unknown}} → removed."""
        renderer = BlockRenderer()
        html = renderer.render_block(
            "<h1>{{title}}</h1><p>{{unknown_slot}}</p>",
            {"title": "OK"},
        )
        assert "{{unknown_slot}}" not in html
        assert "OK" in html

    def test_escape_html_in_text_slots(self):
        """<script> → &lt;script&gt;."""
        renderer = BlockRenderer()
        html = renderer.render_block(
            "<p>{{content}}</p>",
            {"content": '<script>alert("xss")</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ============================================================================
# PageRenderer (4 tests)
# ============================================================================

class TestPageRenderer:

    @pytest.mark.asyncio
    async def test_render_full_page(self, test_project_with_sections, db_session):
        """5 sections → continuous HTML."""
        renderer = PageRenderer()
        html_body, css = await renderer.render_project_html(
            db_session, test_project_with_sections
        )
        assert "Witamy" in html_body
        assert "Gotowy?" in html_body
        assert 'data-section-id=' in html_body
        assert 'data-block-code="HE1"' in html_body

    @pytest.mark.asyncio
    async def test_skip_invisible_sections(self, test_project_with_sections, db_session):
        """is_visible=false → skipped."""
        renderer = PageRenderer()
        html_body, _ = await renderer.render_project_html(
            db_session, test_project_with_sections
        )
        assert "Ukryty" not in html_body

    @pytest.mark.asyncio
    async def test_generate_css_from_style(self, test_project_with_sections, db_session):
        """palette + fonts → CSS variables."""
        renderer = PageRenderer()
        _, css = await renderer.render_project_html(
            db_session, test_project_with_sections
        )
        assert "--color-primary: #3B82F6" in css
        assert "--font-heading: 'Outfit'" in css
        assert "--font-body: 'Inter'" in css

    @pytest.mark.asyncio
    async def test_apply_vision_fixes(self, test_project_with_sections, db_session):
        """fixes → additional CSS."""
        renderer = PageRenderer()
        fixes = [
            {"element": ".hero", "css_addition": ".hero { padding: 2rem; }"},
        ]
        _, css = await renderer.render_project_html(
            db_session, test_project_with_sections, fixes=fixes
        )
        assert "Vision fix: .hero" in css
        assert ".hero { padding: 2rem; }" in css


# ============================================================================
# Block Matching (4 tests)
# ============================================================================

class TestBlockMatching:

    @pytest.mark.asyncio
    async def test_match_by_category(self, seeded_blocks):
        """category=HE → hero blocks only."""
        from app.services.creator.block_service import find_matching_blocks

        results = await find_matching_blocks(seeded_blocks, category_code="HE")
        assert len(results) >= 5
        assert all(b.category_code == "HE" for b in results)

    @pytest.mark.asyncio
    async def test_match_by_media_and_layout(self, seeded_blocks):
        """photo + photo-full-2 → matching blocks."""
        from app.services.creator.block_service import find_matching_blocks

        results = await find_matching_blocks(
            seeded_blocks, media_type="photo", layout_type="photo-full-2"
        )
        assert len(results) >= 1
        assert all(b.media_type == "photo" for b in results)

    @pytest.mark.asyncio
    async def test_match_returns_empty_for_no_match(self, seeded_blocks):
        """absurd criteria → empty list."""
        from app.services.creator.block_service import find_matching_blocks

        results = await find_matching_blocks(
            seeded_blocks, media_type="hologram", layout_type="3d-cube"
        )
        assert results == []

    @pytest.mark.asyncio
    async def test_match_all_blocks_when_no_criteria(self, seeded_blocks):
        """No filters → all active blocks."""
        from app.services.creator.block_service import find_matching_blocks

        results = await find_matching_blocks(seeded_blocks)
        assert len(results) == 40


# ============================================================================
# Image Processing (4 tests)
# ============================================================================

class TestImageProcessing:

    def _create_test_image(self, width=800, height=600, mode="RGB"):
        """Create a test PNG image bytes."""
        from PIL import Image
        img = Image.new(mode, (width, height), color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def test_crop_16_9(self):
        """landscape → 16:9 crop."""
        from app.services.creator.image_service import process_image

        raw = self._create_test_image(1000, 1000)
        result = process_image(raw, "16:9")
        from PIL import Image
        img = Image.open(io.BytesIO(result))
        ratio = img.width / img.height
        assert abs(ratio - 16 / 9) < 0.01

    def test_crop_1_1_square(self):
        """rectangle → square."""
        from app.services.creator.image_service import process_image

        raw = self._create_test_image(800, 600)
        result = process_image(raw, "1:1")
        from PIL import Image
        img = Image.open(io.BytesIO(result))
        assert img.width == img.height

    def test_auto_keeps_ratio(self):
        """auto → resize only, keep original ratio."""
        from app.services.creator.image_service import process_image

        raw = self._create_test_image(3000, 2000)
        result = process_image(raw, "auto", max_width=1920)
        from PIL import Image
        img = Image.open(io.BytesIO(result))
        assert img.width <= 1920
        ratio = img.width / img.height
        assert abs(ratio - 3 / 2) < 0.01

    def test_webp_output(self):
        """output format = WebP."""
        from app.services.creator.image_service import process_image

        raw = self._create_test_image(400, 300)
        result = process_image(raw, "4:3")
        from PIL import Image
        img = Image.open(io.BytesIO(result))
        assert img.format == "WEBP"


# ============================================================================
# Seed (3 tests)
# ============================================================================

class TestSeed:

    @pytest.mark.asyncio
    async def test_seed_40_blocks(self, seeded_blocks):
        """After seed → 40 records."""
        result = await seeded_blocks.execute(
            select(func.count()).select_from(BlockTemplate)
        )
        count = result.scalar()
        assert count == 40

    @pytest.mark.asyncio
    async def test_seed_idempotent(self, seeded_blocks):
        """Double seed → still 40."""
        from app.services.creator.seed_blocks import seed_block_templates

        created = await seed_block_templates(seeded_blocks)
        assert created == 0

        result = await seeded_blocks.execute(
            select(func.count()).select_from(BlockTemplate)
        )
        count = result.scalar()
        assert count == 40

    @pytest.mark.asyncio
    async def test_seed_updates_template(self, seeded_blocks):
        """Changed HTML → updated in DB."""
        from app.services.creator.seed_blocks import BLOCK_SEEDS, seed_block_templates

        # Modify a template
        original_html = BLOCK_SEEDS[0]["html_template"]
        BLOCK_SEEDS[0]["html_template"] = "<section>CHANGED</section>"

        try:
            await seed_block_templates(seeded_blocks)

            result = await seeded_blocks.execute(
                select(BlockTemplate).where(BlockTemplate.code == BLOCK_SEEDS[0]["code"])
            )
            block = result.scalar_one()
            assert block.html_template == "<section>CHANGED</section>"
        finally:
            # Restore
            BLOCK_SEEDS[0]["html_template"] = original_html


# ============================================================================
# API (4 tests)
# ============================================================================

class TestBlockAPI:

    @pytest.mark.asyncio
    async def test_get_blocks_list(self, async_client, auth_headers, seeded_blocks):
        """GET /blocks → list all."""
        response = await async_client.get("/api/v1/blocks", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 40

    @pytest.mark.asyncio
    async def test_get_blocks_filtered(self, async_client, auth_headers, seeded_blocks):
        """GET /blocks?category=HE → filtered."""
        response = await async_client.get(
            "/api/v1/blocks?category=HE", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5
        assert all(b["category_code"] == "HE" for b in data)

    @pytest.mark.asyncio
    async def test_post_blocks_match(self, async_client, auth_headers, seeded_blocks):
        """POST /blocks/match → matching blocks."""
        response = await async_client.post(
            "/api/v1/blocks/match",
            headers=auth_headers,
            json={"media_type": "opinion"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
        assert all(b["media_type"] == "opinion" for b in data)

    @pytest.mark.asyncio
    async def test_get_block_detail(self, async_client, auth_headers, seeded_blocks):
        """GET /blocks/HE1 → template + slots."""
        response = await async_client.get(
            "/api/v1/blocks/HE1", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "HE1"
        assert "{{title}}" in data["html_template"]
        assert len(data["slots_definition"]) >= 3
