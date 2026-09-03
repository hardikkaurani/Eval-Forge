from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# 1. Developer Profiles & API Keys
class DeveloperProfileBase(BaseModel):
    scope: str = "read:all"
    quota_limit: int = 5000


class DeveloperProfileCreate(DeveloperProfileBase):
    user_id: UUID


class DeveloperProfileResponse(DeveloperProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    api_key_hash: str
    request_count: int
    created_at: datetime
    updated_at: datetime


# 2. Webhooks
class WebhookSubscriptionBase(BaseModel):
    target_url: str
    events: List[str] = Field(
        default_factory=lambda: ["evaluation.completed", "job.failed"]
    )
    is_active: bool = True


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    project_id: UUID
    secret_token: Optional[str] = None


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    secret_token: str
    created_at: datetime
    updated_at: datetime


class WebhookDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subscription_id: UUID
    event_type: str
    status_code: Optional[int]
    request_payload: Dict[str, Any]
    response_body: Optional[str]
    latency_ms: int
    success: bool
    attempt_count: int
    delivered_at: datetime


class WebhookOutboxEventCreate(BaseModel):
    project_id: UUID
    event_type: str
    payload: Dict[str, Any]


class WebhookOutboxEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    event_type: str
    payload: Dict[str, Any]
    status: str
    retry_count: int
    created_at: datetime
    processed_at: Optional[datetime]


# 3. Plugins
class PluginDescriptorBase(BaseModel):
    name: str
    identifier: str
    version: str
    plugin_type: str
    capabilities: List[str] = Field(default_factory=lambda: ["metric:compute"])
    configuration_schema: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    is_global: bool = False


class PluginDescriptorCreate(PluginDescriptorBase):
    workspace_id: Optional[str] = None


class PluginDescriptorResponse(PluginDescriptorBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: Optional[str] = None
    is_enabled: bool
    created_at: datetime
    updated_at: datetime


# 4. Model Context Protocol (MCP)
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


# 5. Playground
class PlaygroundExecuteRequest(BaseModel):
    endpoint: str
    method: str = "GET"
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None


class PlaygroundExecuteResponse(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: Any
    latency_ms: int
    request_id: str
