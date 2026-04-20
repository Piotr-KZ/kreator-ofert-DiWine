"""
Tests for Brief 42: Site Type Config API endpoints.
5 integration tests.
"""

import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession


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


class TestSiteTypeConfigAPI:
    """Tests for /creator/site-type-config endpoints."""

    @pytest.mark.asyncio
    async def test_list_site_types(self, async_client):
        """GET /creator/site-type-config returns all types."""
        response = await async_client.get("/api/v1/creator/site-type-config")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 16

        # Each item has expected fields
        for item in data:
            assert "site_type" in item
            assert "label" in item
            assert "category" in item
            assert item["category"] in ("firma", "osoba")

    @pytest.mark.asyncio
    async def test_get_firmowa_config(self, async_client):
        """GET /creator/site-type-config/firmowa returns full config."""
        response = await async_client.get("/api/v1/creator/site-type-config/firmowa")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["site_type"] == "firmowa"
        assert data["label"] == "Strona firmowa"
        assert data["category"] == "firma"
        assert isinstance(data["recommended_blocks"], list)
        assert data["recommended_blocks"][0] == "NA"
        assert data["recommended_blocks"][-1] == "FO"
        assert data["min_sections"] == 6
        assert data["max_sections"] == 14
        assert isinstance(data["style_presets"], list)
        assert isinstance(data["brief_sections"], list)
        assert "s1" in data["brief_sections"]

    @pytest.mark.asyncio
    async def test_get_wizytowka_config(self, async_client):
        """GET /creator/site-type-config/wizytowka returns minimal config."""
        response = await async_client.get("/api/v1/creator/site-type-config/wizytowka")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["min_sections"] == 3
        assert data["max_sections"] == 6
        assert len(data["recommended_blocks"]) == 4
        assert len(data["readiness_skip_checks"]) >= 5

    @pytest.mark.asyncio
    async def test_get_unknown_returns_404(self, async_client):
        """Unknown site type returns 404."""
        response = await async_client.get("/api/v1/creator/site-type-config/nieznany-typ-123")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_blocks_endpoint_with_site_type_filter(self, async_client, seeded_blocks):
        """GET /blocks?site_type=wizytowka filters by allowed categories."""
        # Without filter — all blocks
        resp_all = await async_client.get("/api/v1/blocks")
        assert resp_all.status_code == status.HTTP_200_OK
        all_blocks = resp_all.json()

        # With wizytowka filter — only allowed categories
        resp_filtered = await async_client.get("/api/v1/blocks?site_type=wizytowka")
        assert resp_filtered.status_code == status.HTTP_200_OK
        filtered = resp_filtered.json()

        # Should have fewer blocks
        assert len(filtered) <= len(all_blocks)

        # All filtered blocks should be in allowed categories
        allowed = {"NA", "HE", "FI", "KO", "FO", "CT", "GA"}
        for block in filtered:
            assert block["category_code"] in allowed, f"Block {block['code']} has category {block['category_code']}, not in allowed"
