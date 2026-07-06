import httpx
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class ConnectorManager:
    """Manages outgoing integrations and alert notifications to third-party endpoints."""

    def __init__(self, slack_webhook: str = None, discord_webhook: str = None):
        self.slack_webhook = slack_webhook
        self.discord_webhook = discord_webhook

    async def notify_slack(self, message: str) -> bool:
        if not self.slack_webhook:
            logger.debug("Slack webhook not configured, skipping alert.")
            return False
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(self.slack_webhook, json={"text": message})
                return res.status_code == 200
        except Exception as e:
            logger.error("Slack alert dispatch failed", error=str(e))
            return False

    async def notify_discord(self, message: str) -> bool:
        if not self.discord_webhook:
            logger.debug("Discord webhook not configured, skipping alert.")
            return False
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(self.discord_webhook, json={"content": message})
                return res.status_code == 204
        except Exception as e:
            logger.error("Discord alert dispatch failed", error=str(e))
            return False

    async def create_jira_issue(self, summary: str, description: str, jira_url: str, auth_token: str) -> Dict[str, Any]:
        """Creates an issue in Jira on run failure or regression alert."""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "project": {"key": "EVAL"},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Bug"}
            }
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(f"{jira_url}/rest/api/2/issue", json=payload, headers=headers)
                if res.status_code == 201:
                    return res.json()
        except Exception as e:
            logger.error("Jira issue creation failed", error=str(e))
        return {"success": False, "error": "Failed to create issue"}
