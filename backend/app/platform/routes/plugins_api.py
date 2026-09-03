from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import extract_workspace_id, get_optional_api_key
from app.database.session import get_db
from app.platform.schemas import PluginDescriptorCreate, PluginDescriptorResponse
from app.platform.services.plugin_registry import plugin_registry_service
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/plugins", tags=["Developer Platform - Plugins"])


@router.post("", response_model=ApiResponse[PluginDescriptorResponse], status_code=201)
async def register_plugin(
    payload: PluginDescriptorCreate,
    current_key: Any = Depends(get_optional_api_key),
    db: AsyncSession = Depends(get_db),
):
    try:
        ws_id = payload.workspace_id or (
            extract_workspace_id(current_key) if current_key else None
        )
        plugin = await plugin_registry_service.register_plugin(
            db=db,
            name=payload.name,
            identifier=payload.identifier,
            version=payload.version,
            plugin_type=payload.plugin_type,
            capabilities=payload.capabilities,
            configuration_schema=payload.configuration_schema,
            settings=payload.settings,
            workspace_id=ws_id,
            is_global=payload.is_global,
        )
        return create_response(True, "Plugin registered successfully.", plugin)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("", response_model=ApiResponse[List[PluginDescriptorResponse]])
async def list_active_plugins(
    only_enabled: bool = True,
    current_key: Any = Depends(get_optional_api_key),
    db: AsyncSession = Depends(get_db),
):
    ws_id = extract_workspace_id(current_key) if current_key else None
    plugins = await plugin_registry_service.list_plugins(
        db, workspace_id=ws_id, only_enabled=only_enabled
    )
    return create_response(True, "Plugins retrieved.", list(plugins))


@router.post("/{identifier}/execute", response_model=ApiResponse[dict])
async def execute_plugin(
    identifier: str,
    payload: dict,
    current_key: Any = Depends(get_optional_api_key),
    db: AsyncSession = Depends(get_db),
):
    try:
        ws_id = extract_workspace_id(current_key) if current_key else None
        res = await plugin_registry_service.execute_plugin(
            db, identifier, payload, workspace_id=ws_id
        )
        return create_response(True, "Plugin executed successfully.", res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
