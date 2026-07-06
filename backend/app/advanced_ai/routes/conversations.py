from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.schemas import (
    ConversationEvaluationCreate,
    ConversationEvaluationResponse,
)
from app.advanced_ai.services.agent_conversation import AgentConversationService
from app.database.session import get_db

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post(
    "",
    response_model=ConversationEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation_evaluation(
    payload: ConversationEvaluationCreate, db: AsyncSession = Depends(get_db)
):
    service = AgentConversationService(db)
    # Map turns list from payload schema details
    turns = payload.metrics_json.get(
        "turns",
        [
            {"role": "user", "content": "Hello agent"},
            {"role": "assistant", "content": "Hi there, I can guide you today."},
        ],
    )
    return await service.evaluate_conversation(
        project_id=payload.project_id, session_id=payload.session_id, turns=turns
    )


@router.get("", response_model=List[ConversationEvaluationResponse])
async def list_conversation_evaluations(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = AdvancedAIRepository(db)
    return await repo.get_conversation_evaluations(project_id, skip=skip, limit=limit)
