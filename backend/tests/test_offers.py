"""
Tests for offer module — models, seed, API endpoints, calculator.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import init_db, async_session_local, engine
from app.db.base import Base
from app.services.offer.seed_offer_data import seed_offer_data
from app.services.offer.calculator import (
    get_wine_discount_percent,
    get_personalization_price,
    calc_wine_price,
    calc_set_price,
    validate_set_capacity,
    generate_offer_number,
)


# ─── FIXTURES ───

@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables and seed before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_local() as db:
        await seed_offer_data(db)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Async HTTP client for testing API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── CALCULATOR TESTS ───

class TestCalculator:
    def test_wine_discount_0_for_small_quantity(self):
        rules = [{"rule_type": "wine", "min_quantity": 1, "max_quantity": 99, "discount_percent": 0}]
        assert get_wine_discount_percent(50, rules) == 0

    def test_wine_discount_5_for_100(self):
        rules = [
            {"rule_type": "wine", "min_quantity": 1, "max_quantity": 99, "discount_percent": 0},
            {"rule_type": "wine", "min_quantity": 100, "max_quantity": 199, "discount_percent": 5},
        ]
        assert get_wine_discount_percent(100, rules) == 5

    def test_wine_discount_20_for_300(self):
        rules = [
            {"rule_type": "wine", "min_quantity": 300, "max_quantity": 99999, "discount_percent": 20},
        ]
        assert get_wine_discount_percent(500, rules) == 20

    def test_calc_wine_price(self):
        assert calc_wine_price(80.50, 5) == 76.47  # 80.50 * 0.95 = 76.475 → round → 76.47

    def test_calc_wine_price_no_discount(self):
        assert calc_wine_price(62.00, 0) == 62.00

    def test_personalization_price_by_product(self):
        rules = [
            {"rule_type": "personalization", "product_id": "logo1", "min_quantity": 100, "max_quantity": 199, "fixed_price": 12.0},
            {"rule_type": "personalization", "product_id": "cork1", "min_quantity": 100, "max_quantity": 199, "fixed_price": 6.0},
        ]
        assert get_personalization_price("logo1", 150, rules) == 12.0
        assert get_personalization_price("cork1", 150, rules) == 6.0
        assert get_personalization_price("unknown", 150, rules) == 0

    def test_calc_set_price_basic(self):
        rules = [{"rule_type": "wine", "min_quantity": 100, "max_quantity": 199, "discount_percent": 5}]
        items = [
            {"item_type": "wine", "base_price": 80.0, "product_id": "w1"},
            {"item_type": "sweet", "base_price": 12.0, "product_id": "s1"},
        ]
        result = calc_set_price(items, 26.0, 100, rules)
        assert result["packaging"] == 26.0
        assert result["wines"] == 76.0  # 80 * 0.95
        assert result["sweets"] == 12.0
        assert result["unit_total"] == 114.0
        assert result["grand_total"] == 11400.0

    def test_validate_capacity_ok(self):
        assert validate_set_capacity(1, 5, 1, 4) == []

    def test_validate_capacity_wine_overflow(self):
        warnings = validate_set_capacity(1, 5, 2, 3)
        assert len(warnings) == 1
        assert "butelek" in warnings[0]

    def test_validate_capacity_sweet_overflow(self):
        warnings = validate_set_capacity(1, 5, 1, 7)
        assert len(warnings) == 1
        assert "slotów" in warnings[0]

    def test_generate_offer_number(self):
        assert generate_offer_number(2026, 5, 1) == "OF/2026/05/0001"
        assert generate_offer_number(2026, 12, 42) == "OF/2026/12/0042"


# ─── SEED TESTS ───

class TestSeed:
    async def test_seed_creates_products(self):
        async with async_session_local() as db:
            from sqlalchemy import select, func
            from app.models.offer import Product
            result = await db.execute(select(func.count(Product.id)))
            count = result.scalar()
            assert count == 22  # 10 wines + 6 sweets + 4 deco + 2 pers

    async def test_seed_creates_packagings(self):
        async with async_session_local() as db:
            from sqlalchemy import select, func
            from app.models.offer import Packaging
            result = await db.execute(select(func.count(Packaging.id)))
            assert result.scalar() == 9

    async def test_seed_creates_colors(self):
        async with async_session_local() as db:
            from sqlalchemy import select, func
            from app.models.offer import Color
            result = await db.execute(select(func.count(Color.id)))
            assert result.scalar() == 8

    async def test_seed_creates_discount_rules(self):
        async with async_session_local() as db:
            from sqlalchemy import select, func
            from app.models.offer import DiscountRule
            result = await db.execute(select(func.count(DiscountRule.id)))
            assert result.scalar() == 10  # 4 wine + 6 personalization

    async def test_seed_idempotent(self):
        """Running seed twice should not duplicate data."""
        async with async_session_local() as db:
            await seed_offer_data(db)  # second run
            from sqlalchemy import select, func
            from app.models.offer import Product
            result = await db.execute(select(func.count(Product.id)))
            assert result.scalar() == 22  # same count


# ─── API TESTS ───

class TestCatalogAPI:
    async def test_list_products(self, client):
        r = await client.get("/api/v1/offers/catalog/products")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 22

    async def test_list_products_filter_wine(self, client):
        r = await client.get("/api/v1/offers/catalog/products?category=wine")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 10
        assert all(p["category"] == "wine" for p in data)

    async def test_list_packagings(self, client):
        r = await client.get("/api/v1/offers/catalog/packagings")
        assert r.status_code == 200
        assert len(r.json()) == 9

    async def test_list_packagings_filter_bottles(self, client):
        r = await client.get("/api/v1/offers/catalog/packagings?bottles=2")
        assert r.status_code == 200
        data = r.json()
        assert all(p["bottles"] == 2 for p in data)

    async def test_list_colors(self, client):
        r = await client.get("/api/v1/offers/catalog/colors")
        assert r.status_code == 200
        assert len(r.json()) == 8

    async def test_list_occasions(self, client):
        r = await client.get("/api/v1/offers/catalog/occasions")
        assert r.status_code == 200
        assert len(r.json()) == 5

    async def test_list_discounts(self, client):
        r = await client.get("/api/v1/offers/catalog/discounts")
        assert r.status_code == 200
        assert len(r.json()) == 10


class TestClientsAPI:
    async def test_create_client(self, client):
        r = await client.post("/api/v1/offers/clients", json={
            "company_name": "TestCorp",
            "nip": "1234567890",
            "contact_person": "Jan Testowy",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["company_name"] == "TestCorp"
        assert "id" in data

    async def test_list_clients(self, client):
        await client.post("/api/v1/offers/clients", json={"company_name": "AAA"})
        await client.post("/api/v1/offers/clients", json={"company_name": "BBB"})
        r = await client.get("/api/v1/offers/clients")
        assert r.status_code == 200
        assert len(r.json()) >= 2


class TestOffersAPI:
    async def test_create_offer(self, client):
        # Create client first
        cr = await client.post("/api/v1/offers/clients", json={"company_name": "OfferTest"})
        client_id = cr.json()["id"]

        r = await client.post("/api/v1/offers", json={
            "client_id": client_id,
            "occasion_code": "christmas",
            "quantity": 100,
        })
        assert r.status_code == 200
        data = r.json()
        assert "OF/" in data["offer_number"]
        assert "id" in data

    async def test_create_offer_bad_client(self, client):
        r = await client.post("/api/v1/offers", json={
            "client_id": "nonexistent",
            "quantity": 100,
        })
        assert r.status_code == 404

    async def test_get_offer(self, client):
        cr = await client.post("/api/v1/offers/clients", json={"company_name": "GetTest"})
        client_id = cr.json()["id"]
        or_ = await client.post("/api/v1/offers", json={"client_id": client_id, "quantity": 100})
        offer_id = or_.json()["id"]

        r = await client.get(f"/api/v1/offers/{offer_id}")
        assert r.status_code == 200
        assert r.json()["quantity"] == 100
        assert r.json()["sets"] == []

    async def test_calculate_empty(self, client):
        r = await client.post("/api/v1/offers/calculate", json={
            "quantity": 100,
            "items": [],
        })
        assert r.status_code == 200
        assert r.json()["unit_total"] == 0
