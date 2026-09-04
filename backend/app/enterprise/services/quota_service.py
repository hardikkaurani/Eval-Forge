import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.exceptions import PlanQuotaExceededException
from app.enterprise.models import Plan, Quota, Subscription, UsageRecord


class QuotaService:
    """Manages concurrency-safe usage metering, hard limits, warning thresholds, and billing cycle resets."""

    async def _get_default_limit_for_org(
        self, db: AsyncSession, org_id: uuid.UUID, metric: str
    ) -> float:
        """Resolves metric limit based on organization's active subscription plan."""
        stmt = (
            select(Plan)
            .join(Subscription, Subscription.plan_id == Plan.id)
            .where(
                Subscription.organization_id == org_id, Subscription.status == "active"
            )
            .order_by(Subscription.created_at.desc())
        )
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()

        if plan and isinstance(plan.limits, dict):
            if metric in plan.limits:
                return float(plan.limits[metric])
            if metric == "evaluations" and "evaluations" in plan.limits:
                return float(plan.limits["evaluations"])
            if metric == "api_requests" and "api_requests" in plan.limits:
                return float(plan.limits["api_requests"])
            if metric == "storage" and "storage_mb" in plan.limits:
                return float(plan.limits["storage_mb"])

        # Default fallback limits (Starter tier baseline)
        fallback_limits = {
            "evaluations": 100.0,
            "api_requests": 1000.0,
            "datasets": 50.0,
            "storage": 100.0,
            "concurrent_jobs": 5.0,
        }
        return fallback_limits.get(metric, 5000.0)

    async def record_usage(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        metric: str,
        value: float,
    ) -> UsageRecord:
        """Atomically meters usage and enforces hard quota limits under high concurrency."""
        if value < 0:
            raise ValueError("Usage increment value must be non-negative.")

        # 1. Acquire Quota with row-level lock (or select with fallback)
        try:
            stmt = (
                select(Quota)
                .where(
                    Quota.organization_id == org_id,
                    Quota.workspace_id == workspace_id,
                    Quota.metric == metric,
                )
                .with_for_update()
            )
            res = await db.execute(stmt)
            quota = res.scalar_one_or_none()
        except Exception:
            # Fallback for SQLite in memory testing where with_for_update is no-op
            stmt = select(Quota).where(
                Quota.organization_id == org_id,
                Quota.workspace_id == workspace_id,
                Quota.metric == metric,
            )
            res = await db.execute(stmt)
            quota = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if quota:
            # Handle monthly billing cycle reset
            if quota.reset_at and now >= quota.reset_at.replace(
                tzinfo=(
                    timezone.utc
                    if quota.reset_at.tzinfo is None
                    else quota.reset_at.tzinfo
                )
            ):
                quota.current_value = 0.0
                quota.reset_at = now + timedelta(days=30)

            # Check if hard limit would be breached
            if quota.current_value + value > quota.limit_value:
                raise PlanQuotaExceededException(
                    f"Hard quota limit of {quota.limit_value} exceeded for metric '{metric}' (current: {quota.current_value}, requested: {value})."
                )
            quota.current_value += value
        else:
            limit_val = await self._get_default_limit_for_org(db, org_id, metric)
            if value > limit_val:
                raise PlanQuotaExceededException(
                    f"Hard quota limit of {limit_val} exceeded for metric '{metric}' (requested: {value})."
                )
            quota = Quota(
                id=uuid.uuid4(),
                organization_id=org_id,
                workspace_id=workspace_id,
                metric=metric,
                limit_value=limit_val,
                current_value=value,
                reset_at=now + timedelta(days=30),
            )
            db.add(quota)

        # 2. Add audit UsageRecord
        record = UsageRecord(
            id=uuid.uuid4(),
            organization_id=org_id,
            workspace_id=workspace_id,
            metric=metric,
            value=value,
            timestamp=now,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def check_quota_status(
        self, db: AsyncSession, org_id: uuid.UUID, workspace_id: uuid.UUID, metric: str
    ) -> Dict[str, Any]:
        """Queries quota threshold status without mutating usage records."""
        stmt = select(Quota).where(
            Quota.organization_id == org_id,
            Quota.workspace_id == workspace_id,
            Quota.metric == metric,
        )
        res = await db.execute(stmt)
        quota = res.scalar_one_or_none()

        if not quota:
            default_limit = await self._get_default_limit_for_org(db, org_id, metric)
            return {
                "metric": metric,
                "limit": default_limit,
                "current": 0.0,
                "status": "ok",
                "percentage_used": 0.0,
            }

        curr_val = (
            float(quota.current_value) if quota.current_value is not None else 0.0
        )
        lim_val = float(quota.limit_value) if quota.limit_value is not None else 1.0
        pct = (curr_val / lim_val * 100.0) if lim_val > 0 else 100.0
        status = "ok"
        if pct >= 100:
            status = "hard_limit_exceeded"
        elif pct >= 80:
            status = "warning"

        return {
            "metric": metric,
            "limit": lim_val,
            "current": curr_val,
            "status": status,
            "percentage_used": round(float(pct), 2),
            "reset_at": quota.reset_at,
        }

    async def reserve_quota(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        metric: str,
        amount: float = 1.0,
    ) -> bool:
        """Atomically reserves quota under concurrency. Raises PlanQuotaExceededException if capacity is unavailable."""
        if amount <= 0:
            return True

        now = datetime.now(timezone.utc)
        try:
            stmt = (
                select(Quota)
                .where(
                    Quota.organization_id == org_id,
                    Quota.workspace_id == workspace_id,
                    Quota.metric == metric,
                )
                .with_for_update()
            )
            res = await db.execute(stmt)
            quota = res.scalar_one_or_none()
        except Exception:
            stmt = select(Quota).where(
                Quota.organization_id == org_id,
                Quota.workspace_id == workspace_id,
                Quota.metric == metric,
            )
            res = await db.execute(stmt)
            quota = res.scalar_one_or_none()

        if quota:
            if quota.reset_at and now >= quota.reset_at.replace(
                tzinfo=(
                    timezone.utc
                    if quota.reset_at.tzinfo is None
                    else quota.reset_at.tzinfo
                )
            ):
                quota.current_value = 0.0
                quota.reset_at = now + timedelta(days=30)

            if quota.current_value + amount > quota.limit_value:
                raise PlanQuotaExceededException(
                    f"Quota reservation failed: {metric} limit of {quota.limit_value} exceeded (current: {quota.current_value}, requested: {amount})."
                )
            quota.current_value += amount
        else:
            limit_val = await self._get_default_limit_for_org(db, org_id, metric)
            if amount > limit_val:
                raise PlanQuotaExceededException(
                    f"Quota reservation failed: {metric} limit of {limit_val} exceeded (requested: {amount})."
                )
            quota = Quota(
                id=uuid.uuid4(),
                organization_id=org_id,
                workspace_id=workspace_id,
                metric=metric,
                limit_value=limit_val,
                current_value=amount,
                reset_at=now + timedelta(days=30),
            )
            db.add(quota)

        await db.commit()
        return True

    async def release_quota(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        metric: str,
        amount: float = 1.0,
    ) -> bool:
        """Releases reserved quota following a canceled or failed operation."""
        if amount <= 0:
            return True

        stmt = select(Quota).where(
            Quota.organization_id == org_id,
            Quota.workspace_id == workspace_id,
            Quota.metric == metric,
        )
        res = await db.execute(stmt)
        quota = res.scalar_one_or_none()

        if quota:
            quota.current_value = max(0.0, float(quota.current_value) - amount)
            await db.commit()
        return True

    async def consume_quota(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        metric: str,
        amount: float = 1.0,
    ) -> UsageRecord:
        """Records durable UsageRecord for consumed resource capacity."""
        now = datetime.now(timezone.utc)
        record = UsageRecord(
            id=uuid.uuid4(),
            organization_id=org_id,
            workspace_id=workspace_id,
            metric=metric,
            value=amount,
            timestamp=now,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
