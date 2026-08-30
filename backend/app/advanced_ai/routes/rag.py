from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import (
    HallucinationReportResponse,
    RAGEvaluationCreate,
    RAGEvaluationResponse,
)
from app.advanced_ai.services.rag import RAGService
from app.core.dependencies import _extract_workspace_id, get_current_api_key
from app.database.repository import ProjectRepository
from app.database.session import get_db

router = APIRouter(prefix="/rag", tags=["rag"])


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


@router.post(
    "", response_model=RAGEvaluationResponse, status_code=status.HTTP_201_CREATED
)
async def create_rag_evaluation(
    payload: RAGEvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, payload.project_id, workspace_id)
    service = RAGService(db)
    return await service.evaluate_rag_run(
        project_id=payload.project_id,
        run_id=payload.run_id,
        contexts=["Context 1 details", "Context 2 details"],
        question="Query sentence",
        answer="Model answer text",
        ground_truth="Ground truth sentence",
    )


@router.get("", response_model=List[RAGEvaluationResponse])
async def list_rag_evaluations(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, project_id, workspace_id)
    repo = AdvancedAIRepository(db)
    return await repo.get_rag_evaluations(project_id, skip=skip, limit=limit)


@router.post(
    "/hallucinations",
    response_model=HallucinationReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_hallucination_report(
    result_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, project_id, workspace_id)
    service = RAGService(db)
    return await service.generate_hallucination_report(
        project_id=project_id,
        result_id=result_id,
        contexts=["Context document reference"],
        answer="Generated response details",
    )
