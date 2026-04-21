"""
Testy E2E — pelny flow 5 krokow Lab Creatora.
Create → Brief → Structure → Visual Concept → Content → Preview → Export.
"""

import pytest


class TestFullE2EFlow:
    """Happy path: caly przebieg od stworzenia projektu do exportu HTML."""

    @pytest.mark.asyncio
    async def test_complete_5_step_flow(self, client, mock_claude_json):
        # ── KROK 0: Stwórz projekt ──
        resp = await client.post("/api/v1/projects", json={
            "name": "E2E TestFirma",
            "site_type": "company_card",
        })
        assert resp.status_code == 200
        pid = resp.json()["id"]

        # ── KROK 1: Brief + Style ──
        resp = await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {
                "description": "Firma IT tworzaca oprogramowanie na zamowienie",
                "target_audience": "Male i srednie przedsiebiorstwa",
                "usp": "Wdrozenia w 4 tygodnie",
                "tone": "profesjonalny",
            },
            "style_json": {
                "primary_color": "#4F46E5",
                "secondary_color": "#F59E0B",
            },
        })
        assert resp.status_code == 200

        # Verify brief saved
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        assert project["brief_json"]["description"] == "Firma IT tworzaca oprogramowanie na zamowienie"
        assert project["style_json"]["primary_color"] == "#4F46E5"
        assert project["current_step"] == 1

        # ── KROK 2: Generuj strukture ──
        resp = await client.post(f"/api/v1/projects/{pid}/generate-structure")
        assert resp.status_code == 200
        structure = resp.json()
        assert len(structure["sections"]) >= 3

        # Verify sections in DB
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        assert len(project["sections"]) >= 3
        assert project["current_step"] >= 2

        section_ids = [s["id"] for s in project["sections"]]
        section_codes = [s["block_code"] for s in project["sections"]]

        # Verify no duplicates
        assert len(section_codes) == len(set(section_codes)), "Znaleziono zduplikowane sekcje!"

        # ── KROK 3: Visual Concept ──
        resp = await client.post(f"/api/v1/projects/{pid}/generate-visual-concept")
        assert resp.status_code == 200
        vc = resp.json()
        assert "style" in vc
        assert "bg_approach" in vc
        assert "separator_type" in vc
        assert "sections" in vc

        # Verify VC saved
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        assert project["visual_concept_json"] is not None
        assert project["current_step"] >= 3

        # ── KROK 4: Generuj tresci ──
        resp = await client.post(f"/api/v1/projects/{pid}/generate-content")
        assert resp.status_code == 200
        content = resp.json()
        assert len(content["sections"]) >= 1

        # Verify content saved to sections
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        filled = [s for s in project["sections"] if s["slots_json"]]
        assert len(filled) >= 1
        assert project["current_step"] >= 4

        # ── KROK 5: Preview + Export ──
        resp = await client.get(f"/api/v1/projects/{pid}/preview")
        assert resp.status_code == 200
        html = resp.text
        assert "<!DOCTYPE html>" in html
        assert "E2E TestFirma" in html
        assert "data-section-id" in html
        assert "<style>" in html  # inline CSS

        # Export HTML
        resp = await client.get(f"/api/v1/projects/{pid}/export-html")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "content-disposition" in resp.headers
        assert "E2E_TestFirma" in resp.headers["content-disposition"]


class TestE2EEdgeCases:

    @pytest.mark.asyncio
    async def test_modify_structure_then_regenerate(self, client, mock_claude_json):
        """Uzytkownik dodaje/usuwa sekcje reczne po wygenerowaniu."""
        resp = await client.post("/api/v1/projects", json={"name": "EditFlow"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "Test"},
        })

        # Gen structure
        await client.post(f"/api/v1/projects/{pid}/generate-structure")
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        assert len(project["sections"]) >= 3

        # Add a section manually
        await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "FO1", "position": 99})
        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        original_count = len(project["sections"])

        # Remove first section
        first_sid = project["sections"][0]["id"]
        await client.delete(f"/api/v1/projects/{pid}/sections/{first_sid}")

        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        assert len(project["sections"]) == original_count - 1

    @pytest.mark.asyncio
    async def test_regenerate_single_section(self, client, mock_claude_json):
        """Regeneruj tresc jednej sekcji z instrukcja."""
        resp = await client.post("/api/v1/projects", json={"name": "RegenFlow"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={
            "brief_json": {"description": "IT firma", "tone": "profesjonalny"},
        })

        await client.post(f"/api/v1/projects/{pid}/generate-structure")
        await client.post(f"/api/v1/projects/{pid}/generate-content")

        project = (await client.get(f"/api/v1/projects/{pid}")).json()
        filled = [s for s in project["sections"] if s["slots_json"]]
        assert len(filled) >= 1

        # Regenerate one section
        sid = filled[0]["id"]
        resp = await client.post(f"/api/v1/projects/{pid}/sections/{sid}/regenerate", json={
            "instruction": "Uzyj bardziej emocjonalnego jezyka",
        })
        assert resp.status_code == 200
        assert resp.json()["slots_json"] is not None

    @pytest.mark.asyncio
    async def test_multiple_projects_isolated(self, client, mock_claude_json):
        """Dwa projekty nie wplywaja na siebie."""
        r1 = await client.post("/api/v1/projects", json={"name": "Proj1", "site_type": "company"})
        r2 = await client.post("/api/v1/projects", json={"name": "Proj2", "site_type": "expert"})
        pid1 = r1.json()["id"]
        pid2 = r2.json()["id"]

        await client.patch(f"/api/v1/projects/{pid1}", json={"brief_json": {"description": "P1"}})
        await client.patch(f"/api/v1/projects/{pid2}", json={"brief_json": {"description": "P2"}})

        await client.post(f"/api/v1/projects/{pid1}/generate-structure")
        await client.post(f"/api/v1/projects/{pid2}/generate-structure")

        p1 = (await client.get(f"/api/v1/projects/{pid1}")).json()
        p2 = (await client.get(f"/api/v1/projects/{pid2}")).json()

        assert p1["name"] == "Proj1"
        assert p2["name"] == "Proj2"
        assert p1["site_type"] == "company"
        assert p2["site_type"] == "expert"

    @pytest.mark.asyncio
    async def test_visual_concept_manual_edit(self, client, mock_claude_json):
        """Reczna zmiana visual concept po wygenerowaniu."""
        resp = await client.post("/api/v1/projects", json={"name": "VCEdit"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={"brief_json": {"description": "Test"}})
        await client.post(f"/api/v1/projects/{pid}/generate-structure")
        await client.post(f"/api/v1/projects/{pid}/generate-visual-concept")

        # Get VC
        vc = (await client.get(f"/api/v1/projects/{pid}/visual-concept")).json()
        assert "style" in vc

        # Modify and save
        vc["style"] = "bold"
        vc["separator_type"] = "triangle"
        resp = await client.put(f"/api/v1/projects/{pid}/visual-concept", json=vc)
        assert resp.status_code == 200

        # Verify
        vc2 = (await client.get(f"/api/v1/projects/{pid}/visual-concept")).json()
        assert vc2["style"] == "bold"
        assert vc2["separator_type"] == "triangle"

    @pytest.mark.asyncio
    async def test_delete_project_cascade(self, client, mock_claude_json):
        """Usuniety projekt usuwa tez sekcje."""
        resp = await client.post("/api/v1/projects", json={"name": "Cascade"})
        pid = resp.json()["id"]
        await client.patch(f"/api/v1/projects/{pid}", json={"brief_json": {"description": "Test"}})
        await client.post(f"/api/v1/projects/{pid}/generate-structure")

        # Delete
        resp = await client.delete(f"/api/v1/projects/{pid}")
        assert resp.status_code == 200

        # Verify 404
        resp = await client.get(f"/api/v1/projects/{pid}")
        assert resp.status_code == 404
