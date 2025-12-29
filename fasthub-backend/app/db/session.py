"""
Database session management
Async SQLAlchemy session factory for PostgreSQL
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings


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


# Create async engine for PostgreSQL
engine = create_async_engine(
    get_async_database_url(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=20,  # Connection pool size
    max_overflow=10,  # Extra connections if pool full
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
