from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid

if TYPE_CHECKING:
    from app.models.project import Project


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    project: Mapped["Project"] = relationship("Project", back_populates="evaluations")
    runs: Mapped[list["EvaluationRun"]] = relationship(
        "EvaluationRun", back_populates="evaluation", cascade="all, delete-orphan"
    )


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    evaluation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False
    )  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    judge: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # geval, pairwise, rubric, reference
    provider: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # openai, gemini, etc.
    provider_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    aggregate_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    evaluation: Mapped["Evaluation"] = relationship("Evaluation", back_populates="runs")
    results: Mapped[list["EvaluationResult"]] = relationship(
        "EvaluationResult", back_populates="run", cascade="all, delete-orphan"
    )


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False
    )
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model_output: Mapped[str] = mapped_column(Text, nullable=False)
    reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    judge: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    run: Mapped["EvaluationRun"] = relationship(
        "EvaluationRun", back_populates="results"
    )
    rubric_scores: Mapped[list["RubricScore"]] = relationship(
        "RubricScore", back_populates="result", cascade="all, delete-orphan"
    )
    provider_metadata: Mapped[list["ProviderMetadata"]] = relationship(
        "ProviderMetadata", back_populates="result", cascade="all, delete-orphan"
    )


class RubricScore(Base):
    __tablename__ = "rubric_scores"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evaluation_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    criterion_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rubric_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    result: Mapped["EvaluationResult"] = relationship(
        "EvaluationResult", back_populates="rubric_scores"
    )


class ProviderMetadata(Base):
    __tablename__ = "provider_metadata"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    result_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evaluation_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    result: Mapped["EvaluationResult"] = relationship(
        "EvaluationResult", back_populates="provider_metadata"
    )
