from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.utils.constants import PROJECT_STATUSES, PROJECT_STATUS_ACTIVE


class ProjectBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The name of the project",
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Detailed description of the project",
    )
    status: str = Field(
        default=PROJECT_STATUS_ACTIVE,
        description="Project status (active, inactive, archived)",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in PROJECT_STATUSES:
            raise ValueError(
                f"Status must be one of: {', '.join(PROJECT_STATUSES)}"
            )
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="The name of the project",
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Detailed description of the project",
    )
    status: str | None = Field(
        None,
        description="Project status (active, inactive, archived)",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in PROJECT_STATUSES:
            raise ValueError(
                f"Status must be one of: {', '.join(PROJECT_STATUSES)}"
            )
        return v


class ProjectResponse(BaseModel):
    """Schema representing the serialized project response."""

    id: str
    name: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True
