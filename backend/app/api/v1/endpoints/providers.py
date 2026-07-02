from typing import List

from fastapi import APIRouter

from app.evaluation.schemas.evaluation import ProviderInfo
from app.evaluation.services.evaluation import EvaluationCatalogService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/providers")


@router.get("", response_model=ApiResponse[List[ProviderInfo]], summary="List providers")
async def list_providers():
    providers = [ProviderInfo(**item) for item in EvaluationCatalogService.list_providers()]
    return create_response(
        success=True,
        message="Providers retrieved successfully.",
        data=providers,
    )
