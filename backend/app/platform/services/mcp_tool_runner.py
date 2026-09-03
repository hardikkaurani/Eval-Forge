from typing import Any, Dict, List

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import ProjectRepository
from app.datasets.repositories.dataset import DatasetRepository
from app.evaluation.repositories.evaluation import EvaluationRepository
from app.platform.schemas import MCPToolDefinition

logger = structlog.get_logger()


class MCPToolRunner:
    """Model Context Protocol (MCP) Tool Runner.

    Exposes native Eval-Forge domain operations as standardized tools for AI agents
    with tenant-level authorization and bounded output payloads.
    """

    def list_tools(self) -> List[MCPToolDefinition]:
        return [
            MCPToolDefinition(
                name="list_projects",
                description="List all evaluation projects accessible in the workspace.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "page": {"type": "integer", "default": 1},
                        "page_size": {"type": "integer", "default": 20},
                    },
                },
            ),
            MCPToolDefinition(
                name="list_datasets",
                description="List datasets available for evaluation in a project.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project UUID"},
                    },
                    "required": ["project_id"],
                },
            ),
            MCPToolDefinition(
                name="get_evaluation_status",
                description="Retrieve real-time execution status and completed case counts for an evaluation run.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "run_id": {
                            "type": "string",
                            "description": "Evaluation run UUID",
                        },
                    },
                    "required": ["run_id"],
                },
            ),
            MCPToolDefinition(
                name="get_evaluation_results",
                description="Retrieve scored metrics, judge reasoning, and latency stats for an evaluation run.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "run_id": {
                            "type": "string",
                            "description": "Evaluation run UUID",
                        },
                        "limit": {"type": "integer", "default": 50},
                    },
                    "required": ["run_id"],
                },
            ),
        ]

    async def execute_tool(
        self,
        db: AsyncSession,
        name: str,
        arguments: Dict[str, Any],
        workspace_id: str,
    ) -> Dict[str, Any]:
        """Executes an MCP tool with workspace isolation."""
        logger.info("Executing MCP tool", tool=name, workspace_id=workspace_id)

        try:
            if name == "list_projects":
                project_repo = ProjectRepository(db)
                page = int(arguments.get("page", 1))
                page_size = int(arguments.get("page_size", 20))
                projects, count = await project_repo.list(
                    workspace_id=workspace_id,
                    skip=(page - 1) * page_size,
                    limit=page_size,
                )
                return {
                    "content": [
                        {
                            "type": "json",
                            "data": {
                                "total": count,
                                "projects": [
                                    {
                                        "id": str(p.id),
                                        "name": p.name,
                                        "description": p.description,
                                    }
                                    for p in projects
                                ],
                            },
                        }
                    ],
                    "is_error": False,
                }

            elif name == "list_datasets":
                project_id = arguments.get("project_id")
                if not project_id:
                    raise ValueError("project_id argument is required.")

                project_repo = ProjectRepository(db)
                project = await project_repo.get_by_id(
                    str(project_id), workspace_id=workspace_id
                )

                if not project:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Project '{project_id}' not found.",
                            }
                        ],
                        "is_error": True,
                    }

                dataset_repo = DatasetRepository(db)
                datasets, count = await dataset_repo.list_datasets(
                    project_id=str(project.id),
                    skip=0,
                    limit=50,
                )
                return {
                    "content": [
                        {
                            "type": "json",
                            "data": {
                                "total": count,
                                "datasets": [
                                    {
                                        "id": str(d.id),
                                        "name": d.name,
                                        "description": d.description,
                                    }
                                    for d in datasets
                                ],
                            },
                        }
                    ],
                    "is_error": False,
                }

            elif name == "get_evaluation_status":
                run_id = arguments.get("run_id")
                if not run_id:
                    raise ValueError("run_id argument is required.")

                run = await EvaluationRepository.get_run(db, str(run_id))
                if not run:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Evaluation run '{run_id}' not found.",
                            }
                        ],
                        "is_error": True,
                    }

                evaluation = await EvaluationRepository.get_evaluation(
                    db, str(run.evaluation_id), workspace_id=workspace_id
                )
                if not evaluation:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Evaluation run '{run_id}' not found.",
                            }
                        ],
                        "is_error": True,
                    }

                return {
                    "content": [
                        {
                            "type": "json",
                            "data": {
                                "run_id": str(run.id),
                                "status": run.status,
                                "total_cases": run.total_cases,
                                "completed_cases": run.completed_cases,
                                "failed_cases": run.failed_cases,
                                "error_message": getattr(run, "error_message", None),
                            },
                        }
                    ],
                    "is_error": False,
                }

            elif name == "get_evaluation_results":
                run_id = arguments.get("run_id")
                if not run_id:
                    raise ValueError("run_id argument is required.")

                run = await EvaluationRepository.get_run(db, str(run_id))
                if not run:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Evaluation run '{run_id}' not found.",
                            }
                        ],
                        "is_error": True,
                    }

                evaluation = await EvaluationRepository.get_evaluation(
                    db, str(run.evaluation_id), workspace_id=workspace_id
                )
                if not evaluation:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Evaluation run '{run_id}' not found.",
                            }
                        ],
                        "is_error": True,
                    }

                results, count = await EvaluationRepository.list_results(
                    db, run_id=str(run_id), limit=arguments.get("limit", 50)
                )
                return {
                    "content": [
                        {
                            "type": "json",
                            "data": {
                                "total": count,
                                "results": [
                                    {
                                        "id": str(r.id),
                                        "input_prompt": r.input_prompt,
                                        "model_output": r.model_output,
                                        "metrics": r.metrics,
                                        "passed": r.passed,
                                        "latency_ms": r.latency_ms,
                                    }
                                    for r in results
                                ],
                            },
                        }
                    ],
                    "is_error": False,
                }

            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool '{name}'."}],
                    "is_error": True,
                }

        except Exception as e:
            logger.exception("MCP tool execution failed", tool=name, error=str(e))
            return {
                "content": [
                    {"type": "text", "text": f"Tool execution failed: {str(e)}"}
                ],
                "is_error": True,
            }


mcp_tool_runner = MCPToolRunner()
