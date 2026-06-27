import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.redis import redis_manager
from app.database.session import Base, get_db
from app.main import app

# SQLite in-memory database URL for testing async sessions
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def mock_redis() -> Generator[None, None, None]:
    """Mocks redis_manager connectivity to prevent dependency errors during test runs."""
    ping_mock = AsyncMock(return_value=True)
    close_mock = AsyncMock()
    with (
        patch.object(redis_manager, "ping", ping_mock),
        patch.object(redis_manager, "init", return_value=None),
        patch.object(redis_manager, "close", close_mock),
    ):
        yield


@pytest.fixture(name="db_session")
def db_session_fixture() -> Generator[AsyncSession, None, None]:
    """Initializes schema on in-memory SQLite synchronously, yields session,

    and drops tables on teardown.
    """
    loop = asyncio.new_event_loop()

    engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Run table creation synchronously in the loop
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(create_tables())

    session = TestingSessionLocal()

    yield session

    # Run cleanup synchronously in the loop
    async def destroy_tables():
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    loop.run_until_complete(destroy_tables())
    loop.close()


@pytest.fixture(name="client")
def client_fixture(
    db_session: AsyncSession,
) -> Generator[TestClient, None, None]:
    """Overrides get_db dependency to point to the test session and returns a TestClient."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
