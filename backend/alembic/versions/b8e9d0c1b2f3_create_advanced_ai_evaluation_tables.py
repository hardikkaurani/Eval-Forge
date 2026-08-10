"""create advanced ai evaluation tables

Revision ID: b8e9d0c1b2f3
Revises: a7f8e9c0b1d2
Create Date: 2026-07-06 01:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8e9d0c1b2f3"
down_revision: Union[str, Sequence[str], None] = "a7f8e9c0b1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. rag_evaluations
    op.create_table(
        "rag_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=True),
        sa.Column("context_precision", sa.Float(), nullable=False),
        sa.Column("context_recall", sa.Float(), nullable=False),
        sa.Column("answer_relevancy", sa.Float(), nullable=False),
        sa.Column("faithfulness", sa.Float(), nullable=False),
        sa.Column("groundedness", sa.Float(), nullable=False),
        sa.Column("citation_validation", sa.Float(), nullable=False),
        sa.Column("source_attribution", sa.Float(), nullable=False),
        sa.Column("context_coverage", sa.Float(), nullable=False),
        sa.Column("knowledge_utilization", sa.Float(), nullable=False),
        sa.Column("custom_retrieval_metrics", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["run_id"], ["evaluation_runs.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_rag_evaluations_id"), "rag_evaluations", ["id"], unique=False
    )

    # 2. hallucination_reports
    op.create_table(
        "hallucination_reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("unsupported_claims", sa.JSON(), nullable=False),
        sa.Column("fabricated_facts", sa.JSON(), nullable=False),
        sa.Column("missing_citations", sa.JSON(), nullable=False),
        sa.Column("contradictions", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("reasoning_trace", sa.Text(), nullable=True),
        sa.Column("evidence_mismatch", sa.Boolean(), nullable=False),
        sa.Column("detailed_explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["result_id"], ["evaluation_results.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hallucination_reports_id"),
        "hallucination_reports",
        ["id"],
        unique=False,
    )

    # 3. safety_evaluations
    op.create_table(
        "safety_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("toxicity_score", sa.Float(), nullable=False),
        sa.Column("hate_speech_score", sa.Float(), nullable=False),
        sa.Column("harassment_score", sa.Float(), nullable=False),
        sa.Column("violence_score", sa.Float(), nullable=False),
        sa.Column("self_harm_score", sa.Float(), nullable=False),
        sa.Column("illegal_content_score", sa.Float(), nullable=False),
        sa.Column("adult_content_score", sa.Float(), nullable=False),
        sa.Column("policy_violations", sa.JSON(), nullable=False),
        sa.Column("safety_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["result_id"], ["evaluation_results.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_safety_evaluations_id"), "safety_evaluations", ["id"], unique=False
    )

    # 4. security_evaluations
    op.create_table(
        "security_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("prompt_injection_score", sa.Float(), nullable=False),
        sa.Column("jailbreak_detected", sa.Boolean(), nullable=False),
        sa.Column("pii_exposure", sa.JSON(), nullable=False),
        sa.Column("secret_leakage", sa.JSON(), nullable=False),
        sa.Column("unsafe_output", sa.Boolean(), nullable=False),
        sa.Column("policy_compliance", sa.Boolean(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("report", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["result_id"], ["evaluation_results.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_security_evaluations_id"), "security_evaluations", ["id"], unique=False
    )

    # 5. conversation_evaluations
    op.create_table(
        "conversation_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("turns_count", sa.Integer(), nullable=False),
        sa.Column("memory_retention_score", sa.Float(), nullable=False),
        sa.Column("context_preservation_score", sa.Float(), nullable=False),
        sa.Column("coherence_score", sa.Float(), nullable=False),
        sa.Column("response_consistency_score", sa.Float(), nullable=False),
        sa.Column("user_satisfaction_score", sa.Float(), nullable=False),
        sa.Column("avg_turn_length", sa.Float(), nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversation_evaluations_id"),
        "conversation_evaluations",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversation_evaluations_session_id"),
        "conversation_evaluations",
        ["session_id"],
        unique=False,
    )

    # 6. agent_evaluations
    op.create_table(
        "agent_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=255), nullable=False),
        sa.Column("planning_quality", sa.Float(), nullable=False),
        sa.Column("task_completion", sa.Float(), nullable=False),
        sa.Column("memory_consistency", sa.Float(), nullable=False),
        sa.Column("reasoning_trace_score", sa.Float(), nullable=False),
        sa.Column("tool_usage_score", sa.Float(), nullable=False),
        sa.Column("conversation_quality", sa.Float(), nullable=False),
        sa.Column("agent_collaboration_score", sa.Float(), nullable=False),
        sa.Column("agent_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_agent_evaluations_id"), "agent_evaluations", ["id"], unique=False
    )

    # 7. enterprise_policies
    op.create_table(
        "enterprise_policies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rules", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_enterprise_policies_id"), "enterprise_policies", ["id"], unique=False
    )

    # 8. regression_runs
    op.create_table(
        "regression_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("base_run_id", sa.String(length=36), nullable=False),
        sa.Column("compare_run_id", sa.String(length=36), nullable=False),
        sa.Column("metrics_comparison", sa.JSON(), nullable=False),
        sa.Column("regression_detected", sa.Boolean(), nullable=False),
        sa.Column("report_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["base_run_id"], ["evaluation_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["compare_run_id"], ["evaluation_runs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_regression_runs_id"), "regression_runs", ["id"], unique=False
    )

    # 9. prompt_versions
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("prompt_template", sa.Text(), nullable=False),
        sa.Column("variables", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prompt_versions_id"), "prompt_versions", ["id"], unique=False
    )

    # 10. risk_assessments
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=255), nullable=False),
        sa.Column("security_score", sa.Float(), nullable=False),
        sa.Column("safety_score", sa.Float(), nullable=False),
        sa.Column("overall_risk_score", sa.Float(), nullable=False),
        sa.Column("assessment_report", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_risk_assessments_id"), "risk_assessments", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_risk_assessments_id"), table_name="risk_assessments")
    op.drop_table("risk_assessments")
    op.drop_index(op.f("ix_prompt_versions_id"), table_name="prompt_versions")
    op.drop_table("prompt_versions")
    op.drop_index(op.f("ix_regression_runs_id"), table_name="regression_runs")
    op.drop_table("regression_runs")
    op.drop_index(op.f("ix_enterprise_policies_id"), table_name="enterprise_policies")
    op.drop_table("enterprise_policies")
    op.drop_index(op.f("ix_agent_evaluations_id"), table_name="agent_evaluations")
    op.drop_table("agent_evaluations")
    op.drop_index(
        op.f("ix_conversation_evaluations_session_id"),
        table_name="conversation_evaluations",
    )
    op.drop_index(
        op.f("ix_conversation_evaluations_id"), table_name="conversation_evaluations"
    )
    op.drop_table("conversation_evaluations")
    op.drop_index(op.f("ix_security_evaluations_id"), table_name="security_evaluations")
    op.drop_table("security_evaluations")
    op.drop_index(op.f("ix_safety_evaluations_id"), table_name="safety_evaluations")
    op.drop_table("safety_evaluations")
    op.drop_index(
        op.f("ix_hallucination_reports_id"), table_name="hallucination_reports"
    )
    op.drop_table("hallucination_reports")
    op.drop_index(op.f("ix_rag_evaluations_id"), table_name="rag_evaluations")
    op.drop_table("rag_evaluations")
