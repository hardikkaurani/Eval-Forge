import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.enterprise.schemas import WorkspaceCreate, WorkspaceResponse
from app.enterprise.services.quota_service import QuotaService
from app.enterprise.services.workspace_service import WorkspaceService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/workspaces", tags=["Enterprise SaaS - Workspaces"])
workspace_service = WorkspaceService()
quota_service = QuotaService()


@router.post(
    "",
    response_model=ApiResponse[WorkspaceResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    payload: WorkspaceCreate, db: AsyncSession = Depends(get_db)
):
    """Creates a new isolated workspace (e.g. staging, prod) inside an organization."""
    try:
        org_id = (
            uuid.UUID(payload.organization_id)
            if isinstance(payload.organization_id, str)
            else payload.organization_id
        )
        ws = await workspace_service.create_workspace(
            db, org_id, payload.name, payload.description
        )
        return create_response(
            success=True,
            message="Workspace successfully created.",
            data=WorkspaceResponse.from_orm(ws),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=ApiResponse[List[WorkspaceResponse]])
async def list_workspaces(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Lists all active workspaces registered under an organization."""
    workspaces = await workspace_service.list_workspaces(db, org_id)
    return create_response(
        success=True,
        message="Workspaces list retrieved.",
        data=[WorkspaceResponse.from_orm(w) for w in workspaces],
    )


@router.get("/{workspace_id}/quotas/{metric}", response_model=ApiResponse[dict])
async def get_workspace_quota(
    workspace_id: uuid.UUID,
    org_id: uuid.UUID,
    metric: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves current workspace-level quota utilization limits and thresholds."""
    status_data = await quota_service.check_quota_status(
        db, org_id, workspace_id, metric
    )
    return create_response(
        success=True, message="Workspace quota check completed.", data=status_data
    )
