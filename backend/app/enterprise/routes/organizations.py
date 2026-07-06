import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.enterprise.models import Invitation
from app.enterprise.schemas import (
    InvitationBase,
    InvitationResponse,
    OrganizationCreate,
    OrganizationResponse,
)
from app.enterprise.services.organization_service import OrganizationService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/organizations", tags=["Enterprise SaaS - Organizations"])
org_service = OrganizationService()


@router.post(
    "",
    response_model=ApiResponse[OrganizationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_org(
    payload: OrganizationCreate,
    user_id: str,  # In production, this would be injected from authenticated user session
    db: AsyncSession = Depends(get_db),
):
    """Creates a new enterprise organization and assigns the creator as owner."""
    org = await org_service.create_organization(
        db,
        name=payload.name,
        user_id=user_id,
        custom_domain=payload.custom_domain,
        logo_url=payload.logo_url,
        branding_settings=payload.branding_settings,
        security_policies=payload.security_policies,
    )
    return create_response(
        success=True,
        message="Organization successfully created.",
        data=OrganizationResponse.from_orm(org),
    )


@router.get("/{org_id}", response_model=ApiResponse[OrganizationResponse])
async def get_org(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieves metadata for a specific organization."""
    org = await org_service.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return create_response(
        success=True,
        message="Organization retrieved successfully.",
        data=OrganizationResponse.from_orm(org),
    )


@router.post("/{org_id}/branding", response_model=ApiResponse[OrganizationResponse])
async def update_branding(
    org_id: uuid.UUID, branding: dict, db: AsyncSession = Depends(get_db)
):
    """Updates the custom branding, logo, and theme settings of an organization."""
    try:
        org = await org_service.update_branding(db, org_id, branding)
        return create_response(
            success=True,
            message="Branding updated successfully.",
            data=OrganizationResponse.from_orm(org),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{org_id}/domain", response_model=ApiResponse[OrganizationResponse])
async def configure_domain(
    org_id: uuid.UUID, domain: str, db: AsyncSession = Depends(get_db)
):
    """Configures a verified custom domain for white-label organization login."""
    try:
        org = await org_service.configure_custom_domain(db, org_id, domain)
        return create_response(
            success=True,
            message="Custom domain configured successfully.",
            data=OrganizationResponse.from_orm(org),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/{org_id}/invitations",
    response_model=ApiResponse[InvitationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    org_id: uuid.UUID,
    payload: InvitationBase,
    invited_by: str,
    db: AsyncSession = Depends(get_db),
):
    """Invites a new member to join the organization with a specific role."""
    from datetime import datetime, timedelta

    token = f"inv_{uuid.uuid4().hex}"
    invite = Invitation(
        id=uuid.uuid4(),
        organization_id=org_id,
        email=payload.email,
        role=payload.role,
        invited_by=uuid.UUID(invited_by),
        token=token,
        status="pending",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)

    return create_response(
        success=True,
        message="Invitation sent successfully.",
        data=InvitationResponse.from_orm(invite),
    )
