from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RubricConfigSchema(BaseModel):
    name: str
    description: str
    weight: float = 1.0
    scoring_scale: int = 5
    prompt_template: Optional[str] = None


class EvaluationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: str


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime


class EvaluationRunCreate(BaseModel):
    judge: str
    provider: str
    configuration: Dict[str, Any] = Field(default_factory=dict)
    total_cases: int = 0


class EvaluationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evaluation_id: str
    status: str
    judge: str
    provider: str
    configuration: Dict[str, Any]
    total_cases: int
    completed_cases: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    aggregate_score: Optional[float] = None


class RubricScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    criterion_name: str
    score: float
    reasoning: Optional[str] = None


class ProviderMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_name: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_ms: Optional[int] = None


class EvaluationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    input_prompt: str
    model_output: str
    reference: Optional[str] = None
    score: float
    passed: bool
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    evaluated_at: datetime
    rubric_scores: List[RubricScoreResponse] = Field(default_factory=list)
    provider_metadata: List[ProviderMetadataResponse] = Field(default_factory=list)


class TestCaseInput(BaseModel):
    input_prompt: str
    model_output: str
    reference: Optional[str] = None
    response_b: Optional[str] = None  # Specific to pairwise


class BatchEvaluationRequest(BaseModel):
    project_id: str
    evaluation_name: str
    evaluation_description: Optional[str] = None
    judge: str = "rubric"  # rubric, geval, pairwise, reference
    provider: str = "openai"  # openai, gemini, etc.
    rubric: Optional[RubricConfigSchema] = None
    test_cases: List[TestCaseInput]
    configuration: Dict[str, Any] = Field(
        default_factory=lambda: {
            "temperature": 0.0,
            "max_tokens": None,
            "threshold": 0.7,
            "timeout": 30.0,
        }
    )


class ProviderInfo(BaseModel):
    key: str
    name: str


class JudgeInfo(BaseModel):
    key: str
    name: str


class RubricInfo(BaseModel):
    key: str
    name: str
    description: str
    scoring_scale: int
