"""
Pytest configuration and shared fixtures
"""

import os
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Test database URL - use from environment or fallback to GitHub Actions default
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:testpass@localhost:5432/testdb"
)

# Convert postgresql:// to postgresql+asyncpg:// for async engine
if TEST_DATABASE_URL.startswith("postgresql://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Ensure DATABASE_URL is set before importing app
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base, get_db
from app.main import app
from app.models import APIToken, Invoice, Organization, Subscription, User


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
    """Create database session for tests with automatic cleanup"""
    # Create tables if they don't exist
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

    # Clean up data after test using TRUNCATE (much faster than DROP/CREATE)
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE invoices, subscriptions, api_tokens, audit_logs, members, users, organizations RESTART IDENTITY CASCADE"))


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
    """Create async test client with rate limiter disabled"""
    # Mock limiter.limit() decorator to bypass rate limiting
    from app.core.rate_limit import limiter
    from unittest.mock import MagicMock
    
    original_limit = limiter.limit
    # Replace limiter.limit with a no-op decorator
    limiter.limit = lambda *args, **kwargs: lambda func: func
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Restore original limiter
    limiter.limit = original_limit


@pytest_asyncio.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """Create test organization"""
    org = Organization(name="Test Organization", slug="test-org", stripe_customer_id="cus_test123")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def owner_user(db_session: AsyncSession) -> User:
    """Create organization owner user"""
    user = User(
        email="owner@example.com",
        hashed_password=get_password_hash("ownerpass123"),
        full_name="Organization Owner",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test admin/superuser"""
    from app.models.member import Member
    
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Add admin to test organization
    member = Member(
        user_id=user.id,
        organization_id=test_organization.id,
        role="admin"
    )
    db_session.add(member)
    await db_session.commit()
    
    return user


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create membership
    from app.models.member import Member

    member = Member(
        user_id=user.id, organization_id=test_organization.id, role="admin"
    )
    db_session.add(member)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test_user"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def admin_headers(test_admin: User) -> dict:
    """Create authentication headers for test_admin"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(data={"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def test_api_token(db_session: AsyncSession, test_user: User) -> APIToken:
    """Create test API token"""
    token = APIToken(
        user_id=test_user.id,
        name="Test Token",
        token_hash=get_password_hash("test-token-secret"),
        scopes=["read", "write"],
        is_active=True,
    )
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)
    return token


@pytest_asyncio.fixture
async def test_subscription(
    db_session: AsyncSession, test_organization: Organization
) -> Subscription:
    """Create test subscription"""
    subscription = Subscription(
        organization_id=test_organization.id,
        stripe_subscription_id="sub_test123",
        stripe_price_id="price_test123",
        status="active",
        current_period_start=1234567890,
        current_period_end=1234567890 + 2592000,  # +30 days
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
        stripe_invoice_id="in_test123",
        invoice_number="INV-TEST-001",
        amount=1000.00,
        currency="usd",
        status="paid",
        pdf_url="https://example.com/invoice.pdf",
    )
    db_session.add(invoice)
    await db_session.commit()
    await db_session.refresh(invoice)
    return invoice
