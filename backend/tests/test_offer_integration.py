"""
Integration tests — full offer lifecycle through API.
Tests the flow across: seed → catalog → client → offer → set → items → calculate → preview.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import async_session_local, engine
from app.db.base import Base
from app.services.offer.seed_offer_data import seed_offer_data


# ─── FIXTURES ───

@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables, seed, then drop after test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_local() as db:
        await seed_offer_data(db)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── HELPERS ───

async def _create_client(client: AsyncClient) -> str:
    r = await client.post("/api/v1/offers/clients", json={
        "company_name": "IntegTest Sp. z o.o.",
        "nip": "9876543210",
        "contact_person": "Marek Testowy",
        "email": "marek@integtest.pl",
    })
    assert r.status_code == 200
    return r.json()["id"]


async def _get_product_by_name(client: AsyncClient, name_fragment: str, category: str) -> dict:
    r = await client.get(f"/api/v1/offers/catalog/products?category={category}")
    assert r.status_code == 200
    for p in r.json():
        if name_fragment.lower() in p["name"].lower():
            return p
    raise AssertionError(f"Product matching '{name_fragment}' not found in {category}")


async def _get_packaging(client: AsyncClient, bottles: int) -> dict:
    r = await client.get(f"/api/v1/offers/catalog/packagings?bottles={bottles}")
    assert r.status_code == 200
    pkgs = r.json()
    assert len(pkgs) > 0, f"No packaging for {bottles} bottles"
    return pkgs[0]


# ─── FULL LIFECYCLE TEST ───

class TestFullOfferLifecycle:
    """
    Complete flow: create client → create offer → add set with packaging →
    add wine → add sweet → verify prices → preview HTML.
    """

    async def test_complete_flow(self, client):
        # 1. Create client
        client_id = await _create_client(client)

        # 2. Load catalog — verify seeded data available
        r = await client.get("/api/v1/offers/catalog/products")
        assert r.status_code == 200
        assert len(r.json()) == 22

        r = await client.get("/api/v1/offers/catalog/discounts")
        assert r.status_code == 200
        assert len(r.json()) == 10

        # 3. Create offer (100 szt, christmas → 5% wine discount)
        r = await client.post("/api/v1/offers", json={
            "client_id": client_id,
            "occasion_code": "christmas",
            "quantity": 100,
        })
        assert r.status_code == 200
        offer_id = r.json()["id"]
        offer_number = r.json()["offer_number"]
        assert "OF/" in offer_number

        # 4. Get packaging (1 bottle)
        pkg = await _get_packaging(client, 1)

        # 5. Add set with packaging
        r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
            "name": "Wariant Świąteczny",
            "packaging_id": pkg["id"],
            "budget_per_unit": 150,
        })
        assert r.status_code == 200
        set_id = r.json()["id"]

        # 6. Add wine to set
        wine = await _get_product_by_name(client, "Jagoda Kamczacka", "wine")
        r = await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
            "product_id": wine["id"],
            "item_type": "wine",
            "color_code": wine.get("wine_color"),
        })
        assert r.status_code == 200
        wine_unit_price = r.json()["unit_price"]
        # 100 szt → 5% discount: 80.50 * 0.95 = 76.47
        assert wine_unit_price == pytest.approx(76.47, abs=0.02)

        # 7. Add sweet to set
        sweet = await _get_product_by_name(client, "Pierniczek", "sweet")
        r = await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
            "product_id": sweet["id"],
            "item_type": "sweet",
            "color_code": "red",
        })
        assert r.status_code == 200

        # 8. Verify offer state
        r = await client.get(f"/api/v1/offers/{offer_id}")
        assert r.status_code == 200
        offer_data = r.json()
        assert offer_data["quantity"] == 100
        assert offer_data["occasion_code"] == "christmas"
        assert len(offer_data["sets"]) == 1

        the_set = offer_data["sets"][0]
        assert the_set["name"] == "Wariant Świąteczny"
        assert len(the_set["items"]) == 2

        # unit_price = packaging + wine(discounted) + sweet
        # e.g. 26 + 76.47 + 8.50 = ~110.97
        assert the_set["unit_price"] > 100
        assert the_set["total_price"] == pytest.approx(the_set["unit_price"] * 100, abs=1)

        # 9. Standalone calculator — same items, should match
        r = await client.post("/api/v1/offers/calculate", json={
            "quantity": 100,
            "packaging_id": pkg["id"],
            "items": [
                {"product_id": wine["id"], "item_type": "wine"},
                {"product_id": sweet["id"], "item_type": "sweet"},
            ],
        })
        assert r.status_code == 200
        calc = r.json()
        assert calc["wine_discount_percent"] == 5
        assert calc["wines"] == pytest.approx(76.47, abs=0.02)
        assert calc["warnings"] == []

        # 10. HTML preview
        r = await client.get(f"/api/v1/offers/{offer_id}/preview")
        assert r.status_code == 200
        html = r.text
        assert "OFERTA" in html
        assert "IntegTest" in html
        assert "Wariant Świąteczny" in html
        assert "Jagoda Kamczacka" in html

    async def test_capacity_overflow_blocked(self, client):
        """Adding more wines than packaging allows should return 400."""
        client_id = await _create_client(client)
        pkg = await _get_packaging(client, 1)  # 1-bottle packaging

        r = await client.post("/api/v1/offers", json={
            "client_id": client_id, "quantity": 50,
        })
        offer_id = r.json()["id"]

        r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
            "name": "Test overflow", "packaging_id": pkg["id"],
        })
        set_id = r.json()["id"]

        # Add first wine — should succeed
        wine = await _get_product_by_name(client, "Jagoda", "wine")
        r = await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
            "product_id": wine["id"], "item_type": "wine", "color_code": "czerwone",
        })
        assert r.status_code == 200

        # Add second wine — 1-bottle packaging should block
        wine2 = await _get_product_by_name(client, "Merlot", "wine")
        r = await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
            "product_id": wine2["id"], "item_type": "wine", "color_code": "czerwone",
        })
        assert r.status_code == 400
        assert "slotów" in r.json()["detail"] or "Brak" in r.json()["detail"]

    async def test_remove_item_recalculates(self, client):
        """Removing an item should recalculate set prices."""
        client_id = await _create_client(client)
        pkg = await _get_packaging(client, 1)

        r = await client.post("/api/v1/offers", json={
            "client_id": client_id, "quantity": 100,
        })
        offer_id = r.json()["id"]

        r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
            "name": "Recalc test", "packaging_id": pkg["id"],
        })
        set_id = r.json()["id"]

        # Add wine
        wine = await _get_product_by_name(client, "Jagoda", "wine")
        r = await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
            "product_id": wine["id"], "item_type": "wine", "color_code": "czerwone",
        })
        assert r.status_code == 200

        # Check price with wine
        r = await client.get(f"/api/v1/offers/{offer_id}")
        price_with_wine = r.json()["sets"][0]["unit_price"]
        assert price_with_wine > pkg["price"]  # packaging + wine

        # Get item ID and remove it
        item_id = r.json()["sets"][0]["items"][0]["id"]
        r = await client.delete(f"/api/v1/offers/{offer_id}/sets/{set_id}/items/{item_id}")
        assert r.status_code == 200

        # Price should drop to just packaging
        r = await client.get(f"/api/v1/offers/{offer_id}")
        price_without_wine = r.json()["sets"][0]["unit_price"]
        assert price_without_wine == pkg["price"]
        assert price_without_wine < price_with_wine

    async def test_multiple_sets_in_offer(self, client):
        """Offer with multiple sets — each independently priced."""
        client_id = await _create_client(client)
        pkg1 = await _get_packaging(client, 1)
        pkg2 = await _get_packaging(client, 2)

        r = await client.post("/api/v1/offers", json={
            "client_id": client_id, "quantity": 200, "occasion_code": "universal",
        })
        offer_id = r.json()["id"]

        # Set A (1 bottle)
        r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
            "name": "Set A", "packaging_id": pkg1["id"],
        })
        assert r.status_code == 200
        set_a_id = r.json()["id"]

        # Set B (2 bottles)
        r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
            "name": "Set B", "packaging_id": pkg2["id"],
        })
        assert r.status_code == 200
        set_b_id = r.json()["id"]

        # Verify both sets exist
        r = await client.get(f"/api/v1/offers/{offer_id}")
        assert r.status_code == 200
        assert len(r.json()["sets"]) == 2
        names = {s["name"] for s in r.json()["sets"]}
        assert names == {"Set A", "Set B"}

        # Remove set A
        r = await client.delete(f"/api/v1/offers/{offer_id}/sets/{set_a_id}")
        assert r.status_code == 200

        r = await client.get(f"/api/v1/offers/{offer_id}")
        assert len(r.json()["sets"]) == 1
        assert r.json()["sets"][0]["name"] == "Set B"

    async def test_delete_offer_cascade(self, client):
        """Deleting offer should remove sets and items."""
        client_id = await _create_client(client)
        pkg = await _get_packaging(client, 1)

        r = await client.post("/api/v1/offers", json={
            "client_id": client_id, "quantity": 50,
        })
        offer_id = r.json()["id"]

        r = await client.post(f"/api/v1/offers/{offer_id}/sets", json={
            "name": "To delete", "packaging_id": pkg["id"],
        })
        set_id = r.json()["id"]

        wine = await _get_product_by_name(client, "Jabłkowe", "wine")
        await client.post(f"/api/v1/offers/{offer_id}/sets/{set_id}/items", json={
            "product_id": wine["id"], "item_type": "wine",
        })

        # Delete offer
        r = await client.delete(f"/api/v1/offers/{offer_id}")
        assert r.status_code == 200

        # Offer should be gone
        r = await client.get(f"/api/v1/offers/{offer_id}")
        assert r.status_code == 404

    async def test_discount_tiers(self, client):
        """Different quantities should yield different wine discounts."""
        client_id = await _create_client(client)
        wine = await _get_product_by_name(client, "Jagoda", "wine")

        for qty, expected_disc in [(50, 0), (100, 5), (200, 10), (300, 20)]:
            r = await client.post("/api/v1/offers/calculate", json={
                "quantity": qty,
                "items": [{"product_id": wine["id"], "item_type": "wine"}],
            })
            assert r.status_code == 200
            assert r.json()["wine_discount_percent"] == expected_disc, \
                f"qty={qty}: expected {expected_disc}%, got {r.json()['wine_discount_percent']}%"
