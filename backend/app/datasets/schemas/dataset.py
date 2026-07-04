from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DatasetRecordBase(BaseModel):
    prompt: str = Field(..., description="Prompt or query for the model.")
    input: Optional[str] = Field(
        None, description="Optional system prompt or input prefix."
    )
    context: Optional[str] = Field(
        None, description="Optional retrieval context or grounding information."
    )
    reference_output: Optional[str] = Field(
        None, description="Optional expected golden output."
    )
    candidate_output: Optional[str] = Field(
        None, description="Optional model output to evaluate."
    )
    ground_truth: Optional[str] = Field(
        None, description="Optional absolute ground truth for testing."
    )
    expected_score: Optional[float] = Field(
        None, description="Optional target evaluation score."
    )
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class DatasetRecordCreate(DatasetRecordBase):
    pass


class DatasetRecordResponse(DatasetRecordBase):
    id: str
    version_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetVersionBase(BaseModel):
    version: str = Field(..., description="Version label, e.g. v1, v2.")
    schema_version: str = Field(
        "1.0", description="Version of the dataset schema format."
    )
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class DatasetVersionCreate(DatasetVersionBase):
    records: List[DatasetRecordCreate] = Field(default_factory=list)


class DatasetVersionResponse(DatasetVersionBase):
    id: str
    dataset_id: str
    record_count: int
    hash: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetBase(BaseModel):
    name: str = Field(..., description="Descriptive dataset name.")
    description: Optional[str] = Field(
        None, description="Detailed dataset explanation."
    )
    visibility: str = Field(
        "private", description="Dataset visibility (public/private)."
    )
    source: Optional[str] = Field(
        None, description="Data source or provenance details."
    )
    language: Optional[str] = Field("en", description="Primary dataset language.")
    license: Optional[str] = Field(None, description="Dataset usage license.")
    tags: List[str] = Field(default_factory=list)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class DatasetCreate(DatasetBase):
    owner: Optional[str] = Field(None, description="Owner username or ID.")
    initial_version: Optional[str] = Field("v1", description="Initial version label.")


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    source: Optional[str] = None
    language: Optional[str] = None
    license: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class DatasetResponse(DatasetBase):
    id: str
    project_id: str
    owner: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetDetailResponse(DatasetResponse):
    versions: List[DatasetVersionResponse] = Field(default_factory=list)


class DatasetDiffItem(BaseModel):
    record_id: str
    change_type: str  # 'added', 'removed', 'modified'
    prompt_diff: Optional[str] = None
    field_diffs: Optional[Dict[str, Dict[str, Any]]] = (
        None  # fieldname -> {'old': v, 'new': v}
    )


class DatasetListResponse(BaseModel):
    datasets: List[DatasetResponse]
    total: int
    skip: int
    limit: int


class DatasetRecordsPaginated(BaseModel):
    records: List[DatasetRecordResponse]
    total: int
    skip: int
    limit: int
