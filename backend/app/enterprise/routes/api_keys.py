import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.enterprise.schemas import EnterpriseAPIKeyCreate, EnterpriseAPIKeyResponse
from app.enterprise.services.apikey_service import EnterpriseAPIKeyService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/api-keys", tags=["Enterprise SaaS - API Keys"])
key_service = EnterpriseAPIKeyService()


@router.post("", response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED)
async def generate_api_key(
    payload: EnterpriseAPIKeyCreate, db: AsyncSession = Depends(get_db)
):
    """Generates a secure API key scoped to a specific Organization or Workspace."""
    org_id = uuid.UUID(payload.organization_id) if payload.organization_id else None
    workspace_id = uuid.UUID(payload.workspace_id) if payload.workspace_id else None

    raw_key, key_record = await key_service.generate_key(
        db,
        name=payload.name,
        org_id=org_id,
        workspace_id=workspace_id,
        scopes=payload.scopes,
        expires_in_days=payload.expires_in_days or 30,
    )

    data = {
        "api_key": raw_key,
        "details": EnterpriseAPIKeyResponse.from_orm(key_record),
    }

    return create_response(
        success=True,
        message="API Key generated successfully. Make sure to copy it now; it won't be shown again.",
        data=data,
    )


@router.delete("/{key_id}", response_model=ApiResponse[bool])
async def revoke_api_key(key_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Revokes an API key instantly to deny further API access."""
    success = await key_service.revoke_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found")
    return create_response(
        success=True, message="API Key successfully revoked.", data=True
    )
