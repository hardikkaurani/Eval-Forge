import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.models import AuditLog


class AuditService:
    """Records audit logs for user/role changes, key events, security settings, and exports."""

    async def log_event(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        workspace_id: Optional[uuid.UUID],
        user_id: uuid.UUID,
        action: str,
        details: dict = None,
        ip_address: str = None,
    ) -> AuditLog:
        log = AuditLog(
            id=uuid.uuid4(),
            organization_id=org_id,
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            created_at=datetime.utcnow(),
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    async def search_logs(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.organization_id == org_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())
