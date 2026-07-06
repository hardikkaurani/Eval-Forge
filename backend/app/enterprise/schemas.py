import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# Plan schemas
class PlanBase(BaseModel):
    name: str
    price_monthly: float
    limits: Dict[str, Any]


class PlanCreate(PlanBase):
    pass


class PlanResponse(PlanBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    custom_domain: Optional[str] = None
    branding_settings: Optional[Dict[str, Any]] = None
    security_policies: Optional[Dict[str, Any]] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workspace schemas
class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceCreate(WorkspaceBase):
    organization_id: str


class WorkspaceResponse(WorkspaceBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Role & Permission schemas
class RoleBase(BaseModel):
    name: str
    permissions: List[str]


class RoleCreate(RoleBase):
    organization_id: Optional[str] = None


class RoleResponse(RoleBase):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


# Membership schemas
class MembershipBase(BaseModel):
    organization_id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    role_id: Optional[uuid.UUID] = None
    is_active: bool = True


class MembershipCreate(MembershipBase):
    pass


class MembershipResponse(MembershipBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Invitation schemas
class InvitationBase(BaseModel):
    email: EmailStr
    role: str = "Developer"


class InvitationCreate(InvitationBase):
    organization_id: str
    invited_by: str


class InvitationResponse(InvitationBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    invited_by: uuid.UUID
    token: str
    status: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


# Subscription schemas
class SubscriptionBase(BaseModel):
    organization_id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime


class SubscriptionResponse(SubscriptionBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Invoice schemas
class InvoiceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    amount: float
    status: str
    pdf_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Usage tracking schemas
class UsageRecordCreate(BaseModel):
    organization_id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    metric: str
    value: float


class UsageRecordResponse(UsageRecordCreate):
    id: uuid.UUID
    timestamp: datetime

    class Config:
        from_attributes = True


# Quota schemas
class QuotaResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: Optional[uuid.UUID]
    metric: str
    limit_value: float
    current_value: float
    reset_at: datetime

    class Config:
        from_attributes = True


# Audit Log schemas
class AuditLogCreate(BaseModel):
    organization_id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    action: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogCreate):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Notification schemas
class EnterpriseNotificationCreate(BaseModel):
    organization_id: uuid.UUID
    recipient_id: uuid.UUID
    channel: str
    title: str
    content: str


class EnterpriseNotificationResponse(EnterpriseNotificationCreate):
    id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# API Key schemas
class EnterpriseAPIKeyCreate(BaseModel):
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    name: str
    scopes: List[str] = ["read:all"]
    expires_in_days: Optional[int] = None


class EnterpriseAPIKeyResponse(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID]
    workspace_id: Optional[uuid.UUID]
    name: str
    scopes: List[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
