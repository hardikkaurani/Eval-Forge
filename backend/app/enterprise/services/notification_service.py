import uuid
from datetime import datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.enterprise.models import EnterpriseNotification

logger = structlog.get_logger()


class NotificationService:
    """Dispatches SaaS notifications across email, Slack, Discord, and Webhooks."""

    async def send_notification(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        recipient_id: uuid.UUID,
        channel: str,
        title: str,
        content: str,
    ) -> EnterpriseNotification:
        notification = EnterpriseNotification(
            id=uuid.uuid4(),
            organization_id=org_id,
            recipient_id=recipient_id,
            channel=channel,
            title=title,
            content=content,
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(notification)
        await db.flush()

        # Mock/Actual channel delivery execution
        success = await self._dispatch_to_channel(channel, title, content)
        notification.status = "sent" if success else "failed"

        await db.commit()
        await db.refresh(notification)
        return notification

    async def _dispatch_to_channel(
        self, channel: str, title: str, content: str
    ) -> bool:
        logger.info("Dispatching notification", channel=channel, title=title)

        if channel == "email":
            # Mock email sending via SMTP/Mailgun
            return True

        elif channel in ("slack", "discord"):
            # Mock slack/discord webhook call
            return True

        elif channel == "webhook":
            # Mock external webhook delivery
            return True

        return True
