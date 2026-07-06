import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.exceptions import PlanQuotaExceededException
from app.enterprise.models import Quota, UsageRecord


class QuotaService:
    """Manages soft limits, hard limits, usage tracking, warning banners, and grace periods."""

    async def record_usage(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        metric: str,
        value: float,
    ) -> UsageRecord:
        # Create usage record
        record = UsageRecord(
            id=uuid.uuid4(),
            organization_id=org_id,
            workspace_id=workspace_id,
            metric=metric,
            value=value,
            timestamp=datetime.utcnow(),
        )
        db.add(record)

        # Update or create the active Quota record
        stmt = select(Quota).where(
            Quota.organization_id == org_id,
            Quota.workspace_id == workspace_id,
            Quota.metric == metric,
        )
        res = await db.execute(stmt)
        quota = res.scalar_one_or_none()

        if quota:
            quota.current_value += value
        else:
            # Create a default quota with 5000 limit if not present
            quota = Quota(
                id=uuid.uuid4(),
                organization_id=org_id,
                workspace_id=workspace_id,
                metric=metric,
                limit_value=5000.0,
                current_value=value,
                reset_at=datetime.utcnow() + timedelta(days=30),
            )
            db.add(quota)

        # Check if hard limit is breached
        if quota.current_value > quota.limit_value:
            raise PlanQuotaExceededException(
                f"Hard quota limit of {quota.limit_value} exceeded for metric '{metric}'."
            )

        await db.commit()
        return record

    async def check_quota_status(
        self, db: AsyncSession, org_id: uuid.UUID, workspace_id: uuid.UUID, metric: str
    ) -> dict:
        stmt = select(Quota).where(
            Quota.organization_id == org_id,
            Quota.workspace_id == workspace_id,
            Quota.metric == metric,
        )
        res = await db.execute(stmt)
        quota = res.scalar_one_or_none()

        if not quota:
            return {"metric": metric, "limit": 5000.0, "current": 0.0, "status": "ok"}

        pct = (quota.current_value / quota.limit_value) * 100
        status = "ok"
        if pct >= 100:
            status = "hard_limit_exceeded"
        elif pct >= 85:
            status = "warning"

        return {
            "metric": metric,
            "limit": quota.limit_value,
            "current": quota.current_value,
            "status": status,
            "reset_at": quota.reset_at,
        }
