from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import SecurityEvaluationCreate, SecurityEvaluationResponse
from app.advanced_ai.services.safety_security import SafetySecurityService
from app.database.session import get_db

router = APIRouter(prefix="/security", tags=["security"])


@router.post(
    "", response_model=SecurityEvaluationResponse, status_code=status.HTTP_201_CREATED
)
async def create_security_evaluation(
    payload: SecurityEvaluationCreate, db: AsyncSession = Depends(get_db)
):
    service = SafetySecurityService(db)
    return await service.evaluate_security(
        project_id=payload.project_id,
        result_id=payload.result_id,
        input_prompt="System instructions bypass text",
        model_output="Credential secrets pattern output",
    )


@router.get("", response_model=List[SecurityEvaluationResponse])
async def list_security_evaluations(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvancedAIRepository(db)
    return await repo.get_security_evaluations(project_id, skip=skip, limit=limit)
