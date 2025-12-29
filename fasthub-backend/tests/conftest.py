"""
Pytest configuration and shared fixtures
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base, get_db
from app.main import app
from app.models import APIToken, Invoice, Organization, Subscription, User

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://autoflow:autoflow123@localhost:5432/autoflow_test"


# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

    # Drop tables after test (manually to avoid circular dependency)
    async with test_engine.begin() as conn:
        # Drop tables in correct order
        await conn.execute(text("DROP TABLE IF EXISTS invoices CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS subscriptions CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS api_tokens CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS organizations CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS subscriptionstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS invoicestatus CASCADE"))


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency"""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create test client"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """Create test organization"""
    org = Organization(name="Test Organization", slug="test-org", stripe_customer_id="cus_test123")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
        role="user",
        organization_id=test_organization.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test admin user"""
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        role="admin",
        organization_id=test_organization.id,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user"""
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_headers(test_admin: User) -> dict:
    """Create authentication headers for admin user"""
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def test_subscription(
    db_session: AsyncSession, test_organization: Organization
) -> Subscription:
    """Create test subscription"""
    from datetime import datetime, timedelta

    subscription = Subscription(
        organization_id=test_organization.id,
        stripe_subscription_id="sub_test123",
        stripe_price_id="price_test123",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        cancel_at_period_end=False,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)
    return subscription


@pytest_asyncio.fixture
async def test_invoice(db_session: AsyncSession, test_organization: Organization) -> Invoice:
    """Create test invoice"""
    invoice = Invoice(
        organization_id=test_organization.id,
        invoice_number="INV-TEST-001",
        stripe_invoice_id="in_test123",
        status="PAID",
        amount=99.99,
        currency="USD",
        description="Test subscription payment",
    )
    db_session.add(invoice)
    await db_session.commit()
    await db_session.refresh(invoice)
    return invoice
