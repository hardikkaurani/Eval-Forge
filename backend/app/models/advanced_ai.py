from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid

if TYPE_CHECKING:
    from app.models.evaluation import EvaluationResult, EvaluationRun
    from app.models.project import Project


class RAGEvaluation(Base):
    __tablename__ = "rag_evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("evaluation_runs.id", ondelete="SET NULL"), nullable=True
    )
    context_precision: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    context_recall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    answer_relevancy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    faithfulness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    groundedness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    citation_validation: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    source_attribution: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    context_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    knowledge_utilization: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    custom_retrieval_metrics: Mapped[dict] = mapped_column(
        JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")
    run: Mapped[Optional["EvaluationRun"]] = relationship("EvaluationRun")


class HallucinationReport(Base):
    __tablename__ = "hallucination_reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evaluation_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    unsupported_claims: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    fabricated_facts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    missing_citations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    contradictions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    reasoning_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_mismatch: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    detailed_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")
    result: Mapped["EvaluationResult"] = relationship("EvaluationResult")


class SafetyEvaluation(Base):
    __tablename__ = "safety_evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evaluation_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    toxicity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hate_speech_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    harassment_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    violence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    self_harm_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    illegal_content_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    adult_content_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    policy_violations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    safety_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")
    result: Mapped["EvaluationResult"] = relationship("EvaluationResult")


class SecurityEvaluation(Base):
    __tablename__ = "security_evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evaluation_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    prompt_injection_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    jailbreak_detected: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    pii_exposure: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    secret_leakage: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    unsafe_output: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    policy_compliance: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    report: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")
    result: Mapped["EvaluationResult"] = relationship("EvaluationResult")


class ConversationEvaluation(Base):
    __tablename__ = "conversation_evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    turns_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    memory_retention_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    context_preservation_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    coherence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    response_consistency_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    user_satisfaction_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    avg_turn_length: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metrics_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")


class AgentEvaluation(Base):
    __tablename__ = "agent_evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    planning_quality: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    task_completion: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    memory_consistency: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    reasoning_trace_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    tool_usage_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    conversation_quality: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    agent_collaboration_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    agent_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")


class Policy(Base):
    __tablename__ = "enterprise_policies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")


class RegressionRun(Base):
    __tablename__ = "regression_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    base_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False
    )
    compare_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False
    )
    metrics_comparison: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    regression_detected: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    report_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")
    base_run: Mapped["EvaluationRun"] = relationship(
        "EvaluationRun", foreign_keys=[base_run_id]
    )
    compare_run: Mapped["EvaluationRun"] = relationship(
        "EvaluationRun", foreign_keys=[compare_run_id]
    )


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # model, agent, prompt
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    security_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    safety_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    overall_risk_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    assessment_report: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    project: Mapped["Project"] = relationship("Project")
