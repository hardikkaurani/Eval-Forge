from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import AgentEvaluationCreate, AgentEvaluationResponse
from app.advanced_ai.services.agent_conversation import AgentConversationService
from app.database.session import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post(
    "", response_model=AgentEvaluationResponse, status_code=status.HTTP_201_CREATED
)
async def create_agent_evaluation(
    payload: AgentEvaluationCreate, db: AsyncSession = Depends(get_db)
):
    service = AgentConversationService(db)
    return await service.evaluate_agent(
        project_id=payload.project_id,
        agent_name=payload.agent_name,
        planning_quality=payload.planning_quality,
        task_completion=payload.task_completion,
        memory_consistency=payload.memory_consistency,
        reasoning_trace_score=payload.reasoning_trace_score,
        tool_usage_score=payload.tool_usage_score,
        conversation_quality=payload.conversation_quality,
        agent_collaboration_score=payload.agent_collaboration_score,
    )


@router.get("", response_model=List[AgentEvaluationResponse])
async def list_agent_evaluations(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvancedAIRepository(db)
    return await repo.get_agent_evaluations(project_id, skip=skip, limit=limit)
