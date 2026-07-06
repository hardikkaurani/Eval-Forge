"""create analytics reporting observability tables

Revision ID: a7f8e9c0b1d2
Revises: f9b5a7c21e3f
Create Date: 2026-07-06 00:00:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7f8e9c0b1d2"
down_revision: Union[str, Sequence[str], None] = "f9b5a7c21e3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. analytics_snapshots
    op.create_table(
        "analytics_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scope", sa.String(length=50), nullable=False),
        sa.Column("scope_id", sa.String(length=36), nullable=True),
        sa.Column("total_evaluations", sa.Integer(), nullable=False),
        sa.Column("success_rate", sa.Float(), nullable=False),
        sa.Column("avg_score", sa.Float(), nullable=False),
        sa.Column("median_score", sa.Float(), nullable=False),
        sa.Column("avg_latency_ms", sa.Float(), nullable=False),
        sa.Column("p95_latency_ms", sa.Float(), nullable=False),
        sa.Column("p99_latency_ms", sa.Float(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analytics_snapshots_id"), "analytics_snapshots", ["id"], unique=False)
    op.create_index(op.f("ix_analytics_snapshots_timestamp"), "analytics_snapshots", ["timestamp"], unique=False)

    # 2. metrics
    op.create_table(
        "metrics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_metrics_id"), "metrics", ["id"], unique=False)
    op.create_index(op.f("ix_metrics_name"), "metrics", ["name"], unique=False)
    op.create_index(op.f("ix_metrics_timestamp"), "metrics", ["timestamp"], unique=False)

    # 3. trends
    op.create_table(
        "trends",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("granularity", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("change_from_previous", sa.Float(), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trends_id"), "trends", ["id"], unique=False)
    op.create_index(op.f("ix_trends_metric_name"), "trends", ["metric_name"], unique=False)

    # 4. leaderboards
    op.create_table(
        "leaderboards",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("evaluations_count", sa.Integer(), nullable=False),
        sa.Column("avg_latency_ms", sa.Float(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=False),
        sa.Column("snapshot_date", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leaderboards_id"), "leaderboards", ["id"], unique=False)
    op.create_index(op.f("ix_leaderboards_snapshot_date"), "leaderboards", ["snapshot_date"], unique=False)

    # 5. reports
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reports_id"), "reports", ["id"], unique=False)

    # 6. insights
    op.create_table(
        "insights",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insights_id"), "insights", ["id"], unique=False)
    op.create_index(op.f("ix_insights_created_at"), "insights", ["created_at"], unique=False)

    # 7. alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("actual_value", sa.Float(), nullable=True),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_id"), "alerts", ["id"], unique=False)
    op.create_index(op.f("ix_alerts_triggered_at"), "alerts", ["triggered_at"], unique=False)

    # 8. dashboard_snapshots
    op.create_table(
        "dashboard_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("layout", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dashboard_snapshots_id"), "dashboard_snapshots", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dashboard_snapshots_id"), table_name="dashboard_snapshots")
    op.drop_table("dashboard_snapshots")
    op.drop_index(op.f("ix_alerts_triggered_at"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_id"), table_name="alerts")
    op.drop_table("alerts")
    op.drop_index(op.f("ix_insights_created_at"), table_name="insights")
    op.drop_index(op.f("ix_insights_id"), table_name="insights")
    op.drop_table("insights")
    op.drop_index(op.f("ix_reports_id"), table_name="reports")
    op.drop_table("reports")
    op.drop_index(op.f("ix_leaderboards_snapshot_date"), table_name="leaderboards")
    op.drop_index(op.f("ix_leaderboards_id"), table_name="leaderboards")
    op.drop_table("leaderboards")
    op.drop_index(op.f("ix_trends_metric_name"), table_name="trends")
    op.drop_index(op.f("ix_trends_id"), table_name="trends")
    op.drop_table("trends")
    op.drop_index(op.f("ix_metrics_timestamp"), table_name="metrics")
    op.drop_index(op.f("ix_metrics_name"), table_name="metrics")
    op.drop_index(op.f("ix_metrics_id"), table_name="metrics")
    op.drop_table("metrics")
    op.drop_index(op.f("ix_analytics_snapshots_timestamp"), table_name="analytics_snapshots")
    op.drop_index(op.f("ix_analytics_snapshots_id"), table_name="analytics_snapshots")
    op.drop_table("analytics_snapshots")
