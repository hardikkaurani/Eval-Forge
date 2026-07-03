from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExperimentBase(BaseModel):
    name: str = Field(..., description="Descriptive experiment run name.")
    description: Optional[str] = Field(None, description="Detailed explanation of the experiment scope.")
    judge: str = Field(..., description="Name of the judge (e.g. rubrics, geval, pairwise).")
    provider: str = Field(..., description="LLM provider name (e.g. openai, gemini).")
    model: Optional[str] = Field(None, description="LLM model name.")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Pipeline and judge settings.")


class ExperimentCreate(ExperimentBase):
    dataset_version_id: str = Field(..., description="ID of the dataset version to execute over.")


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class ExperimentResponse(ExperimentBase):
    id: str
    project_id: str
    dataset_version_id: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ExperimentDetailResponse(ExperimentResponse):
    metrics: Dict[str, Any] = Field(default_factory=dict)
    results: List[Dict[str, Any]] = Field(default_factory=list)
