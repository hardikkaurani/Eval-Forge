from typing import Any, Dict, List

import httpx


class EvalForgeClient:
    """Official EvalForge Python SDK Client."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        self.client = httpx.Client(headers=self.headers, timeout=timeout)

    def trigger_run(self, project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submits an asynchronous evaluation run."""
        url = f"{self.base_url}/api/v1/evaluations/batch"
        # Set project ID in payload
        payload["project_id"] = project_id
        res = self.client.post(url, json=payload)
        res.raise_for_status()
        return res.json()

    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Polls the status of an active evaluation run."""
        url = f"{self.base_url}/api/v1/evaluations/runs/{run_id}"
        res = self.client.get(url)
        res.raise_for_status()
        return res.json()

    def register_webhook(
        self, project_id: str, target_url: str, events: List[str]
    ) -> Dict[str, Any]:
        """Registers a new webhook target URL for event streams."""
        url = f"{self.base_url}/api/v1/webhooks"
        payload = {"project_id": project_id, "target_url": target_url, "events": events}
        res = self.client.post(url, json=payload)
        res.raise_for_status()
        return res.json()
