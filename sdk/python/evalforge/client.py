import asyncio
import os
import time
from typing import Any, Dict, Optional

import httpx

from evalforge.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
from evalforge.resources import (
    AsyncDatasetsResource,
    AsyncEvaluationsResource,
    AsyncJobsResource,
    AsyncProjectsResource,
    DatasetsResource,
    EvaluationsResource,
    JobsResource,
    ProjectsResource,
)

DEFAULT_BASE_URL = "http://localhost:8000"


class EvalForge:
    """Official synchronous Eval-Forge API Client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.environ.get("EVALFORGE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "Eval-Forge API key must be provided or set via EVALFORGE_API_KEY environment variable."
            )

        self.base_url = (base_url or os.environ.get("EVALFORGE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "evalforge-python/1.0.0",
            },
        )

        # Resources
        self.projects = ProjectsResource(self)
        self.datasets = DatasetsResource(self)
        self.evaluations = EvaluationsResource(self)
        self.jobs = JobsResource(self)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = self._http.request(method, path, params=params, json=json)
                request_id = response.headers.get("X-Request-ID")

                if response.status_code == 401:
                    raise AuthenticationError("Invalid or missing API key.", request_id=request_id)
                elif response.status_code == 404:
                    raise NotFoundError(f"Resource not found: {path}", request_id=request_id)
                elif response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        time.sleep(1.0 * (2**attempt))
                        continue
                    raise RateLimitError("Rate limit exceeded.", request_id=request_id)
                elif response.status_code >= 400:
                    raise APIError(
                        f"API Error {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        request_id=request_id,
                    )

                return response.json()

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(1.0 * (2**attempt))
                    continue
                raise APIConnectionError(f"Connection failed: {str(e)}") from e

        if last_exception:
            raise APIConnectionError(f"Request failed after {self.max_retries} retries.") from last_exception
        raise APIError("Unknown error occurred during request execution.", status_code=500)

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncEvalForge:
    """Official asynchronous Eval-Forge API Client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.environ.get("EVALFORGE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "Eval-Forge API key must be provided or set via EVALFORGE_API_KEY environment variable."
            )
        self.base_url = (base_url or os.environ.get("EVALFORGE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "evalforge-python-async/1.0.0",
            },
        )

        # Async Resources
        self.projects = AsyncProjectsResource(self)
        self.datasets = AsyncDatasetsResource(self)
        self.evaluations = AsyncEvaluationsResource(self)
        self.jobs = AsyncJobsResource(self)

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = await self._http.request(method, path, params=params, json=json)
                request_id = response.headers.get("X-Request-ID")

                if response.status_code == 401:
                    raise AuthenticationError("Invalid or missing API key.", request_id=request_id)
                elif response.status_code == 404:
                    raise NotFoundError(f"Resource not found: {path}", request_id=request_id)
                elif response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1.0 * (2**attempt))
                        continue
                    raise RateLimitError("Rate limit exceeded.", request_id=request_id)
                elif response.status_code >= 400:
                    raise APIError(
                        f"API Error {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        request_id=request_id,
                    )

                return response.json()

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1.0 * (2**attempt))
                    continue
                raise APIConnectionError(f"Connection failed: {str(e)}") from e

        if last_exception:
            raise APIConnectionError(f"Request failed after {self.max_retries} retries.") from last_exception
        raise APIError("Unknown error occurred during request execution.", status_code=500)

    async def aclose(self):
        await self._http.aclose()

    async def close(self):
        await self.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
