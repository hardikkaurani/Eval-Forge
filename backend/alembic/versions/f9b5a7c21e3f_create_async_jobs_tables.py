"""create async jobs tables

Revision ID: f9b5a7c21e3f
Revises: d83a17e8b91a
Create Date: 2026-07-05 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f9b5a7c21e3f"
down_revision: Union[str, Sequence[str], None] = "d83a17e8b91a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("queue_name", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("worker_id", sa.String(length=255), nullable=True),
        sa.Column("progress", sa.Float(), nullable=False),
        sa.Column("current_step", sa.String(length=255), nullable=True),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recurring_cron", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_id"), "jobs", ["id"], unique=False)

    # 2. job_logs
    op.create_table(
        "job_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("log_level", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_logs_id"), "job_logs", ["id"], unique=False)

    # 3. workers
    op.create_table(
        "workers",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("queue_name", sa.String(length=100), nullable=False),
        sa.Column("current_job_id", sa.String(length=36), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), nullable=False),
        sa.Column("system_load", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workers_id"), "workers", ["id"], unique=False)

    # 4. queues
    op.create_table(
        "queues",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_queues_id"), "queues", ["id"], unique=False)

    # 5. execution_history
    op.create_table(
        "execution_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("worker_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_execution_history_id"), "execution_history", ["id"], unique=False
    )

    # 6. retry_history
    op.create_table(
        "retry_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("retry_attempt", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_retry_history_id"), "retry_history", ["id"], unique=False)

    # 7. cancellations
    op.create_table(
        "cancellations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("cancelled_by", sa.String(length=255), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cancellations_id"), "cancellations", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cancellations_id"), table_name="cancellations")
    op.drop_table("cancellations")
    op.drop_index(op.f("ix_retry_history_id"), table_name="retry_history")
    op.drop_table("retry_history")
    op.drop_index(op.f("ix_execution_history_id"), table_name="execution_history")
    op.drop_table("execution_history")
    op.drop_index(op.f("ix_queues_id"), table_name="queues")
    op.drop_table("queues")
    op.drop_index(op.f("ix_workers_id"), table_name="workers")
    op.drop_table("workers")
    op.drop_index(op.f("ix_job_logs_id"), table_name="job_logs")
    op.drop_table("job_logs")
    op.drop_index(op.f("ix_jobs_id"), table_name="jobs")
    op.drop_table("jobs")
