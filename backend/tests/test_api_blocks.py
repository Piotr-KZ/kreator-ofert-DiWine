"""
Testy API — Blocks, Site Types, Export, Health.
"""

import pytest


class TestBlocksAPI:

    @pytest.mark.asyncio
    async def test_list_categories(self, client):
        resp = await client.get("/api/v1/blocks/categories")
        assert resp.status_code == 200
        cats = resp.json()
        assert len(cats) >= 7
        codes = [c["code"] for c in cats]
        assert "NA" in codes
        assert "HE" in codes
        assert "KO" in codes

    @pytest.mark.asyncio
    async def test_categories_have_fields(self, client):
        resp = await client.get("/api/v1/blocks/categories")
        cat = resp.json()[0]
        assert "code" in cat
        assert "name" in cat
        assert "icon" in cat
        assert "order" in cat

    @pytest.mark.asyncio
    async def test_list_blocks(self, client):
        resp = await client.get("/api/v1/blocks")
        assert resp.status_code == 200
        blocks = resp.json()
        assert len(blocks) >= 6
        codes = [b["code"] for b in blocks]
        assert "NA1" in codes
        assert "HE1" in codes

    @pytest.mark.asyncio
    async def test_list_blocks_by_category(self, client):
        resp = await client.get("/api/v1/blocks", params={"category": "HE"})
        assert resp.status_code == 200
        blocks = resp.json()
        assert all(b["category_code"] == "HE" for b in blocks)

    @pytest.mark.asyncio
    async def test_block_fields(self, client):
        resp = await client.get("/api/v1/blocks")
        block = resp.json()[0]
        assert "code" in block
        assert "name" in block
        assert "slots_definition" in block


class TestSiteTypesAPI:

    @pytest.mark.asyncio
    async def test_list_site_types(self, client):
        resp = await client.get("/api/v1/site-types")
        assert resp.status_code == 200
        types = resp.json()
        assert len(types) >= 5
        values = [t["value"] for t in types]
        assert "company_card" in values
        assert "company" in values
        assert "lp_product" in values
        assert "lp_service" in values
        assert "expert" in values


class TestHealthEndpoint:

    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "Lab Creator"


class TestExportAPI:

    @pytest.mark.asyncio
    async def test_preview_empty_project(self, client):
        resp = await client.post("/api/v1/projects", json={"name": "PreviewTest"})
        pid = resp.json()["id"]

        resp = await client.get(f"/api/v1/projects/{pid}/preview")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "PreviewTest" in resp.text

    @pytest.mark.asyncio
    async def test_export_html(self, client):
        resp = await client.post("/api/v1/projects", json={"name": "ExportTest"})
        pid = resp.json()["id"]

        resp = await client.get(f"/api/v1/projects/{pid}/export-html")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "content-disposition" in resp.headers
        assert "ExportTest" in resp.headers["content-disposition"]

    @pytest.mark.asyncio
    async def test_preview_with_sections(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "FullPreview"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "IT firma"},
            "style_json": {"primary_color": "#4F46E5"},
        })

        await client.post(f"/api/v1/projects/{pid}/generate-structure")
        await client.post(f"/api/v1/projects/{pid}/generate-content")

        resp = await client.get(f"/api/v1/projects/{pid}/preview")
        assert resp.status_code == 200
        html = resp.text
        assert "<!DOCTYPE html>" in html
        assert "data-section-id" in html

    @pytest.mark.asyncio
    async def test_export_404(self, client):
        resp = await client.get("/api/v1/projects/fake/preview")
        assert resp.status_code == 404
