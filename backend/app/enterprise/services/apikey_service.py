import asyncio
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.redis import redis_manager
from app.enterprise.models import EnterpriseAPIKey


class EnterpriseAPIKeyContainer:
    """Lightweight container representing a cached API key record."""

    def __init__(self, data: dict):
        self.id = data.get("id")
        self.organization_id = data.get("organization_id")
        self.workspace_id = data.get("workspace_id")
        self.name = data.get("name", "API Key")
        self.scopes = data.get("scopes", ["read:all"])
        self.is_active = data.get("is_active", True)
        self.expires_at = data.get("expires_at")
        self.tier = data.get("tier", "FREE")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "organization_id": (
                str(self.organization_id) if self.organization_id else None
            ),
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "name": self.name,
            "scopes": self.scopes,
            "is_active": self.is_active,
            "expires_at": self.expires_at,
            "tier": self.tier,
        }


class EnterpriseAPIKeyService:
    """Generates, rotates, hashes, and revokes scoped organization/workspace keys."""

    _single_flight_locks: Dict[str, asyncio.Lock] = {}

    def _hash_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    async def generate_key(
        self,
        db: AsyncSession,
        name: str,
        org_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        scopes: List[str] = None,
        expires_in_days: int = 30,
    ) -> tuple[str, EnterpriseAPIKey]:
        raw_key = f"ef_ent_{uuid.uuid4().hex}"
        key_hash = self._hash_key(raw_key)

        expires_at = (
            datetime.utcnow() + timedelta(days=expires_in_days)
            if expires_in_days
            else None
        )

        key_record = EnterpriseAPIKey(
            id=uuid.uuid4(),
            organization_id=org_id,
            workspace_id=workspace_id,
            name=name,
            key_hash=key_hash,
            scopes=scopes or ["read:all"],
            is_active=True,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )
        db.add(key_record)
        await db.commit()
        await db.refresh(key_record)
        return raw_key, key_record

    async def validate_key(
        self, db: AsyncSession, raw_key: str
    ) -> Optional[EnterpriseAPIKey]:
        key_hash = self._hash_key(raw_key)
        stmt = select(EnterpriseAPIKey).where(
            EnterpriseAPIKey.key_hash == key_hash, EnterpriseAPIKey.is_active
        )
        res = await db.execute(stmt)
        key_record = res.scalar_one_or_none()

        if not key_record:
            return None

        # Check expiration
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            key_record.is_active = False
            await db.commit()
            return None

        return key_record

    async def validate_key_cached(
        self, db: Optional[AsyncSession], raw_key: str
    ) -> Optional[EnterpriseAPIKeyContainer]:
        """Validates API key with Redis caching (evalforge:apikey:token:<hash>) and single-flight lock."""
        key_hash = self._hash_key(raw_key)
        cache_key = f"evalforge:apikey:token:{key_hash}"

        # 1. Warm Redis cache check
        if redis_manager.client:
            try:
                cached_val = await redis_manager.client.get(cache_key)
                if cached_val:
                    data = json.loads(cached_val)
                    if not data.get("is_active"):
                        return None
                    return EnterpriseAPIKeyContainer(data)
            except Exception:
                pass

        # 2. Single-flight request coalescing to prevent DB cache stampedes
        lock = self._single_flight_locks.setdefault(key_hash, asyncio.Lock())
        async with lock:
            if redis_manager.client:
                try:
                    cached_val = await redis_manager.client.get(cache_key)
                    if cached_val:
                        data = json.loads(cached_val)
                        if not data.get("is_active"):
                            return None
                        return EnterpriseAPIKeyContainer(data)
                except Exception:
                    pass

            key_record = None
            if db:
                key_record = await self.validate_key(db, raw_key)
            else:
                from app.database.session import SessionLocal

                async with SessionLocal() as session:
                    key_record = await self.validate_key(session, raw_key)

            if not key_record:
                if redis_manager.client:
                    try:
                        await redis_manager.client.setex(
                            cache_key, 60, json.dumps({"is_active": False})
                        )
                    except Exception:
                        pass
                return None

            container = EnterpriseAPIKeyContainer(
                {
                    "id": str(key_record.id),
                    "organization_id": (
                        str(key_record.organization_id)
                        if key_record.organization_id
                        else None
                    ),
                    "workspace_id": (
                        str(key_record.workspace_id)
                        if key_record.workspace_id
                        else None
                    ),
                    "name": key_record.name,
                    "scopes": key_record.scopes,
                    "is_active": key_record.is_active,
                    "expires_at": (
                        key_record.expires_at.isoformat()
                        if key_record.expires_at
                        else None
                    ),
                    "tier": getattr(key_record, "tier", "FREE"),
                }
            )

            if redis_manager.client:
                try:
                    await redis_manager.client.setex(
                        cache_key, 300, json.dumps(container.to_dict())
                    )
                except Exception:
                    pass

            return container

    async def revoke_key(self, db: AsyncSession, key_id: uuid.UUID) -> bool:
        stmt = select(EnterpriseAPIKey).where(EnterpriseAPIKey.id == key_id)
        res = await db.execute(stmt)
        key_record = res.scalar_one_or_none()
        if not key_record:
            return False

        key_record.is_active = False
        await db.commit()

        if redis_manager.client and key_record.key_hash:
            try:
                cache_key = f"evalforge:apikey:token:{key_record.key_hash}"
                await redis_manager.client.delete(cache_key)
            except Exception:
                pass

        return True
