from typing import Any, Dict, List

import structlog

logger = structlog.get_logger()


class MCPServer:
    """Model Context Protocol (MCP) Server.

    Enables AI agents to query EvalForge databases, discover datasets/evaluations,
    and trigger runs through structured tool integrations.
    """

    def __init__(self):
        self._tools = {
            "get_project_summary": {
                "name": "get_project_summary",
                "description": "Retrieve project details, including evaluation history and metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The target project UUID.",
                        }
                    },
                    "required": ["project_id"],
                },
            },
            "trigger_evaluation_run": {
                "name": "trigger_evaluation_run",
                "description": "Start an asynchronous LLM evaluation batch task.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "dataset_id": {"type": "string"},
                        "judge": {
                            "type": "string",
                            "enum": ["geval", "deepeval", "rubric"],
                        },
                    },
                    "required": ["project_id", "dataset_id", "judge"],
                },
            },
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self._tools.values())

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing MCP tool call", tool=name, arguments=arguments)
        if name not in self._tools:
            return {
                "content": [
                    {"type": "text", "text": f"Error: Tool '{name}' not found."}
                ],
                "is_error": True,
            }

        # Simulate execution response
        if name == "get_project_summary":
            project_id = arguments.get("project_id")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Project Summary for '{project_id}': Active. Total Runs: 42. Success Rate: 91.5%.",
                    }
                ],
                "is_error": False,
            }

        elif name == "trigger_evaluation_run":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Evaluation Run initiated successfully. Job ID: {arguments.get('dataset_id')}_run.",
                    }
                ],
                "is_error": False,
            }

        return {
            "content": [{"type": "text", "text": "Unimplemented action."}],
            "is_error": True,
        }


# Global MCP Server Singleton
mcp_server = MCPServer()
