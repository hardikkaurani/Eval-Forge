import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.enterprise.schemas import AuditLogResponse
from app.enterprise.services.audit_service import AuditService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/audit", tags=["Enterprise SaaS - Audit Logs"])
audit_service = AuditService()


@router.get("", response_model=ApiResponse[List[AuditLogResponse]])
async def query_audit_logs(
    org_id: uuid.UUID,
    action: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Queries audit log records for tenant-aware compliance and security tracking."""
    logs = await audit_service.search_logs(db, org_id, action, limit)
    return create_response(
        success=True,
        message="Audit logs retrieved successfully.",
        data=[AuditLogResponse.from_orm(log) for log in logs],
    )
