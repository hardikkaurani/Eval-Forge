from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid

if TYPE_CHECKING:
    from app.models.project import Project


class Dataset(Base):
    """SQLAlchemy model representing an evaluation dataset."""

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visibility: Mapped[str] = mapped_column(String(50), default="private", nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
    )

    project: Mapped["Project"] = relationship("Project", back_populates="datasets")
    versions: Mapped[List["DatasetVersion"]] = relationship(
        "DatasetVersion", back_populates="dataset", cascade="all, delete-orphan"
    )
    benchmarks: Mapped[List["BenchmarkSuite"]] = relationship(
        "BenchmarkSuite", secondary="benchmark_datasets", back_populates="datasets"
    )


class DatasetVersion(Base):
    """SQLAlchemy model representing an immutable version of a dataset."""

    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(50), default="1.0", nullable=False)
    hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="versions")
    records: Mapped[List["DatasetRecord"]] = relationship(
        "DatasetRecord", back_populates="version_ref", cascade="all, delete-orphan"
    )
    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment", back_populates="dataset_version", cascade="all, delete-orphan"
    )


class DatasetRecord(Base):
    """SQLAlchemy model representing a single structured record/sample within a dataset version."""

    __tablename__ = "dataset_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid, index=True
    )
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    input: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    ground_truth: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    custom_fields: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    version_ref: Mapped["DatasetVersion"] = relationship("DatasetVersion", back_populates="records")
