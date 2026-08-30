from typing import Any, AsyncGenerator, Optional

import structlog
from fastapi import Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import Settings, settings
from app.core.redis import redis_manager
from app.database.session import get_db as db_generator
from app.enterprise.services.apikey_service import EnterpriseAPIKeyService

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


async def validate_api_key(token: str, db: AsyncSession):
    """Validate an API key token and return the associated API key record."""
    if not token:
        return None
    key_service = EnterpriseAPIKeyService()
    return await key_service.validate_key(db, token)


def extract_workspace_id(api_key_record: Any) -> Optional[str]:
    """Safely extract workspace_id string from authenticated API key record."""
    if api_key_record and getattr(api_key_record, "workspace_id", None):
        return str(api_key_record.workspace_id)
    return None


_extract_workspace_id = extract_workspace_id


async def get_current_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    """Validate API key from X-API-Key header and return the associated API key record."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide it via X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    api_key_record = await validate_api_key(x_api_key, db)
    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key_record
