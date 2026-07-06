import hashlib
from uuid import uuid4, UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.session import get_db
from app.platform.models import DeveloperProfile
from app.platform.schemas import DeveloperProfileCreate, DeveloperProfileResponse
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/public", tags=["Developer Platform - Public credentials"])


@router.post("/keys", response_model=ApiResponse[DeveloperProfileResponse], status_code=201)
async def generate_api_key(
    payload: DeveloperProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Generates a secure API key credentials profile for a user."""
    raw_key = f"ef_{uuid4().hex}{uuid4().hex}"
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    profile = DeveloperProfile(
        id=uuid4(),
        user_id=payload.user_id,
        api_key_hash=key_hash,
        scope=payload.scope,
        quota_limit=payload.quota_limit,
        request_count=0
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    # Temporarily return raw key in message so the user can copy it once
    res_data = DeveloperProfileResponse.model_validate(profile)
    return create_response(
        True,
        f"API credentials generated successfully. Copy your API Key: {raw_key}",
        res_data
    )


@router.get("/keys", response_model=ApiResponse[List[DeveloperProfileResponse]])
async def list_user_api_keys(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DeveloperProfile).where(DeveloperProfile.user_id == user_id)
    )
    profiles = result.scalars().all()
    return create_response(True, "API credentials retrieved.", list(profiles))
