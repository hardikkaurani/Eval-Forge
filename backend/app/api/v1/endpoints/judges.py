from typing import List

from fastapi import APIRouter

from app.evaluation.schemas.evaluation import JudgeInfo
from app.evaluation.services.evaluation import EvaluationCatalogService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/judges")


@router.get("", response_model=ApiResponse[List[JudgeInfo]], summary="List judges")
async def list_judges():
    judges = [JudgeInfo(**item) for item in EvaluationCatalogService.list_judges()]
    return create_response(
        success=True,
        message="Judges retrieved successfully.",
        data=judges,
    )
