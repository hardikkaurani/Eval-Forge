import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.models import EnterpriseAPIKey


class EnterpriseAPIKeyService:
    """Generates, rotates, hashes, and revokes scoped organization/workspace keys."""

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

    async def revoke_key(self, db: AsyncSession, key_id: uuid.UUID) -> bool:
        stmt = select(EnterpriseAPIKey).where(EnterpriseAPIKey.id == key_id)
        res = await db.execute(stmt)
        key_record = res.scalar_one_or_none()
        if not key_record:
            return False

        key_record.is_active = False
        await db.commit()
        return True
