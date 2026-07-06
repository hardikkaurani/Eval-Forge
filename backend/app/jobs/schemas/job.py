from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the background job")
    queue_name: str = Field("default", max_length=100, description="Target queue name")
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="Job parameters and inputs"
    )
    max_retries: int = Field(
        3, ge=0, le=10, description="Max retry attempts on failure"
    )
    scheduled_at: Optional[datetime] = Field(
        None, description="Delayed execution timestamp"
    )
    recurring_cron: Optional[str] = Field(
        None, max_length=255, description="Cron format for recurring executions"
    )
    timezone: str = Field(
        "UTC", max_length=100, description="Timezone context for cron schedules"
    )


class JobCancel(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for cancelling the job")


class JobLogResponse(BaseModel):
    id: str
    job_id: str
    log_level: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionHistoryResponse(BaseModel):
    id: str
    job_id: str
    worker_id: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class RetryHistoryResponse(BaseModel):
    id: str
    job_id: str
    retry_attempt: int
    error_message: Optional[str] = None
    attempted_at: datetime
    next_attempt_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CancellationResponse(BaseModel):
    id: str
    job_id: str
    reason: Optional[str] = None
    cancelled_by: str
    cancelled_at: datetime

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: str
    name: str
    status: str
    queue_name: str
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    worker_id: Optional[str] = None
    progress: float
    current_step: Optional[str] = None
    max_retries: int
    retry_count: int
    error_message: Optional[str] = None
    created_at: datetime
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    recurring_cron: Optional[str] = None
    timezone: str

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    logs: List[JobLogResponse] = []
    execution_history: List[ExecutionHistoryResponse] = []
    retry_history: List[RetryHistoryResponse] = []
    cancellation: Optional[CancellationResponse] = None

    class Config:
        from_attributes = True


class WorkerResponse(BaseModel):
    id: str
    name: str
    status: str
    queue_name: str
    current_job_id: Optional[str] = None
    last_heartbeat: datetime
    system_load: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class QueueResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QueueMetricsResponse(BaseModel):
    queue_name: str
    active_jobs: int
    queued_jobs: int
    completed_jobs: int
    failed_jobs: int
    latency_seconds: float


class SystemMetricsResponse(BaseModel):
    queue_size: int
    worker_count: int
    running_jobs: int
    failed_jobs: int
    average_execution_time: float
    retry_rate: float
    success_rate: float
    queue_latency: float
    worker_utilization: float
    error_frequency: Dict[str, int]
    provider_latency: Dict[str, float]
