from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import UUID

from evalforge.models import Dataset, EvaluationResult, EvaluationRun, Job, Project

if TYPE_CHECKING:
    from evalforge.client import AsyncEvalForge, EvalForge


class ProjectsResource:

    def __init__(self, client: "EvalForge"):
        self._client = client

    def create(self, name: str, description: Optional[str] = None) -> Project:
        data = self._client._request(
            "POST",
            "/api/v1/projects",
            json={"name": name, "description": description},
        )
        return Project.model_validate(data.get("data", data))

    def list(self, page: int = 1, page_size: int = 20) -> List[Project]:
        data = self._client._request(
            "GET",
            "/api/v1/projects",
            params={"page": page, "page_size": page_size},
        )
        items = data.get("data", data)
        return [Project.model_validate(i) for i in (items if isinstance(items, list) else [])]

    def get(self, project_id: UUID | str) -> Project:
        data = self._client._request("GET", f"/api/v1/projects/{project_id}")
        return Project.model_validate(data.get("data", data))


class DatasetsResource:

    def __init__(self, client: "EvalForge"):
        self._client = client

    def create(self, project_id: UUID | str, name: str, description: Optional[str] = None) -> Dataset:
        data = self._client._request(
            "POST",
            "/api/v1/datasets",
            json={"project_id": str(project_id), "name": name, "description": description},
        )
        return Dataset.model_validate(data.get("data", data))

    def list(self, project_id: UUID | str) -> List[Dataset]:
        data = self._client._request("GET", "/api/v1/datasets", params={"project_id": str(project_id)})
        items = data.get("data", data)
        return [Dataset.model_validate(i) for i in (items if isinstance(items, list) else [])]


class EvaluationsResource:

    def __init__(self, client: "EvalForge"):
        self._client = client

    def create(
        self,
        project_id: UUID | str,
        name: str,
        test_cases: List[Dict[str, Any]],
        metrics: Optional[List[str]] = None,
    ) -> EvaluationRun:
        payload = {
            "project_id": str(project_id),
            "name": name,
            "test_cases": test_cases,
            "metrics": metrics or ["accuracy", "semantic_similarity"],
        }
        data = self._client._request("POST", "/api/v1/evaluations", json=payload)
        return EvaluationRun.model_validate(data.get("data", data))

    def get(self, run_id: UUID | str) -> EvaluationRun:
        data = self._client._request("GET", f"/api/v1/evaluations/{run_id}")
        return EvaluationRun.model_validate(data.get("data", data))

    def list_results(self, run_id: UUID | str, limit: int = 50) -> List[EvaluationResult]:
        data = self._client._request("GET", f"/api/v1/evaluations/{run_id}/results", params={"limit": limit})
        items = data.get("data", data)
        return [EvaluationResult.model_validate(i) for i in (items if isinstance(items, list) else [])]


class JobsResource:

    def __init__(self, client: "EvalForge"):
        self._client = client

    def get(self, job_id: UUID | str) -> Job:
        data = self._client._request("GET", f"/api/v1/jobs/{job_id}")
        return Job.model_validate(data.get("data", data))


class AsyncProjectsResource:

    def __init__(self, client: "AsyncEvalForge"):
        self._client = client

    async def create(self, name: str, description: Optional[str] = None) -> Project:
        data = await self._client._request(
            "POST",
            "/api/v1/projects",
            json={"name": name, "description": description},
        )
        return Project.model_validate(data.get("data", data))

    async def list(self, page: int = 1, page_size: int = 20) -> List[Project]:
        data = await self._client._request(
            "GET",
            "/api/v1/projects",
            params={"page": page, "page_size": page_size},
        )
        items = data.get("data", data)
        return [Project.model_validate(i) for i in (items if isinstance(items, list) else [])]

    async def get(self, project_id: UUID | str) -> Project:
        data = await self._client._request("GET", f"/api/v1/projects/{project_id}")
        return Project.model_validate(data.get("data", data))


class AsyncDatasetsResource:

    def __init__(self, client: "AsyncEvalForge"):
        self._client = client

    async def create(self, project_id: UUID | str, name: str, description: Optional[str] = None) -> Dataset:
        data = await self._client._request(
            "POST",
            "/api/v1/datasets",
            json={"project_id": str(project_id), "name": name, "description": description},
        )
        return Dataset.model_validate(data.get("data", data))

    async def list(self, project_id: UUID | str) -> List[Dataset]:
        data = await self._client._request("GET", "/api/v1/datasets", params={"project_id": str(project_id)})
        items = data.get("data", data)
        return [Dataset.model_validate(i) for i in (items if isinstance(items, list) else [])]


class AsyncEvaluationsResource:

    def __init__(self, client: "AsyncEvalForge"):
        self._client = client

    async def create(
        self,
        project_id: UUID | str,
        name: str,
        test_cases: List[Dict[str, Any]],
        metrics: Optional[List[str]] = None,
    ) -> EvaluationRun:
        payload = {
            "project_id": str(project_id),
            "name": name,
            "test_cases": test_cases,
            "metrics": metrics or ["accuracy", "semantic_similarity"],
        }
        data = await self._client._request("POST", "/api/v1/evaluations", json=payload)
        return EvaluationRun.model_validate(data.get("data", data))

    async def get(self, run_id: UUID | str) -> EvaluationRun:
        data = await self._client._request("GET", f"/api/v1/evaluations/{run_id}")
        return EvaluationRun.model_validate(data.get("data", data))

    async def list_results(self, run_id: UUID | str, limit: int = 50) -> List[EvaluationResult]:
        data = await self._client._request("GET", f"/api/v1/evaluations/{run_id}/results", params={"limit": limit})
        items = data.get("data", data)
        return [EvaluationResult.model_validate(i) for i in (items if isinstance(items, list) else [])]


class AsyncJobsResource:

    def __init__(self, client: "AsyncEvalForge"):
        self._client = client

    async def get(self, job_id: UUID | str) -> Job:
        data = await self._client._request("GET", f"/api/v1/jobs/{job_id}")
        return Job.model_validate(data.get("data", data))
