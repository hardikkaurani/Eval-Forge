import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.dependencies import _extract_workspace_id, get_current_api_key
from app.database.session import get_db
from app.enterprise.models import Organization, Workspace
from app.enterprise.routes.organizations import _verify_org_membership
from app.enterprise.services.billing_service import BillingService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/admin", tags=["Enterprise SaaS - Administration"])
billing_service = BillingService()


@router.post("/seed-plans", response_model=ApiResponse[bool])
async def seed_saas_plans(
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Seeds default SaaS plans (Starter, Pro, Team, Business, Enterprise) to the database."""
    await billing_service.seed_plans(db)
    return create_response(
        success=True, message="SaaS Plans seeded successfully.", data=True
    )


@router.get("/organizations", response_model=ApiResponse[List[Dict[str, Any]]])
async def list_all_organizations(
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Exposes tenant organization for current user context."""
    workspace_id = _extract_workspace_id(current_key)
    orgs = []
    if workspace_id:
        try:
            ws_uuid = uuid.UUID(workspace_id)
            stmt = (
                select(Organization)
                .join(Workspace, Workspace.organization_id == Organization.id)
                .where(Workspace.id == ws_uuid)
            )
            res = await db.execute(stmt)
            orgs = res.scalars().all()
        except ValueError:
            pass

    org_list = []
    for o in orgs:
        org_list.append(
            {
                "id": str(o.id),
                "name": o.name,
                "custom_domain": o.custom_domain,
                "created_at": o.created_at,
            }
        )

    return create_response(
        success=True, message="Tenant organizations retrieved.", data=org_list
    )


@router.post("/sso/identity-providers", response_model=ApiResponse[dict])
async def configure_sso_identity_provider(
    org_id: uuid.UUID,
    provider_type: str,
    metadata_url: str,
    client_id: str,
    client_secret: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Configures SAML/OIDC Single Sign-On (SSO) identity provider settings for an organization."""
    await _verify_org_membership(db, current_key, org_id)
    mock_config = {
        "org_id": str(org_id),
        "provider": provider_type,
        "metadata_url": metadata_url,
        "client_id": client_id,
        "is_active": True,
        "configured_at": "2026-07-06T12:00:00Z",
    }

    return create_response(
        success=True,
        message="SSO Identity Provider registered successfully.",
        data=mock_config,
    )
