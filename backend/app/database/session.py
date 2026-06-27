from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.config import settings

# Create asynchronous engine with production-grade connection pooling
engine = create_async_engine(
    settings.get_database_url,
    echo=settings.DEBUG,
    future=True,
    pool_size=20,  # Maintain up to 20 connection slots in pool
    max_overflow=10,  # Allow up to 10 additional temporary connections
    pool_timeout=30,  # Seconds to wait before erroring on connection request
    pool_recycle=1800,  # Recycle connections after 30 minutes to avoid stale sockets
    pool_pre_ping=True,  # Test connection health before delivering from pool
)

# Session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an asynchronous database session.

    Ensures that session is properly closed after use under all conditions.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
