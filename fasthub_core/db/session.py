"""
Database session management
Async SQLAlchemy session factory for PostgreSQL
"""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from fasthub_core.config import get_settings


def get_async_database_url(url: str) -> str:
    """
    Convert PostgreSQL database URL to async format
    postgresql:// -> postgresql+asyncpg://
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# Lazy initialization - engine will be created on first access
_engine = None
_async_session_local = None


def get_engine():
    """Get or create the database engine"""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            get_async_database_url(settings.DATABASE_URL),
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
        )
    return _engine


def get_async_session_local():
    """Get or create the async session factory"""
    global _async_session_local
    if _async_session_local is None:
        _async_session_local = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_local


# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize the database engine (call before first use in CLI context)."""
    get_engine()


@asynccontextmanager
async def get_db_session():
    """
    Context manager dla sesji DB (poza FastAPI Depends).

    Użycie:
        async with get_db_session() as db:
            result = await db.execute(query)
    """
    session_factory = get_async_session_local()
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    session_local = get_async_session_local()
    async with session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
