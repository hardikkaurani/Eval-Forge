import asyncio
import hashlib
import hmac
import ipaddress
import json
import socket
import time
import urllib.parse
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config.config import settings
from app.platform.models import (
    WebhookDelivery,
    WebhookOutboxEvent,
    WebhookSubscription,
)

logger = structlog.get_logger()

PROHIBITED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / Cloud Metadata
    ipaddress.ip_network("100.64.0.0/10"),    # Carrier-grade NAT
    ipaddress.ip_network("198.18.0.0/15"),    # Benchmark testing
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-local
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique-local private
    ipaddress.ip_network("::/128"),           # IPv6 Unspecified
]


def validate_webhook_destination(url: str, allow_http: bool = False) -> tuple[bool, str]:
    """Validates destination webhook URL against SSRF, private CIDRs, and prohibited schemes."""
    if not url or not isinstance(url, str):
        return False, "Target URL is missing or invalid."

    try:
        parsed = urllib.parse.urlparse(url.strip())
    except Exception as e:
        return False, f"Failed to parse URL: {str(e)}"

    scheme = parsed.scheme.lower()
    if scheme == "https":
        pass
    elif scheme == "http":
        if not allow_http and settings.APP_ENV == "production":
            return False, "HTTP scheme is prohibited in production; HTTPS is required."
    else:
        return False, f"Unsupported URL scheme '{scheme}'. Only HTTPS/HTTP are permitted."

    if parsed.username or parsed.password:
        return False, "Embedding credentials in webhook URL is prohibited."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in target URL."

    # Check for direct localhost hostname
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        return False, "Prohibited loopback or metadata hostname."

    # Resolve IP addresses for hostname
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        resolved_ips = {item[4][0] for item in addr_info}
    except Exception as e:
        return False, f"Failed to resolve hostname '{hostname}': {str(e)}"

    if not resolved_ips:
        return False, f"Could not resolve any IP address for host '{hostname}'."

    for ip_str in resolved_ips:
        try:
            ip_obj = ipaddress.ip_address(ip_str)

            # Check IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
            if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
                ip_obj = ip_obj.ipv4_mapped

            if (
                ip_obj.is_loopback
                or ip_obj.is_private
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
            ):
                return False, f"Resolved IP '{ip_str}' belongs to a private, loopback, or reserved network."

            for net in PROHIBITED_IP_NETWORKS:
                if ip_obj in net:
                    return False, f"Resolved IP '{ip_str}' is within prohibited CIDR {net}."
        except ValueError:
            return False, f"Invalid IP address representation: '{ip_str}'."

    return True, ""


def generate_webhook_signature(
    payload_str: str, secret: str, timestamp: Optional[int] = None
) -> str:
    """Generates an HMAC-SHA256 signature header formatted as: t={timestamp},v1={hex_hash}."""
    t = timestamp if timestamp is not None else int(time.time())
    signed_payload = f"{t}.{payload_str}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={t},v1={signature}"


def verify_webhook_signature(
    payload_str: str,
    secret: str,
    signature_header: str,
    tolerance_seconds: int = 300,
) -> bool:
    """Verifies HMAC-SHA256 signature header and validates that the timestamp is within tolerance."""
    if not signature_header or "t=" not in signature_header or "v1=" not in signature_header:
        return False

    try:
        parts = dict(item.split("=", 1) for item in signature_header.split(","))
        timestamp = int(parts.get("t", "0"))
        provided_sig = parts.get("v1", "")

        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance_seconds:
            logger.warning("Webhook signature timestamp expired or out of tolerance", diff=abs(current_time - timestamp))
            return False

        expected_sig = generate_webhook_signature(payload_str, secret, timestamp)
        expected_hash = expected_sig.split("v1=")[-1]
        return hmac.compare_digest(provided_sig, expected_hash)
    except Exception as e:
        logger.warning("Failed to verify webhook signature", error=str(e))
        return False


class WebhookOutboxService:
    """Transactional Outbox and Dispatcher for reliable webhook deliveries."""

    def __init__(self, timeout_seconds: float = 5.0, max_retries: int = 3):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def enqueue_event(
        self,
        db: AsyncSession,
        project_id: uuid.UUID,
        event_type: str,
        payload: Dict[str, Any],
    ) -> WebhookOutboxEvent:
        """Atomically records an event in the outbox table within the caller's DB transaction."""
        event = WebhookOutboxEvent(
            id=uuid.uuid4(),
            project_id=project_id,
            event_type=event_type,
            payload=payload,
            status="PENDING",
            retry_count=0,
            max_retries=self.max_retries,
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        return event

    async def process_outbox_event(
        self,
        db: AsyncSession,
        event_id: uuid.UUID,
    ) -> List[WebhookDelivery]:
        """Dispatches an outbox event to all active matching webhook subscriptions."""
        res = await db.execute(
            select(WebhookOutboxEvent).where(WebhookOutboxEvent.id == event_id)
        )
        event = res.scalar_one_or_none()
        if not event:
            return []

        # Find subscriptions for this project that listen to this event
        sub_res = await db.execute(
            select(WebhookSubscription).where(
                WebhookSubscription.project_id == event.project_id,
                WebhookSubscription.is_active.is_(True),
            )
        )
        subscriptions = sub_res.scalars().all()
        matching_subs = [
            s for s in subscriptions if event.event_type in (s.events or [])
        ]

        deliveries: List[WebhookDelivery] = []
        for sub in matching_subs:
            delivery = await self._deliver_to_subscription(db, sub, event.event_type, event.payload)
            deliveries.append(delivery)

        event.status = "PROCESSED"
        event.processed_at = datetime.now(timezone.utc)
        await db.commit()
        return deliveries

    async def _deliver_to_subscription(
        self,
        db: AsyncSession,
        subscription: WebhookSubscription,
        event_type: str,
        payload: Dict[str, Any],
    ) -> WebhookDelivery:
        target_url = str(subscription.target_url)
        is_safe, error_reason = validate_webhook_destination(
            target_url, allow_http=(settings.APP_ENV != "production")
        )

        payload_body = {
            "event": event_type,
            "subscription_id": str(subscription.id),
            "project_id": str(subscription.project_id),
            "timestamp": int(time.time()),
            "data": payload,
        }
        payload_str = json.dumps(payload_body, sort_keys=True)
        signature = generate_webhook_signature(payload_str, str(subscription.secret_token))

        headers = {
            "Content-Type": "application/json",
            "X-EvalForge-Signature": signature,
            "X-EvalForge-Event": event_type,
            "User-Agent": "EvalForge-Webhook-Outbox/1.0",
        }

        success = False
        status_code = None
        response_body = ""
        attempt_count = 0
        start_time = time.perf_counter()

        if not is_safe:
            logger.warning(
                "Webhook delivery blocked by SSRF defense",
                url=target_url,
                reason=error_reason,
            )
            response_body = "Delivery blocked: Prohibited destination."
            status_code = 400
        else:
            for attempt in range(self.max_retries):
                attempt_count += 1
                try:
                    async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                        response = await client.post(
                            target_url,
                            content=payload_str,
                            headers=headers,
                        )
                        status_code = response.status_code
                        response_body = response.text
                        if response.status_code in (200, 201, 202, 204):
                            success = True
                            break
                except Exception as e:
                    response_body = f"Connection failed: {str(e)}"
                    logger.warning(
                        "Webhook delivery failed",
                        url=target_url,
                        attempt=attempt + 1,
                        error=str(e),
                    )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(min(0.5 * (2**attempt), 5.0))

        latency = int((time.perf_counter() - start_time) * 1000)

        delivery = WebhookDelivery(
            id=uuid.uuid4(),
            subscription_id=subscription.id,
            event_type=event_type,
            status_code=status_code,
            request_payload=payload_body,
            response_body=response_body[:2000] if response_body else None,
            latency_ms=latency,
            success=success,
            attempt_count=attempt_count,
            delivered_at=datetime.now(timezone.utc),
        )
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        return delivery


webhook_outbox_service = WebhookOutboxService()
