from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_api_key
from app.database.session import get_db
from app.evaluation.rubrics.rubrics import (
    BUILT_IN_RUBRICS,
    MAX_CUSTOM_RUBRICS_PER_PROJECT,
    MAX_DESCRIPTION_LENGTH,
    MAX_KEY_LENGTH,
    MAX_NAME_LENGTH,
    MAX_TEMPLATE_LENGTH,
    Rubric,
    validate_custom_rubric,
)
from app.evaluation.schemas.evaluation import RubricInfo
from app.evaluation.services.evaluation import EvaluationCatalogService
from app.models.evaluation import CustomRubric
from app.utils.responses import ApiResponse, create_response
from app.utils.time import get_utc_now
from app.utils.uuid import generate_uuid

router = APIRouter(prefix="/rubrics")


def _extract_workspace_id(key: Any) -> str | None:
    if hasattr(key, "workspace_id") and key.workspace_id:
        return str(key.workspace_id)
    return None


class CustomRubricCreate(BaseModel):
    project_id: Optional[str] = Field(
        default=None, description="Optional Project ID for project-scoped custom rubric"
    )
    key: str = Field(..., min_length=2, max_length=MAX_KEY_LENGTH)
    name: str = Field(..., min_length=2, max_length=MAX_NAME_LENGTH)
    description: str = Field(..., min_length=5, max_length=MAX_DESCRIPTION_LENGTH)
    weight: float = Field(default=1.0, ge=0.0)
    scoring_scale: int = Field(default=5, ge=1, le=10)
    prompt_template: Optional[str] = Field(default=None, max_length=MAX_TEMPLATE_LENGTH)


@router.get("", response_model=ApiResponse[List[RubricInfo]], summary="List rubrics")
async def list_rubrics(
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    if project_id:
        from app.database.repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id, workspace_id=workspace_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{project_id}' not found.",
            )

    # 1. Built-in rubrics catalog
    items = [RubricInfo(**item) for item in EvaluationCatalogService.list_rubrics()]

    # 2. Fetch DB custom rubrics
    stmt = select(CustomRubric)
    if project_id:
        stmt = stmt.where(CustomRubric.project_id == project_id)
    res = await db.execute(stmt)
    db_customs = res.scalars().all()

    existing_keys = {item.key for item in items}
    for cr in db_customs:
        if cr.rubric_key not in existing_keys:
            items.append(
                RubricInfo(
                    key=cr.rubric_key,
                    name=cr.name,
                    description=cr.description,
                    scoring_scale=cr.scoring_scale,
                )
            )

    return create_response(
        success=True,
        message="Rubrics retrieved successfully.",
        data=items,
    )


@router.post(
    "/custom",
    response_model=ApiResponse[RubricInfo],
    status_code=status.HTTP_201_CREATED,
    summary="Register custom Jinja2 metric rubric",
)
async def create_custom_rubric(
    payload: CustomRubricCreate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    if payload.project_id:
        from app.database.repository import ProjectRepository

        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(
            payload.project_id, workspace_id=workspace_id
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{payload.project_id}' not found.",
            )

    rubric_key = payload.key.lower().strip()

    try:
        rubric_obj = Rubric(
            name=payload.name,
            description=payload.description,
            weight=payload.weight,
            scoring_scale=payload.scoring_scale,
            prompt_template=payload.prompt_template,
        )
        validate_custom_rubric(rubric_obj, key=rubric_key)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err

    # Check max rubrics per project bound (P8-08)
    if payload.project_id:
        count_stmt = (
            select(func.count())
            .select_from(CustomRubric)
            .where(CustomRubric.project_id == payload.project_id)
        )
        count_res = await db.execute(count_stmt)
        total_custom = count_res.scalar_one()

        existing_stmt = select(CustomRubric).where(
            CustomRubric.project_id == payload.project_id,
            CustomRubric.rubric_key == rubric_key,
        )
        existing_res = await db.execute(existing_stmt)
        existing_rec = existing_res.scalar_one_or_none()

        if not existing_rec and total_custom >= MAX_CUSTOM_RUBRICS_PER_PROJECT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum custom rubrics limit ({MAX_CUSTOM_RUBRICS_PER_PROJECT}) reached for project.",
            )
    else:
        existing_stmt = select(CustomRubric).where(
            CustomRubric.project_id.is_(None),
            CustomRubric.rubric_key == rubric_key,
        )
        existing_res = await db.execute(existing_stmt)
        existing_rec = existing_res.scalar_one_or_none()

    if existing_rec:
        existing_rec.name = payload.name
        existing_rec.description = payload.description
        existing_rec.weight = payload.weight
        existing_rec.scoring_scale = payload.scoring_scale
        existing_rec.prompt_template = payload.prompt_template
        existing_rec.updated_at = get_utc_now()
    else:
        existing_rec = CustomRubric(
            id=generate_uuid(),
            project_id=payload.project_id,
            rubric_key=rubric_key,
            name=payload.name,
            description=payload.description,
            weight=payload.weight,
            scoring_scale=payload.scoring_scale,
            prompt_template=payload.prompt_template,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(existing_rec)

    await db.commit()
    await db.refresh(existing_rec)

    # Also sync non-authoritative fast cache
    from app.evaluation.rubrics.rubrics import register_custom_rubric

    register_custom_rubric(rubric_key, rubric_obj)

    data = RubricInfo(
        key=rubric_key,
        name=existing_rec.name,
        description=existing_rec.description,
        scoring_scale=existing_rec.scoring_scale,
    )
    return create_response(
        success=True,
        message=f"Custom metric rubric '{rubric_key}' registered successfully.",
        data=data,
    )
