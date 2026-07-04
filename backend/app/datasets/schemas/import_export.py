from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ImportJobResponse(BaseModel):
    id: str
    project_id: str
    dataset_id: Optional[str] = None
    status: str
    file_format: str
    file_path: Optional[str] = None
    progress: float
    total_records: int
    processed_records: int
    error_message: Optional[str] = None
    validation_report: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExportJobResponse(BaseModel):
    id: str
    project_id: str
    dataset_id: Optional[str] = None
    status: str
    file_format: str
    file_path: Optional[str] = None
    progress: float
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
