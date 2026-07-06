from typing import List

from fastapi import APIRouter

from app.platform.schemas import MCPCallRequest, MCPCallResponse, MCPToolDefinition
from app.platform.services.mcp_server import mcp_server
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/mcp", tags=["Developer Platform - Model Context Protocol"])


@router.get("/tools", response_model=ApiResponse[List[MCPToolDefinition]])
async def list_mcp_tools():
    """Retrieve all available MCP-compatible tools for AI Agent integration."""
    tools = mcp_server.list_tools()
    return create_response(True, "MCP tools retrieved.", list(tools))


@router.post("/tools/call", response_model=MCPCallResponse)
async def call_mcp_tool(payload: MCPCallRequest):
    """Executes an MCP tool call with provided arguments."""
    res = await mcp_server.call_tool(payload.name, payload.arguments)
    return MCPCallResponse(
        content=res.get("content", []), is_error=res.get("is_error", False)
    )
