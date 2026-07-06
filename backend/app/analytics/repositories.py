from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import (
    Alert,
    AnalyticsSnapshot,
    DashboardSnapshot,
    Insight,
    Leaderboard,
    Metric,
    Report,
    Trend,
)


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Analytics Snapshots ---
    async def create_snapshot(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        self.db.add(snapshot)
        return snapshot

    async def get_latest_snapshot(
        self, project_id: str, scope: str = "project", scope_id: Optional[str] = None
    ) -> Optional[AnalyticsSnapshot]:
        conditions = [
            AnalyticsSnapshot.project_id == project_id,
            AnalyticsSnapshot.scope == scope,
        ]
        if scope_id:
            conditions.append(AnalyticsSnapshot.scope_id == scope_id)

        stmt = (
            select(AnalyticsSnapshot)
            .where(and_(*conditions))
            .order_by(desc(AnalyticsSnapshot.timestamp))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_snapshots(
        self,
        project_id: str,
        scope: str = "project",
        scope_id: Optional[str] = None,
        limit: int = 30,
    ) -> List[AnalyticsSnapshot]:
        conditions = [
            AnalyticsSnapshot.project_id == project_id,
            AnalyticsSnapshot.scope == scope,
        ]
        if scope_id:
            conditions.append(AnalyticsSnapshot.scope_id == scope_id)

        stmt = (
            select(AnalyticsSnapshot)
            .where(and_(*conditions))
            .order_by(desc(AnalyticsSnapshot.timestamp))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Metrics ---
    async def log_metric(self, metric: Metric) -> Metric:
        self.db.add(metric)
        return metric

    async def get_metrics(
        self,
        project_id: str,
        name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Metric]:
        conditions = [Metric.project_id == project_id]
        if name:
            conditions.append(Metric.name == name)
        if start_time:
            conditions.append(Metric.timestamp >= start_time)
        if end_time:
            conditions.append(Metric.timestamp <= end_time)

        stmt = (
            select(Metric)
            .where(and_(*conditions))
            .order_by(desc(Metric.timestamp))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Trends ---
    async def save_trend(self, trend: Trend) -> Trend:
        self.db.add(trend)
        return trend

    async def list_trends(
        self,
        project_id: str,
        metric_name: Optional[str] = None,
        granularity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Trend]:
        conditions = [Trend.project_id == project_id]
        if metric_name:
            conditions.append(Trend.metric_name == metric_name)
        if granularity:
            conditions.append(Trend.granularity == granularity)
        if start_time:
            conditions.append(Trend.end_date >= start_time)
        if end_time:
            conditions.append(Trend.start_date <= end_time)

        stmt = select(Trend).where(and_(*conditions)).order_by(desc(Trend.end_date))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Leaderboards ---
    async def save_leaderboard_entry(self, entry: Leaderboard) -> Leaderboard:
        self.db.add(entry)
        return entry

    async def get_leaderboard(
        self, project_id: str, entity_type: str, limit: int = 50
    ) -> List[Leaderboard]:
        stmt = (
            select(Leaderboard)
            .where(
                and_(
                    Leaderboard.project_id == project_id,
                    Leaderboard.entity_type == entity_type,
                )
            )
            .order_by(Leaderboard.rank)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def clear_leaderboard(self, project_id: str, entity_type: str) -> None:
        stmt = delete(Leaderboard).where(
            and_(
                Leaderboard.project_id == project_id,
                Leaderboard.entity_type == entity_type,
            )
        )
        await self.db.execute(stmt)

    # --- Reports ---
    async def create_report(self, report: Report) -> Report:
        self.db.add(report)
        return report

    async def get_report(self, report_id: str) -> Optional[Report]:
        stmt = select(Report).where(Report.id == report_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        project_id: str,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Report], int]:
        conditions = [Report.project_id == project_id]
        if report_type:
            conditions.append(Report.type == report_type)
        if status:
            conditions.append(Report.status == status)

        stmt = (
            select(Report)
            .where(and_(*conditions))
            .order_by(desc(Report.created_at))
            .offset(skip)
            .limit(limit)
        )

        count_stmt = select(func.count()).select_from(Report).where(and_(*conditions))

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        return list(result.scalars().all()), count_result.scalar_one()

    # --- Insights ---
    async def create_insight(self, insight: Insight) -> Insight:
        self.db.add(insight)
        return insight

    async def get_insight(self, insight_id: str) -> Optional[Insight]:
        stmt = select(Insight).where(Insight.id == insight_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_insights(
        self,
        project_id: str,
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
    ) -> List[Insight]:
        conditions = [Insight.project_id == project_id]
        if insight_type:
            conditions.append(Insight.type == insight_type)
        if severity:
            conditions.append(Insight.severity == severity)

        stmt = (
            select(Insight)
            .where(and_(*conditions))
            .order_by(desc(Insight.created_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Alerts ---
    async def create_alert(self, alert: Alert) -> Alert:
        self.db.add(alert)
        return alert

    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_alerts(
        self, project_id: str, status: Optional[str] = None, limit: int = 50
    ) -> List[Alert]:
        conditions = [Alert.project_id == project_id]
        if status:
            conditions.append(Alert.status == status)

        stmt = (
            select(Alert)
            .where(and_(*conditions))
            .order_by(desc(Alert.triggered_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Dashboard Snapshots ---
    async def save_dashboard_snapshot(
        self, snapshot: DashboardSnapshot
    ) -> DashboardSnapshot:
        self.db.add(snapshot)
        return snapshot

    async def get_dashboard_snapshot(
        self, project_id: str, snapshot_id: str
    ) -> Optional[DashboardSnapshot]:
        stmt = select(DashboardSnapshot).where(
            and_(
                DashboardSnapshot.project_id == project_id,
                DashboardSnapshot.id == snapshot_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_dashboard_snapshots(
        self, project_id: str
    ) -> List[DashboardSnapshot]:
        stmt = (
            select(DashboardSnapshot)
            .where(DashboardSnapshot.project_id == project_id)
            .order_by(desc(DashboardSnapshot.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
