"""
Testy API — Projects CRUD + Sections.
"""

import pytest


class TestProjectsCRUD:

    @pytest.mark.asyncio
    async def test_create_project(self, client):
        resp = await client.post("/api/v1/projects", json={"name": "Moja Firma", "site_type": "company"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Moja Firma"
        assert data["site_type"] == "company"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_project_default_type(self, client):
        resp = await client.post("/api/v1/projects", json={"name": "Wizytowka"})
        data = resp.json()
        assert data["site_type"] == "company_card"

    @pytest.mark.asyncio
    async def test_list_projects(self, client):
        await client.post("/api/v1/projects", json={"name": "P1"})
        await client.post("/api/v1/projects", json={"name": "P2"})

        resp = await client.get("/api/v1/projects")
        assert resp.status_code == 200
        projects = resp.json()
        assert len(projects) >= 2

    @pytest.mark.asyncio
    async def test_get_project(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "GetTest"})
        pid = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/projects/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "GetTest"
        assert data["sections"] == []

    @pytest.mark.asyncio
    async def test_get_project_404(self, client):
        resp = await client.get("/api/v1/projects/nonexistent-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "Before"})
        pid = create_resp.json()["id"]

        resp = await client.patch(f"/api/v1/projects/{pid}", json={
            "name": "After",
            "brief_json": {"description": "Opis firmy"},
            "style_json": {"primary_color": "#FF0000"},
        })
        assert resp.status_code == 200

        get_resp = await client.get(f"/api/v1/projects/{pid}")
        data = get_resp.json()
        assert data["name"] == "After"
        assert data["brief_json"]["description"] == "Opis firmy"
        assert data["style_json"]["primary_color"] == "#FF0000"

    @pytest.mark.asyncio
    async def test_delete_project(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "ToDelete"})
        pid = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/projects/{pid}")
        assert resp.status_code == 200

        get_resp = await client.get(f"/api/v1/projects/{pid}")
        assert get_resp.status_code == 404


class TestSectionsCRUD:

    @pytest.mark.asyncio
    async def test_add_section(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "P"})
        pid = create_resp.json()["id"]

        resp = await client.post(f"/api/v1/projects/{pid}/sections", json={
            "block_code": "HE1",
            "position": 0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["block_code"] == "HE1"
        assert data["position"] == 0

    @pytest.mark.asyncio
    async def test_update_section(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "P"})
        pid = create_resp.json()["id"]

        sec_resp = await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "HE1"})
        sid = sec_resp.json()["id"]

        resp = await client.patch(f"/api/v1/projects/{pid}/sections/{sid}", json={
            "variant": "B",
            "is_visible": False,
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_section(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "P"})
        pid = create_resp.json()["id"]

        sec_resp = await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "HE1"})
        sid = sec_resp.json()["id"]

        resp = await client.delete(f"/api/v1/projects/{pid}/sections/{sid}")
        assert resp.status_code == 200

        # Verify gone
        get_resp = await client.get(f"/api/v1/projects/{pid}")
        assert len(get_resp.json()["sections"]) == 0

    @pytest.mark.asyncio
    async def test_delete_section_404(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "P"})
        pid = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/projects/{pid}/sections/fake-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_reorder_sections(self, client):
        create_resp = await client.post("/api/v1/projects", json={"name": "P"})
        pid = create_resp.json()["id"]

        s1 = (await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "NA1", "position": 0})).json()["id"]
        s2 = (await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "HE1", "position": 1})).json()["id"]
        s3 = (await client.post(f"/api/v1/projects/{pid}/sections", json={"block_code": "KO1", "position": 2})).json()["id"]

        # Reverse order
        resp = await client.post(f"/api/v1/projects/{pid}/sections/reorder", json={
            "section_ids": [s3, s2, s1],
        })
        assert resp.status_code == 200

        # Verify new order
        get_resp = await client.get(f"/api/v1/projects/{pid}")
        sections = get_resp.json()["sections"]
        assert sections[0]["block_code"] == "KO1"
        assert sections[1]["block_code"] == "HE1"
        assert sections[2]["block_code"] == "NA1"
