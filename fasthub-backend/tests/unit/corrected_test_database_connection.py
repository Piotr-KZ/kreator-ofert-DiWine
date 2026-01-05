"""Test database connection utilities"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, engine

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection can be established"""
    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        assert result is not None

@pytest.mark.asyncio
async def test_get_db_session():
    """Test get_db returns AsyncSession"""
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break  # Only test first yield

@pytest.mark.asyncio
async def test_session_transaction():
    """Test session can execute queries"""
    async for session in get_db():
        result = await session.execute("SELECT 1 as value")
        row = result.first()
        assert row.value == 1
        break
