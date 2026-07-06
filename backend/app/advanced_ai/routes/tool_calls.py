from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.advanced_ai.services.agent_conversation import AgentConversationService

router = APIRouter(prefix="/tool-calls", tags=["tool-calls"])


@router.post("/evaluate", status_code=status.HTTP_200_OK)
def evaluate_tool_calls(
    tool_selections: List[Dict[str, Any]],
    executions: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db)
):
    service = AgentConversationService(db)
    return service.evaluate_tool_calls(tool_selections, executions)
