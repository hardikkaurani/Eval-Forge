from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RAGEvaluationCreate(BaseModel):
    project_id: str
    run_id: Optional[str] = None
    context_precision: float = 0.0
    context_recall: float = 0.0
    answer_relevancy: float = 0.0
    faithfulness: float = 0.0
    groundedness: float = 0.0
    citation_validation: float = 0.0
    source_attribution: float = 0.0
    context_coverage: float = 0.0
    knowledge_utilization: float = 0.0
    custom_retrieval_metrics: Dict[str, Any] = Field(default_factory=dict)


class RAGEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    run_id: Optional[str] = None
    context_precision: float
    context_recall: float
    answer_relevancy: float
    faithfulness: float
    groundedness: float
    citation_validation: float
    source_attribution: float
    context_coverage: float
    knowledge_utilization: float
    custom_retrieval_metrics: Dict[str, Any]
    created_at: datetime


class HallucinationReportCreate(BaseModel):
    project_id: str
    result_id: str
    unsupported_claims: List[str] = Field(default_factory=list)
    fabricated_facts: List[str] = Field(default_factory=list)
    missing_citations: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0
    reasoning_trace: Optional[str] = None
    evidence_mismatch: bool = False
    detailed_explanation: Optional[str] = None


class HallucinationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    result_id: str
    unsupported_claims: List[str]
    fabricated_facts: List[str]
    missing_citations: List[str]
    contradictions: List[str]
    confidence_score: float
    reasoning_trace: Optional[str]
    evidence_mismatch: bool
    detailed_explanation: Optional[str]
    created_at: datetime


class SafetyEvaluationCreate(BaseModel):
    project_id: str
    result_id: str
    toxicity_score: float = 0.0
    hate_speech_score: float = 0.0
    harassment_score: float = 0.0
    violence_score: float = 0.0
    self_harm_score: float = 0.0
    illegal_content_score: float = 0.0
    adult_content_score: float = 0.0
    policy_violations: List[str] = Field(default_factory=list)
    safety_score: float = 100.0


class SafetyEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    result_id: str
    toxicity_score: float
    hate_speech_score: float
    harassment_score: float
    violence_score: float
    self_harm_score: float
    illegal_content_score: float
    adult_content_score: float
    policy_violations: List[str]
    safety_score: float
    created_at: datetime


class SecurityEvaluationCreate(BaseModel):
    project_id: str
    result_id: str
    prompt_injection_score: float = 0.0
    jailbreak_detected: bool = False
    pii_exposure: List[str] = Field(default_factory=list)
    secret_leakage: List[str] = Field(default_factory=list)
    unsafe_output: bool = False
    policy_compliance: bool = True
    risk_score: float = 0.0
    report: Dict[str, Any] = Field(default_factory=dict)


class SecurityEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    result_id: str
    prompt_injection_score: float
    jailbreak_detected: bool
    pii_exposure: List[str]
    secret_leakage: List[str]
    unsafe_output: bool
    policy_compliance: bool
    risk_score: float
    report: Dict[str, Any]
    created_at: datetime


class ConversationEvaluationCreate(BaseModel):
    project_id: str
    session_id: str
    turns_count: int = 1
    memory_retention_score: float = 0.0
    context_preservation_score: float = 0.0
    coherence_score: float = 0.0
    response_consistency_score: float = 0.0
    user_satisfaction_score: float = 0.0
    avg_turn_length: float = 0.0
    metrics_json: Dict[str, Any] = Field(default_factory=dict)


class ConversationEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    session_id: str
    turns_count: int
    memory_retention_score: float
    context_preservation_score: float
    coherence_score: float
    response_consistency_score: float
    user_satisfaction_score: float
    avg_turn_length: float
    metrics_json: Dict[str, Any]
    created_at: datetime


class AgentEvaluationCreate(BaseModel):
    project_id: str
    agent_name: str
    planning_quality: float = 0.0
    task_completion: float = 0.0
    memory_consistency: float = 0.0
    reasoning_trace_score: float = 0.0
    tool_usage_score: float = 0.0
    conversation_quality: float = 0.0
    agent_collaboration_score: float = 0.0
    agent_score: float = 0.0


class AgentEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    agent_name: str
    planning_quality: float
    task_completion: float
    memory_consistency: float
    reasoning_trace_score: float
    tool_usage_score: float
    conversation_quality: float
    agent_collaboration_score: float
    agent_score: float
    created_at: datetime


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    rules: Dict[str, Any]
    is_active: bool
    created_at: datetime


class RegressionRunCreate(BaseModel):
    project_id: str
    base_run_id: str
    compare_run_id: str
    metrics_comparison: Dict[str, Any] = Field(default_factory=dict)
    regression_detected: bool = False
    report_summary: Optional[str] = None


class RegressionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    base_run_id: str
    compare_run_id: str
    metrics_comparison: Dict[str, Any]
    regression_detected: bool
    report_summary: Optional[str] = None
    created_at: datetime


class PromptVersionCreate(BaseModel):
    name: str
    version: int = 1
    prompt_template: str
    variables: List[str] = Field(default_factory=list)


class PromptVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    version: int
    prompt_template: str
    variables: List[str]
    created_at: datetime


class RiskAssessmentCreate(BaseModel):
    project_id: str
    entity_type: str
    entity_id: str
    security_score: float = 100.0
    safety_score: float = 100.0
    overall_risk_score: float = 0.0
    assessment_report: Dict[str, Any] = Field(default_factory=dict)


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    entity_type: str
    entity_id: str
    security_score: float
    safety_score: float
    overall_risk_score: float
    assessment_report: Dict[str, Any]
    created_at: datetime
