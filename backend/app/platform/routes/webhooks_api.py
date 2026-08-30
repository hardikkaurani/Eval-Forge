from typing import Any, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.dependencies import _extract_workspace_id, get_current_api_key
from app.database.repository import ProjectRepository
from app.database.session import get_db
from app.platform.models import WebhookDelivery, WebhookSubscription
from app.platform.schemas import (
    WebhookDeliveryResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/webhooks", tags=["Developer Platform - Webhooks"])


async def _verify_project_ws(
    db: AsyncSession, project_id: UUID | str, workspace_id: str
) -> None:
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(str(project_id), workspace_id=workspace_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )


@router.post(
    "", response_model=ApiResponse[WebhookSubscriptionResponse], status_code=201
)
async def create_webhook_subscription(
    payload: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, payload.project_id, workspace_id)
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
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    await _verify_project_ws(db, project_id, workspace_id)
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
    subscription_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    workspace_id = _extract_workspace_id(current_key)
    res_sub = await db.execute(
        select(WebhookSubscription).where(WebhookSubscription.id == subscription_id)
    )
    sub = res_sub.scalar_one_or_none()
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )
    await _verify_project_ws(db, sub.project_id, workspace_id)

    result = await db.execute(
        select(WebhookDelivery).where(
            WebhookDelivery.subscription_id == subscription_id
        )
    )
    deliveries = result.scalars().all()
    return create_response(True, "Deliveries retrieved.", list(deliveries))
