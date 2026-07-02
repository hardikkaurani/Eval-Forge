from typing import List

from fastapi import APIRouter

from app.evaluation.schemas.evaluation import RubricInfo
from app.evaluation.services.evaluation import EvaluationCatalogService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/rubrics")


@router.get("", response_model=ApiResponse[List[RubricInfo]], summary="List rubrics")
async def list_rubrics():
    rubrics = [RubricInfo(**item) for item in EvaluationCatalogService.list_rubrics()]
    return create_response(
        success=True,
        message="Rubrics retrieved successfully.",
        data=rubrics,
    )
