import hashlib
from typing import Any, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.dependencies import get_current_api_key, get_db
from app.platform.models import DeveloperProfile
from app.platform.schemas import DeveloperProfileCreate, DeveloperProfileResponse
from app.utils.responses import ApiResponse, create_response

router = APIRouter(
    prefix="/platform", tags=["Developer Platform - Public Specification & Keys"]
)


@router.get("/spec")
async def get_openapi_specification(request: Request):
    """Returns the live OpenAPI 3.1 specification generated directly from FastAPI."""
    return request.app.openapi()


@router.get("/routes", response_model=ApiResponse[List[dict]])
async def list_public_routes(request: Request):
    """Lists all registered routes in the Eval-Forge API catalog."""
    catalog = []
    openapi_spec = request.app.openapi()
    for path, methods in openapi_spec.get("paths", {}).items():
        catalog.append(
            {
                "path": path,
                "methods": [m.upper() for m in methods.keys()],
                "summary": (
                    methods.get("get", {}).get("summary")
                    or methods.get("post", {}).get("summary", "")
                ),
            }
        )
    return create_response(True, "Route catalog retrieved.", catalog)


@router.post(
    "/keys", response_model=ApiResponse[DeveloperProfileResponse], status_code=201
)
async def generate_api_key(
    payload: DeveloperProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Generates a secure API key credentials profile for a user."""
    raw_key = f"ef_live_{uuid4().hex}{uuid4().hex[:16]}"
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    profile = DeveloperProfile(
        id=uuid4(),
        user_id=payload.user_id,
        api_key_hash=key_hash,
        scope=payload.scope,
        quota_limit=payload.quota_limit,
        request_count=0,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    res_data = DeveloperProfileResponse.model_validate(profile)
    return create_response(
        True,
        f"API credentials generated successfully. Copy your API Key: {raw_key}",
        res_data,
    )


@router.get("/keys", response_model=ApiResponse[List[DeveloperProfileResponse]])
async def list_user_api_keys(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    result = await db.execute(
        select(DeveloperProfile).where(DeveloperProfile.user_id == user_id)
    )
    profiles = result.scalars().all()
    return create_response(True, "API credentials retrieved.", list(profiles))
