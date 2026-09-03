from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import _extract_workspace_id, get_db, get_optional_api_key
from app.platform.schemas import MCPCallRequest, MCPCallResponse, MCPToolDefinition
from app.platform.services.mcp_tool_runner import mcp_tool_runner
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/mcp", tags=["Developer Platform - Model Context Protocol"])


@router.get("/tools", response_model=ApiResponse[List[MCPToolDefinition]])
async def list_mcp_tools():
    """Retrieve all available MCP-compatible tools for AI Agent integration."""
    tools = mcp_tool_runner.list_tools()
    return create_response(True, "MCP tools retrieved.", list(tools))


@router.post("/tools/call", response_model=MCPCallResponse)
async def call_mcp_tool(
    payload: MCPCallRequest,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_optional_api_key),
):
    """Executes an MCP tool call with workspace isolation."""
    workspace_id = _extract_workspace_id(current_key)
    res = await mcp_tool_runner.execute_tool(
        db=db,
        name=payload.name,
        arguments=payload.arguments,
        workspace_id=workspace_id,
    )
    return MCPCallResponse(
        content=res.get("content", []),
        is_error=res.get("is_error", False),
    )
