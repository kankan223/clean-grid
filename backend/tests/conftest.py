"""
Pytest configuration for CleanGrid backend tests
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ["DATABASE_URL"] = "postgresql+asyncpg://cleangrid:cleangrid@localhost:5432/cleangrid_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-pytests-only"

import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.models.points import User, UserRole




@pytest.fixture
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "postgresql+asyncpg://cleangrid:cleangrid@localhost:5432/cleangrid_test",
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Create test database session"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Create test client with database override"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Create admin user for testing"""
    import uuid
    
    admin_user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        display_name="Test Admin",
        role=UserRole.ADMIN,
        total_points=100,
        is_active=True,
        email_verified=True,
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    return admin_user


@pytest.fixture
async def crew_user(db_session: AsyncSession):
    """Create crew user for testing"""
    import uuid
    
    crew_user = User(
        id=uuid.uuid4(),
        email="crew@test.com",
        display_name="Test Crew",
        role=UserRole.CREW,
        total_points=50,
        is_active=True,
        email_verified=True,
    )
    db_session.add(crew_user)
    await db_session.commit()
    await db_session.refresh(crew_user)
    return crew_user


@pytest.fixture
async def citizen_user(db_session: AsyncSession):
    """Create citizen user for testing"""
    import uuid
    
    citizen_user = User(
        id=uuid.uuid4(),
        email="citizen@test.com",
        display_name="Test Citizen",
        role=UserRole.CITIZEN,
        total_points=25,
        is_active=True,
        email_verified=True,
    )
    db_session.add(citizen_user)
    await db_session.commit()
    await db_session.refresh(citizen_user)
    return citizen_user
