from uuid import uuid4
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.session import get_db
from app.platform.models import PluginDescriptor
from app.platform.schemas import PluginDescriptorCreate, PluginDescriptorResponse
from app.platform.services.plugin_engine import plugin_engine
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/plugins", tags=["Developer Platform - Plugins"])


@router.post("", response_model=ApiResponse[PluginDescriptorResponse], status_code=201)
async def register_plugin(
    payload: PluginDescriptorCreate,
    db: AsyncSession = Depends(get_db)
):
    plugin = PluginDescriptor(
        id=uuid4(),
        name=payload.name,
        identifier=payload.identifier,
        version=payload.version,
        plugin_type=payload.plugin_type,
        configuration_schema=payload.configuration_schema,
        settings=payload.settings,
        is_enabled=True
    )
    db.add(plugin)
    await db.commit()
    await db.refresh(plugin)
    return create_response(True, "Plugin registered successfully.", plugin)


@router.get("", response_model=ApiResponse[List[PluginDescriptorResponse]])
async def list_active_plugins(
    db: AsyncSession = Depends(get_db)
):
    plugins = await plugin_engine.discover_plugins(db)
    return create_response(True, "Active plugins discovered.", list(plugins))


@router.post("/{identifier}/execute", response_model=ApiResponse[dict])
async def execute_plugin(
    identifier: str,
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    # Ensure active plugins are loaded
    await plugin_engine.discover_plugins(db)
    try:
        res = plugin_engine.execute_metric_plugin(identifier, payload)
        return create_response(True, "Plugin executed successfully.", res)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
