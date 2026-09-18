from typing import Any

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_api_key
from app.utils.responses import create_response

router = APIRouter()


@router.get("/connection", summary="Inspect the authenticated API key scope")
async def connection_info(current_key: Any = Depends(get_current_api_key)):
    """Return connection metadata without exposing credentials or key hashes."""
    return create_response(
        True,
        "Connection verified.",
        {
            "name": current_key.name,
            "workspace_id": (
                str(current_key.workspace_id) if current_key.workspace_id else None
            ),
            "organization_id": (
                str(current_key.organization_id)
                if current_key.organization_id
                else None
            ),
            "scopes": current_key.scopes,
        },
    )
