"""
Integration tests — full user flow across Krok 5 + 6.
Tests: text templates API, page templates, build-page, public link, accept.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import async_session_local, engine
from app.db.base import Base
from app.services.offer.seed_offer_data import seed_offer_data
from app.services.offer.seed_offer_texts import seed_offer_texts
from app.services.offer.seed_offer_blocks import seed_offer_blocks


# ─── FIXTURES ───

@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables, seed all data, then drop after test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_local() as db:
        await seed_offer_data(db)
    async with async_session_local() as db:
        await seed_offer_texts(db)
    async with async_session_local() as db:
        await seed_offer_blocks(db)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── HELPERS ───

async def _setup_offer_with_set(client: AsyncClient) -> dict:
    """Create client + offer + set with wine → return ids."""
    # Client
    r = await client.post("/api/v1/offers/clients", json={
        "company_name": "FlowTest Sp. z o.o.",
        "nip": "1112223344",
        "contact_person": "Anna Flowowa",
        "email": "anna@flowtest.pl",
    })
    assert r.status_code == 200
    client_id = r.json()["id"]

    # Offer
    r = await client.post("/api/v1/offers", json={
        "client_id": client_id,
        "occasion_code": "christmas",
        "quantity": 100,
    })
    assert r.status_code == 200
    offer_id = r.json()["id"]

    # Packaging
    r = await client.get("/api/v1/offers/catalog/packagings?bottles=1")
    assert r.status_code == 200
    pkg = r.json()[0]

    # Set
    r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
        "name": "Zestaw Testowy",
        "packaging_id": pkg["id"],
    })
    assert r.status_code == 200
    set_id = r.json()["id"]

    # Wine
    r = await client.get("/api/v1/offers/catalog/products?category=wine")
    assert r.status_code == 200
    wine = next(p for p in r.json() if "jagoda" in p["name"].lower())
    r = await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
        "product_id": wine["id"],
        "item_type": "wine",
        "color_code": wine.get("wine_color"),
    })
    assert r.status_code == 200

    return {"offer_id": offer_id, "set_id": set_id, "client_id": client_id}


# ─── TEXT TEMPLATES TESTS ───

class TestTextTemplatesAPI:
    async def test_get_greeting_templates_christmas(self, client):
        r = await client.get("/api/v1/offers/ai/text-templates?block_type=greeting&occasion_code=christmas")
        assert r.status_code == 200
        templates = r.json()
        assert len(templates) >= 3  # A, B, C for christmas
        assert all(t["block_type"] == "greeting" for t in templates)

    async def test_get_why_us_templates(self, client):
        r = await client.get("/api/v1/offers/ai/text-templates?block_type=why_us")
        assert r.status_code == 200
        templates = r.json()
        assert len(templates) >= 3  # A, B, C

    async def test_get_closing_templates(self, client):
        r = await client.get("/api/v1/offers/ai/text-templates?block_type=closing")
        assert r.status_code == 200
        assert len(r.json()) >= 3

    async def test_personalize_simple_via_service(self, client):
        """Test personalization logic directly (endpoint needs API key)."""
        from app.services.offer.ai_service import OfferAIService
        service = OfferAIService.__new__(OfferAIService)
        result = await service.personalize_text(
            template_text="Oferta dla {company_name}, {quantity} zestawów.",
            company_name="FlowTest",
            quantity=100,
        )
        assert "FlowTest" in result
        assert "100" in result

    async def test_gus_invalid_nip(self, client):
        r = await client.post("/api/v1/offers/ai/gus-lookup", json={"nip": "123"})
        assert r.status_code == 200
        assert r.json()["found"] is False


# ─── PAGE TEMPLATES TESTS ───

class TestPageTemplatesAPI:
    async def test_list_page_templates(self, client):
        r = await client.get("/api/v1/offers/page-templates")
        assert r.status_code == 200
        templates = r.json()
        assert len(templates) == 4
        ids = [t["id"] for t in templates]
        assert "standard" in ids
        assert "premium" in ids

    async def test_each_template_has_block_count(self, client):
        r = await client.get("/api/v1/offers/page-templates")
        for t in r.json():
            assert "block_count" in t
            assert t["block_count"] > 0


# ─── BUILD PAGE + PUBLIC FLOW ───

class TestBuildPageFlow:
    async def test_build_page_standard(self, client):
        """Full flow: create offer → build page → get URLs."""
        ids = await _setup_offer_with_set(client)

        r = await client.post(f"/api/v1/offers/{ids['offer_id']}/build-page", json={
            "template_id": "standard",
        })
        assert r.status_code == 200
        data = r.json()
        assert "project_id" in data
        assert data["template_id"] == "standard"
        assert "/public/offers/" in data["public_url"]
        assert "/lab/" in data["editor_url"]

    async def test_build_page_preview(self, client):
        """After building page, internal preview should return HTML."""
        ids = await _setup_offer_with_set(client)
        await client.post(f"/api/v1/offers/{ids['offer_id']}/build-page", json={
            "template_id": "standard",
        })

        r = await client.get(f"/api/v1/offers/{ids['offer_id']}/page-preview")
        assert r.status_code == 200
        html = r.text
        assert "<!DOCTYPE html>" in html
        assert "OFERTA PREZENTOWA" in html  # NO1 header block content

    async def test_build_page_without_sets_fails(self, client):
        """Building page without sets should return 400."""
        r = await client.post("/api/v1/offers/clients", json={
            "company_name": "Empty Corp", "nip": "9998887766",
        })
        client_id = r.json()["id"]
        r = await client.post("/api/v1/offers", json={
            "client_id": client_id, "quantity": 50,
        })
        offer_id = r.json()["id"]

        r = await client.post(f"/api/v1/offers/{offer_id}/build-page", json={
            "template_id": "standard",
        })
        assert r.status_code == 400

    async def test_public_link_works(self, client):
        """Public token link should return offer page HTML."""
        ids = await _setup_offer_with_set(client)
        r = await client.post(f"/api/v1/offers/{ids['offer_id']}/build-page", json={
            "template_id": "standard",
        })
        public_url = r.json()["public_url"]

        r = await client.get(f"/api/v1{public_url}")
        assert r.status_code == 200
        assert "<!DOCTYPE html>" in r.text

    async def test_public_link_invalid_token(self, client):
        r = await client.get("/api/v1/public/offers/invalid-token-xyz")
        assert r.status_code == 404

    async def test_accept_offer(self, client):
        """Client accepts offer via public link."""
        ids = await _setup_offer_with_set(client)
        r = await client.post(f"/api/v1/offers/{ids['offer_id']}/build-page", json={
            "template_id": "standard",
        })
        token = r.json()["public_url"].split("/")[-1]

        r = await client.post(f"/api/v1/public/offers/{token}/accept")
        assert r.status_code == 200
        assert r.json()["status"] == "accepted"

        # Verify offer status changed
        r = await client.get(f"/api/v1/offers/{ids['offer_id']}")
        assert r.json()["status"] == "accepted"

    async def test_build_premium_template(self, client):
        """Premium template should also build successfully."""
        ids = await _setup_offer_with_set(client)
        r = await client.post(f"/api/v1/offers/{ids['offer_id']}/build-page", json={
            "template_id": "premium",
        })
        assert r.status_code == 200
        assert r.json()["template_id"] == "premium"

    async def test_build_quick_template(self, client):
        """Quick template — minimal blocks."""
        ids = await _setup_offer_with_set(client)
        r = await client.post(f"/api/v1/offers/{ids['offer_id']}/build-page", json={
            "template_id": "quick",
        })
        assert r.status_code == 200
        assert r.json()["template_id"] == "quick"
