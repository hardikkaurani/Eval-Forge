from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_api_key, get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService
from app.utils.pagination import PaginatedResponse
from app.utils.responses import ApiResponse, create_response

router = APIRouter()


def _extract_workspace_id(api_key_record: Any) -> str | None:
    if api_key_record and getattr(api_key_record, "workspace_id", None):
        return str(api_key_record.workspace_id)
    return None


@router.post(
    "",
    response_model=ApiResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    response_description="The created project details wrapped in the API response structure",
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Creates a new project record scoped to authorized workspace context."""
    workspace_id = _extract_workspace_id(current_key)
    service = ProjectService(db, workspace_id=workspace_id)
    project = await service.create_project(payload)
    return create_response(
        success=True,
        message="Project created successfully.",
        data=ProjectResponse.model_validate(project),
    )


@router.get(
    "/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    summary="Retrieve a project by ID",
    response_description="The project details wrapped in the API response structure",
)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Retrieves a specific project by UUID within authorized workspace boundary."""
    workspace_id = _extract_workspace_id(current_key)
    service = ProjectService(db, workspace_id=workspace_id)
    project = await service.get_project(project_id)
    return create_response(
        success=True,
        message="Project retrieved successfully.",
        data=ProjectResponse.model_validate(project),
    )


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[ProjectResponse]],
    summary="List and filter projects",
    response_description="A paginated list of projects with filtering, searching, and sorting applied",
)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(
        None, description="Search query matching project name or description"
    ),
    status: str | None = Query(
        None, description="Filter projects by status (active, inactive, archived)"
    ),
    sort_by: str = Query("created_at", description="Field to sort projects by"),
    sort_order: str = Query("desc", description="Sort order direction (asc, desc)"),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Lists, filters, searches, and sorts projects within authorized workspace boundary."""
    workspace_id = _extract_workspace_id(current_key)
    service = ProjectService(db, workspace_id=workspace_id)
    items, meta = await service.list_projects(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    paginated_data = PaginatedResponse(
        items=[ProjectResponse.model_validate(item) for item in items],
        meta=meta,
    )

    return create_response(
        success=True,
        message="Projects listed successfully.",
        data=paginated_data,
    )


@router.patch(
    "/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    summary="Update an existing project",
    response_description="The updated project details wrapped in the API response structure",
)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Updates one or more attributes of a project within authorized workspace boundary."""
    workspace_id = _extract_workspace_id(current_key)
    service = ProjectService(db, workspace_id=workspace_id)
    project = await service.update_project(project_id, payload)
    return create_response(
        success=True,
        message="Project updated successfully.",
        data=ProjectResponse.model_validate(project),
    )


@router.delete(
    "/{project_id}",
    response_model=ApiResponse[ProjectResponse],
    summary="Soft delete a project",
    response_description="The soft-deleted project details wrapped in the API response structure",
)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Soft deletes a project by updating its deleted_at timestamp within authorized workspace boundary."""
    workspace_id = _extract_workspace_id(current_key)
    service = ProjectService(db, workspace_id=workspace_id)
    project = await service.delete_project(project_id)
    return create_response(
        success=True,
        message="Project soft-deleted successfully.",
        data=ProjectResponse.model_validate(project),
    )
