from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.advanced_ai.schemas import SafetyEvaluationCreate, SafetyEvaluationResponse
from app.advanced_ai.services.safety_security import SafetySecurityService
from app.advanced_ai.repositories import AdvancedAIRepository

router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("", response_model=SafetyEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_safety_evaluation(
    payload: SafetyEvaluationCreate,
    db: AsyncSession = Depends(get_db)
):
    service = SafetySecurityService(db)
    return await service.evaluate_safety(
        project_id=payload.project_id,
        result_id=payload.result_id,
        input_prompt="Trigger prompt text",
        model_output="Response text"
    )


@router.get("", response_model=List[SafetyEvaluationResponse])
async def list_safety_evaluations(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    repo = AdvancedAIRepository(db)
    return await repo.get_safety_evaluations(project_id, skip=skip, limit=limit)
