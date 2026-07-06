from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AnalyticsOverview(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total_evaluations: int
    success_rate: float
    avg_score: float
    median_score: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_tokens: int
    estimated_cost: float
    daily_eval_volume: List[Dict[str, Any]]
    score_distribution: List[Dict[str, Any]]


class MetricItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    name: str
    value: float
    dimensions: Dict[str, Any]
    timestamp: datetime


class TrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    metric_name: str
    granularity: str
    start_date: datetime
    end_date: datetime
    value: float
    change_from_previous: float
    dimensions: Dict[str, Any]


class TrendResponse(BaseModel):
    metric_name: str
    trends: List[TrendItem]
    comparison: Optional[Dict[str, Any]] = None


class LeaderboardItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    entity_type: str
    entity_name: str
    score: float
    rank: int
    evaluations_count: int
    avg_latency_ms: float
    estimated_cost: float
    snapshot_date: datetime


class LeaderboardResponse(BaseModel):
    entity_type: str
    items: List[LeaderboardItem]


class ReportCreate(BaseModel):
    name: str
    type: str = Field(..., description="PDF or CSV")
    filters: Dict[str, Any] = Field(default_factory=dict)


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    name: str
    type: str
    status: str
    file_path: Optional[str] = None
    filters: Dict[str, Any]
    summary: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime


class InsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    type: str
    severity: str
    message: str
    metadata_json: Dict[str, Any]
    created_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    type: str
    message: str
    status: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    triggered_at: datetime
    resolved_at: Optional[datetime] = None


class SystemMetrics(BaseModel):
    cpu_usage_percent: float
    memory_usage_bytes: int
    memory_usage_percent: float
    disk_usage_percent: float
    active_redis_connections: int
    redis_health: str
    postgres_health: str
    queue_backlog: int
    active_worker_count: int
    api_request_count_1h: int
    provider_status: Dict[str, str]


class DashboardSnapshotCreate(BaseModel):
    name: str
    layout: Dict[str, Any]


class DashboardSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    name: str
    layout: Dict[str, Any]
    created_at: datetime
