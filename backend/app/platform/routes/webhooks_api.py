from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.session import get_db
from app.platform.models import WebhookDelivery, WebhookSubscription
from app.platform.schemas import (
    WebhookDeliveryResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/webhooks", tags=["Developer Platform - Webhooks"])


@router.post(
    "", response_model=ApiResponse[WebhookSubscriptionResponse], status_code=201
)
async def create_webhook_subscription(
    payload: WebhookSubscriptionCreate, db: AsyncSession = Depends(get_db)
):
    sub = WebhookSubscription(
        id=uuid4(),
        project_id=payload.project_id,
        target_url=payload.target_url,
        secret_token=payload.secret_token or f"sec_{uuid4().hex[:16]}",
        events=payload.events,
        is_active=payload.is_active,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return create_response(True, "Webhook subscription created successfully.", sub)


@router.get("", response_model=ApiResponse[List[WebhookSubscriptionResponse]])
async def list_webhook_subscriptions(
    project_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WebhookSubscription).where(WebhookSubscription.project_id == project_id)
    )
    subs = result.scalars().all()
    return create_response(True, "Subscriptions retrieved.", list(subs))


@router.get(
    "/{subscription_id}/deliveries",
    response_model=ApiResponse[List[WebhookDeliveryResponse]],
)
async def list_webhook_deliveries(
    subscription_id: UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WebhookDelivery).where(
            WebhookDelivery.subscription_id == subscription_id
        )
    )
    deliveries = result.scalars().all()
    return create_response(True, "Deliveries retrieved.", list(deliveries))
