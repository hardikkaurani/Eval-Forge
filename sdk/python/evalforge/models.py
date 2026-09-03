from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    workspace_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Dataset(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class EvaluationRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    status: str
    total_cases: int = 0
    completed_cases: int = 0
    failed_cases: int = 0
    created_at: Optional[datetime] = None


class EvaluationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    input_prompt: str
    model_output: str
    reference: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    passed: bool = True
    latency_ms: Optional[int] = None


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    status: str
    job_type: str
    progress: float = 0.0
    created_at: Optional[datetime] = None
