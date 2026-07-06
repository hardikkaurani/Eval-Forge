import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.models import Organization, Workspace, Membership, Invitation
from app.enterprise.exceptions import TenantAccessViolationException


class OrganizationService:
    """Manages multi-tenant organizations, onboarding, custom domains, branding, and team members."""

    async def create_organization(
        self,
        db: AsyncSession,
        name: str,
        user_id: str,
        custom_domain: str = None,
        logo_url: str = None,
        branding_settings: dict = None,
        security_policies: dict = None
    ) -> Organization:
        org = Organization(
            id=uuid.uuid4(),
            name=name,
            custom_domain=custom_domain,
            logo_url=logo_url,
            branding_settings=branding_settings,
            security_policies=security_policies,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(org)
        await db.flush()

        # Add the creator as the Owner of the organization
        membership = Membership(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(membership)
        await db.commit()
        await db.refresh(org)
        return org

    async def get_organization(self, db: AsyncSession, org_id: uuid.UUID) -> Organization:
        stmt = select(Organization).where(Organization.id == org_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_branding(self, db: AsyncSession, org_id: uuid.UUID, branding: dict) -> Organization:
        org = await self.get_organization(db, org_id)
        if not org:
            raise TenantAccessViolationException("Organization not found")
        org.branding_settings = branding
        org.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(org)
        return org

    async def configure_custom_domain(self, db: AsyncSession, org_id: uuid.UUID, domain: str) -> Organization:
        org = await self.get_organization(db, org_id)
        if not org:
            raise TenantAccessViolationException("Organization not found")
        org.custom_domain = domain
        org.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(org)
        return org
