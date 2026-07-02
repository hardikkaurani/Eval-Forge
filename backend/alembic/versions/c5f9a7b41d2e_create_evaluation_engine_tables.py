"""Create evaluation engine tables

Revision ID: c5f9a7b41d2e
Revises: 32b927f78b0d
Create Date: 2026-07-02 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5f9a7b41d2e"
down_revision: Union[str, Sequence[str], None] = "32b927f78b0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluations_id"), "evaluations", ["id"], unique=False)

    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("judge", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("provider_model", sa.String(length=255), nullable=True),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("total_cases", sa.Integer(), nullable=False),
        sa.Column("completed_cases", sa.Integer(), nullable=False),
        sa.Column("failed_cases", sa.Integer(), nullable=False),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aggregate_score", sa.Float(), nullable=True),
        sa.Column("status_detail", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluation_runs_id"), "evaluation_runs", ["id"], unique=False)

    op.create_table(
        "evaluation_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("input_prompt", sa.Text(), nullable=False),
        sa.Column("model_output", sa.Text(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=True),
        sa.Column("judge", sa.String(length=100), nullable=True),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["evaluation_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluation_results_id"), "evaluation_results", ["id"], unique=False)

    op.create_table(
        "rubric_scores",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("criterion_name", sa.String(length=100), nullable=False),
        sa.Column("rubric_key", sa.String(length=100), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["result_id"], ["evaluation_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rubric_scores_id"), "rubric_scores", ["id"], unique=False)

    op.create_table(
        "provider_metadata",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["result_id"], ["evaluation_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_provider_metadata_id"), "provider_metadata", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_provider_metadata_id"), table_name="provider_metadata")
    op.drop_table("provider_metadata")
    op.drop_index(op.f("ix_rubric_scores_id"), table_name="rubric_scores")
    op.drop_table("rubric_scores")
    op.drop_index(op.f("ix_evaluation_results_id"), table_name="evaluation_results")
    op.drop_table("evaluation_results")
    op.drop_index(op.f("ix_evaluation_runs_id"), table_name="evaluation_runs")
    op.drop_table("evaluation_runs")
    op.drop_index(op.f("ix_evaluations_id"), table_name="evaluations")
    op.drop_table("evaluations")
