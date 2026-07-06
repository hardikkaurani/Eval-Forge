import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.enterprise.schemas import InvoiceResponse, SubscriptionResponse
from app.enterprise.services.billing_service import BillingService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/billing", tags=["Enterprise SaaS - Billing"])
billing_service = BillingService()


@router.post("/checkout", response_model=ApiResponse[str])
async def create_checkout_session(
    org_id: uuid.UUID, plan_name: str, provider: str = "stripe"
):
    """Generates a billing checkout session URL for Stripe, Paddle, or Lemon Squeezy."""
    try:
        connector = await billing_service.get_connector(provider)
        url = await connector.create_checkout_session(str(org_id), plan_name)
        return create_response(
            success=True, message="Checkout session created successfully.", data=url
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/subscriptions", response_model=ApiResponse[SubscriptionResponse])
async def create_subscription(
    org_id: uuid.UUID, plan_name: str, db: AsyncSession = Depends(get_db)
):
    """Activates or updates an organization subscription plan with feature/usage limits."""
    try:
        sub = await billing_service.create_subscription(db, org_id, plan_name)
        return create_response(
            success=True,
            message="Subscription updated successfully.",
            data=SubscriptionResponse.from_orm(sub),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/invoices", response_model=ApiResponse[List[InvoiceResponse]])
async def get_invoice_history(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieves list of past billing invoices and receipts for the organization."""
    invoices = await billing_service.get_billing_history(db, org_id)
    return create_response(
        success=True,
        message="Invoice history retrieved.",
        data=[InvoiceResponse.from_orm(inv) for inv in invoices],
    )
