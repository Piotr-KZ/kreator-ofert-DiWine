"""
Testy API — AI endpoints z mockiem Anthropic.
"""

import pytest
from unittest.mock import patch


class TestGenerateStructure:

    @pytest.mark.asyncio
    async def test_generate_structure(self, client, mock_claude_json):
        # Create project + save brief
        resp = await client.post("/api/v1/projects", json={"name": "AITest", "site_type": "company_card"})
        pid = resp.json()["id"]

        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "Firma IT", "target_audience": "MŚP", "usp": "Szybkie wdrozenia", "tone": "profesjonalny"},
            "style_json": {"primary_color": "#4F46E5", "secondary_color": "#F59E0B"},
        })

        # Generate structure
        resp = await client.post(f"/api/v1/projects/{pid}/generate-structure")
        assert resp.status_code == 200
        data = resp.json()
        assert "sections" in data
        assert len(data["sections"]) >= 3

        # Verify sections saved to project
        get_resp = await client.get(f"/api/v1/projects/{pid}")
        project = get_resp.json()
        assert len(project["sections"]) == len(data["sections"])
        assert project["current_step"] >= 2

    @pytest.mark.asyncio
    async def test_generate_structure_updates_step(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "StepTest"})
        pid = resp.json()["id"]

        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "Test"},
        })
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        get_resp = await client.get(f"/api/v1/projects/{pid}")
        assert get_resp.json()["current_step"] >= 2

    @pytest.mark.asyncio
    async def test_generate_structure_clears_old_sections(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "ClearTest"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={"brief_json": {"description": "Test"}})

        # Add manual section
        await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "GA1"})

        # Generate — should replace all
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        get_resp = await client.get(f"/api/v1/projects/{pid}")
        codes = [s["block_code"] for s in get_resp.json()["sections"]]
        assert "GA1" not in codes  # Old section replaced


class TestGenerateVisualConcept:

    @pytest.mark.asyncio
    async def test_generate_visual_concept(self, client, mock_claude_json):
        # Create + brief + structure
        resp = await client.post("/api/v1/projects", json={"name": "VCTest"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "Firma IT", "target_audience": "MSP", "usp": "Szybki", "tone": "profesjonalny"},
            "style_json": {"primary_color": "#4F46E5", "secondary_color": "#F59E0B"},
        })
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        # Generate visual concept
        resp = await client.post(f"/api/v1/projects/{pid}/generate-visual-concept")
        assert resp.status_code == 200
        data = resp.json()
        assert "style" in data
        assert "sections" in data

    @pytest.mark.asyncio
    async def test_visual_concept_requires_sections(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "NoSections"})
        pid = resp.json()["id"]

        resp = await client.post(f"/api/v1/projects/{pid}/generate-visual-concept")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_save_visual_concept(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "SaveVC"})
        pid = resp.json()["id"]

        vc = {"style": "bold", "bg_approach": "dark_theme", "separator_type": "diagonal", "sections": []}
        resp = await client.put(f"/api/v1/projects/{pid}/visual-concept", json=vc)
        assert resp.status_code == 200

        # Verify saved
        get_resp = await client.get(f"/api/v1/projects/{pid}/visual-concept")
        assert get_resp.json()["style"] == "bold"

    @pytest.mark.asyncio
    async def test_get_visual_concept_empty(self, client):
        resp = await client.post("/api/v1/projects", json={"name": "EmptyVC"})
        pid = resp.json()["id"]

        resp = await client.get(f"/api/v1/projects/{pid}/visual-concept")
        assert resp.status_code == 200
        assert resp.json() == {}


class TestGenerateContent:

    @pytest.mark.asyncio
    async def test_generate_content(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "ContentTest"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "IT", "target_audience": "B2B", "usp": "Fast", "tone": "profesjonalny"},
        })
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        resp = await client.post(f"/api/v1/projects/{pid}/generate-content")
        assert resp.status_code == 200
        data = resp.json()
        assert "sections" in data
        assert len(data["sections"]) >= 1

    @pytest.mark.asyncio
    async def test_generate_content_no_sections(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "NoSec"})
        pid = resp.json()["id"]

        resp = await client.post(f"/api/v1/projects/{pid}/generate-content")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_regenerate_section(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "RegenTest"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "IT"},
        })
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        # Get a section ID
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        sid = project["sections"][0]["id"]

        resp = await client.post(f"/api/v1/projects/{pid}/sections/{sid}/regenerate", json={
            "instruction": "Skroc tekst"
        })
        assert resp.status_code == 200
        assert "slots_json" in resp.json()

    @pytest.mark.asyncio
    async def test_regenerate_section_404(self, client, mock_claude_json):
        resp = await client.post("/api/v1/projects", json={"name": "Regen404"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={"brief_json": {"description": "IT"}})
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        resp = await client.post(f"/api/v1/projects/{pid}/sections/fake-id/regenerate", json={})
        assert resp.status_code == 404
