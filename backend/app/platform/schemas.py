from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


# 1. Developer Profiles
class DeveloperProfileBase(BaseModel):
    scope: str = "read:all"
    quota_limit: int = 5000


class DeveloperProfileCreate(DeveloperProfileBase):
    user_id: UUID


class DeveloperProfileResponse(DeveloperProfileBase):
    id: UUID
    user_id: UUID
    api_key_hash: str
    request_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 2. Webhooks
class WebhookSubscriptionBase(BaseModel):
    target_url: str
    events: List[str] = Field(default_factory=lambda: ["eval_completed"])
    is_active: bool = True


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    project_id: UUID
    secret_token: Optional[str] = None


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    id: UUID
    project_id: UUID
    secret_token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    event_type: str
    status_code: Optional[int]
    request_payload: Dict[str, Any]
    response_body: Optional[str]
    latency_ms: int
    success: bool
    delivered_at: datetime

    class Config:
        from_attributes = True


# 3. Plugins
class PluginDescriptorBase(BaseModel):
    name: str
    identifier: str
    version: str
    plugin_type: str
    configuration_schema: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class PluginDescriptorCreate(PluginDescriptorBase):
    pass


class PluginDescriptorResponse(PluginDescriptorBase):
    id: UUID
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 4. Model Context Protocol (MCP)
class MCPToolParameter(BaseModel):
    type: str
    description: str
    required: bool = False


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


class MCPCallResponse(BaseModel):
    content: List[Dict[str, Any]]
    is_error: bool = False
