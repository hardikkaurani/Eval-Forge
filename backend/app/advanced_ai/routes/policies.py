from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import PolicyCreate, PolicyResponse, PolicyUpdate
from app.advanced_ai.services.policy_regression import PolicyRegressionService
from app.core.dependencies import _extract_workspace_id, get_current_api_key
from app.database.repository import ProjectRepository
from app.database.session import get_db

router = APIRouter(prefix="/policies", tags=["policies"])


async def _verify_project_ws(
    db: AsyncSession, project_id: str, workspace_id: str | None
) -> None:
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id, workspace_id=workspace_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    project_id: str,
    payload: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, project_id, workspace_id)
    service = PolicyRegressionService(db)
    return await service.create_policy(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        rules=payload.rules,
    )


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, project_id, workspace_id)
    repo = AdvancedAIRepository(db)
    return await repo.get_policies(project_id, skip=skip, limit=limit)


@router.patch("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str = Path(..., min_length=36, max_length=36),
    payload: PolicyUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    repo = AdvancedAIRepository(db)
    policy = await repo.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found.")
    await _verify_project_ws(db, policy.project_id, workspace_id)
    update_data = payload.model_dump(exclude_unset=True) if payload else {}
    res = await repo.update_policy(policy_id, update_data)
    await db.commit()
    return res


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: str = Path(..., min_length=36, max_length=36),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    repo = AdvancedAIRepository(db)
    policy = await repo.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found.")
    await _verify_project_ws(db, policy.project_id, workspace_id)
    await repo.delete_policy(policy_id)
    await db.commit()
