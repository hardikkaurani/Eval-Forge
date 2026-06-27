from typing import AsyncGenerator
from redis.asyncio import Redis
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import Settings, settings
from app.core.redis import redis_manager
from app.database.session import get_db as db_generator

logger = structlog.get_logger()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider to obtain an asynchronous database session."""
    async for session in db_generator():
        yield session


def get_settings() -> Settings:
    """Dependency provider to obtain application configuration settings."""
    return settings


def get_redis() -> Redis:
    """Dependency provider to obtain the active Redis client."""
    return redis_manager.get_client()


def get_logger() -> structlog.stdlib.BoundLogger:
    """Dependency provider to obtain the structured logger."""
    return logger


async def get_current_user_placeholder() -> dict:
    """Placeholder dependency provider for future user authentication compatibility.

    Currently returns an anonymous user context. Can be replaced with actual
    JWT/OAuth verification in future phases.
    """
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "email": "anonymous@evalforge.ai",
        "role": "anonymous",
        "is_active": True,
    }
