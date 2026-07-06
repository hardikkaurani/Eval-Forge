from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import RegressionRunCreate, RegressionRunResponse
from app.advanced_ai.services.policy_regression import PolicyRegressionService
from app.database.session import get_db

router = APIRouter(prefix="/regressions", tags=["regressions"])


@router.post(
    "", response_model=RegressionRunResponse, status_code=status.HTTP_201_CREATED
)
async def create_regression_run(
    payload: RegressionRunCreate, db: AsyncSession = Depends(get_db)
):
    service = PolicyRegressionService(db)
    return await service.trigger_regression_check(
        project_id=payload.project_id,
        base_run_id=payload.base_run_id,
        compare_run_id=payload.compare_run_id,
    )


@router.get("", response_model=List[RegressionRunResponse])
async def list_regression_runs(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvancedAIRepository(db)
    return await repo.get_regression_runs(project_id, skip=skip, limit=limit)
