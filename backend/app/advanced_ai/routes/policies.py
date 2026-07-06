from typing import List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import PolicyCreate, PolicyResponse, PolicyUpdate
from app.advanced_ai.services.policy_regression import PolicyRegressionService
from app.database.session import get_db

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    project_id: str, payload: PolicyCreate, db: AsyncSession = Depends(get_db)
):
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
):
    repo = AdvancedAIRepository(db)
    return await repo.get_policies(project_id, skip=skip, limit=limit)


@router.patch("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str = Path(..., min_length=36, max_length=36),
    payload: PolicyUpdate = None,
    db: AsyncSession = Depends(get_db),
):
    repo = AdvancedAIRepository(db)
    update_data = payload.model_dump(exclude_unset=True)
    return await repo.update_policy(policy_id, update_data)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: str = Path(..., min_length=36, max_length=36),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvancedAIRepository(db)
    await repo.delete_policy(policy_id)
