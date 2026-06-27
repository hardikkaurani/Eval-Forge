from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.evaluation.registry.registry import judge_registry, provider_registry
from app.evaluation.rubrics.rubrics import BUILT_IN_RUBRICS
from app.evaluation.schemas.evaluation import (
    BatchEvaluationRequest,
    EvaluationCreate,
    EvaluationResponse,
    EvaluationRunResponse,
    JudgeInfo,
    ProviderInfo,
    RubricInfo,
)
from app.evaluation.services.evaluation import EvaluationService
from app.utils.pagination import PaginatedResponse, create_pagination_meta
from app.utils.responses import ApiResponse, create_response

router = APIRouter()


@router.post(
    "",
    response_model=ApiResponse[EvaluationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new evaluation",
)
async def create_evaluation(
    payload: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Creates a new evaluation configuration for a project."""
    evaluation = await EvaluationService.create_evaluation(
        db=db,
        project_id=payload.project_id,
        name=payload.name,
        description=payload.description,
    )
    await db.commit()
    return create_response(
        success=True,
        message="Evaluation created successfully.",
        data=EvaluationResponse.model_validate(evaluation),
    )


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[EvaluationResponse]],
    summary="List evaluations for a project",
)
async def list_evaluations(
    project_id: str = Query(..., description="Project UUID to list evaluations for"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
):
    """Lists evaluations with pagination for a project."""
    items, total = await EvaluationService.list_evaluations(
        db=db, project_id=project_id, page=page, page_size=page_size
    )

    meta = create_pagination_meta(page=page, page_size=page_size, total_items=total)

    paginated_data = PaginatedResponse(
        items=[EvaluationResponse.model_validate(item) for item in items],
        meta=meta,
    )

    return create_response(
        success=True,
        message="Evaluations listed successfully.",
        data=paginated_data,
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[EvaluationResponse],
    summary="Retrieve evaluation by ID",
)
async def get_evaluation(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves detailed evaluation by its UUID."""
    evaluation = await EvaluationService.get_evaluation(db, id)
    return create_response(
        success=True,
        message="Evaluation retrieved successfully.",
        data=EvaluationResponse.model_validate(evaluation),
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[None],
    summary="Delete evaluation by ID",
)
async def delete_evaluation(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """Soft deletes an evaluation."""
    await EvaluationService.delete_evaluation(db, id)
    await db.commit()
    return create_response(
        success=True,
        message="Evaluation deleted successfully.",
    )


@router.post(
    "/batch",
    response_model=ApiResponse[EvaluationRunResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Run a batch evaluation",
)
async def run_batch_evaluation(
    payload: BatchEvaluationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Orchestrates and executes a batch run of LLM-as-a-Judge evaluations."""
    run = await EvaluationService.run_batch_evaluation(db, payload)
    return create_response(
        success=True,
        message="Batch evaluation completed.",
        data=EvaluationRunResponse.model_validate(run),
    )


@router.get(
    "/metadata/providers",
    response_model=ApiResponse[List[ProviderInfo]],
    summary="List registered providers",
)
async def list_providers():
    """Lists keys and display names of all registered providers in the system."""
    keys = provider_registry.list_keys()
    providers = [ProviderInfo(key=k, name=k.capitalize()) for k in keys]
    return create_response(
        success=True,
        message="Providers retrieved successfully.",
        data=providers,
    )


@router.get(
    "/metadata/judges",
    response_model=ApiResponse[List[JudgeInfo]],
    summary="List registered judges",
)
async def list_judges():
    """Lists keys and display names of all registered evaluation judges in the system."""
    keys = judge_registry.list_keys()
    judges = [JudgeInfo(key=k, name=f"{k.capitalize()} Judge") for k in keys]
    return create_response(
        success=True,
        message="Judges retrieved successfully.",
        data=judges,
    )


@router.get(
    "/metadata/rubrics",
    response_model=ApiResponse[List[RubricInfo]],
    summary="List built-in rubrics",
)
async def list_rubrics():
    """Lists all built-in criteria dimensions/rubrics."""
    rubrics = [
        RubricInfo(
            key=k, name=v.name, description=v.description, scoring_scale=v.scoring_scale
        )
        for k, v in BUILT_IN_RUBRICS.items()
    ]
    return create_response(
        success=True,
        message="Rubrics retrieved successfully.",
        data=rubrics,
    )
