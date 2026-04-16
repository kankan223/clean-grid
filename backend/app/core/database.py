"""
Database configuration for CleanGrid Backend
Uses SQLAlchemy 2.0 async with asyncpg driver
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    poolclass=NullPool,  # Disable connection pooling for async
    pool_pre_ping=True,  # Verify connections before use
    future=True,  # Use SQLAlchemy 2.0 style
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent expired object access
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    Used in FastAPI endpoints with Depends(get_db)
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


async def init_db() -> None:
    """
    Initialize database tables
    Call this on application startup
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from app.models import user, incident, route, points  # noqa
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections
    Call this on application shutdown
    """
    await engine.dispose()


# Database health check
async def check_db_health() -> bool:
    """
    Check if database connection is healthy
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
