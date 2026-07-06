from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, index=True
    )
    scope: Mapped[str] = mapped_column(
        String(50), default="project"
    )  # project, dataset, evaluation_run
    scope_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    total_evaluations: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_score: Mapped[float] = mapped_column(Float, default=0.0)
    median_score: Mapped[float] = mapped_column(Float, default=0.0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    p95_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    p99_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)

    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100), index=True
    )  # e.g., "latency", "token_count", "score"
    value: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict
    )  # e.g., model, provider, judge
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, index=True
    )


class Trend(Base):
    __tablename__ = "trends"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    metric_name: Mapped[str] = mapped_column(String(100), index=True)
    granularity: Mapped[str] = mapped_column(String(20))  # daily, weekly, monthly
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    value: Mapped[float] = mapped_column(Float)
    change_from_previous: Mapped[float] = mapped_column(Float, default=0.0)
    dimensions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(
        String(50)
    )  # model, provider, dataset, benchmark, experiment
    entity_name: Mapped[str] = mapped_column(String(255))
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    evaluations_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, index=True
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(20))  # PDF, CSV
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING"
    )  # PENDING, GENERATING, COMPLETED, FAILED
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    filters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now
    )


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(50)
    )  # regression, improvement, latency, hallucination, safety, provider_instability
    severity: Mapped[str] = mapped_column(String(20))  # low, medium, high, critical
    message: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, index=True
    )


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(50)
    )  # failure_rate, latency, provider_down, queue_backlog, worker_crash, database_issue
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active, resolved
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class DashboardSnapshot(Base):
    __tablename__ = "dashboard_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100))
    layout: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now
    )
