from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.datasets.schemas.dataset import DatasetResponse


class BenchmarkSuiteBase(BaseModel):
    name: str = Field(..., description="Descriptive benchmark suite name.")
    description: Optional[str] = Field(None, description="Detailed explanation of what this suite tests.")
    tags: List[str] = Field(default_factory=list)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class BenchmarkSuiteCreate(BenchmarkSuiteBase):
    dataset_ids: List[str] = Field(default_factory=list, description="IDs of datasets to include in this suite.")


class BenchmarkSuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    dataset_ids: Optional[List[str]] = None


class BenchmarkSuiteResponse(BenchmarkSuiteBase):
    id: str
    project_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BenchmarkSuiteDetailResponse(BenchmarkSuiteResponse):
    datasets: List[DatasetResponse] = Field(default_factory=list)
