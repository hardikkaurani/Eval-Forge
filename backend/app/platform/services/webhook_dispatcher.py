import hmac
import hashlib
import time
import json
import uuid
import asyncio
from typing import Dict, Any, Optional
import httpx
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models import WebhookSubscription, WebhookDelivery

logger = structlog.get_logger()


class WebhookDispatcher:
    """Webhook Dispatcher Service.

    Signs webhook request bodies using HMAC-SHA256, delivers payloads to target URLs,
    implements backoff retries, and records execution audit logs.
    """

    def __init__(self, timeout_seconds: float = 5.0, max_retries: int = 3):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def _generate_signature(self, payload_str: str, secret: str) -> str:
        key = secret.encode("utf-8")
        msg = payload_str.encode("utf-8")
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    async def dispatch(
        self,
        db: AsyncSession,
        subscription: WebhookSubscription,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        payload_str = json.dumps({
            "event": event_type,
            "subscription_id": str(subscription.id),
            "timestamp": int(time.time()),
            "data": payload
        })
        signature = self._generate_signature(payload_str, subscription.secret_token)

        headers = {
            "Content-Type": "application/json",
            "X-EvalForge-Signature": signature,
            "X-EvalForge-Event": event_type,
            "User-Agent": "EvalForge-Webhook-Dispatcher/1.0"
        }

        success = False
        status_code = None
        response_body = ""
        start_time = time.perf_counter()

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(
                        subscription.target_url,
                        content=payload_str,
                        headers=headers
                    )
                    status_code = response.status_code
                    response_body = response.text
                    if response.status_code in (200, 201, 202, 204):
                        success = True
                        break
            except Exception as e:
                response_body = f"Connection failed: {str(e)}"
                logger.warning(
                    "Webhook delivery attempt failed",
                    url=subscription.target_url,
                    attempt=attempt + 1,
                    error=str(e)
                )
            
            # Backoff delay
            await asyncio.sleep(2.0 ** attempt)

        latency = int((time.perf_counter() - start_time) * 1000)

        # Log delivery report
        delivery = WebhookDelivery(
            id=uuid.uuid4(),
            subscription_id=subscription.id,
            event_type=event_type,
            status_code=status_code,
            request_payload=payload,
            response_body=response_body[:2000], # Cap response storage
            latency_ms=latency,
            success=success
        )
        db.add(delivery)
        await db.commit()

        logger.info(
            "Webhook dispatched",
            url=subscription.target_url,
            event=event_type,
            success=success,
            status_code=status_code,
            latency_ms=latency
        )
        return success

