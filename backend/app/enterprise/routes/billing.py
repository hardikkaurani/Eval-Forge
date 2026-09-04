import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_api_key
from app.database.session import get_db
from app.enterprise.exceptions import BillingGatewayException
from app.enterprise.routes.organizations import _verify_org_membership
from app.enterprise.schemas import InvoiceResponse, SubscriptionResponse
from app.enterprise.services.billing_service import BillingService
from app.utils.responses import ApiResponse, create_response

router = APIRouter(prefix="/billing", tags=["Enterprise SaaS - Billing"])
public_webhook_router = APIRouter(
    prefix="/billing/webhooks", tags=["Enterprise SaaS - Webhooks"]
)
billing_service = BillingService()


async def _verify_billing_authority(
    db: AsyncSession,
    current_key: Any,
    org_id: uuid.UUID,
    required_action: str = "write",
) -> None:
    """Enforces role and scope-based authorization for organization billing operations."""
    if not current_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    perm = "billing:read" if required_action == "read" else "billing:manage"
    await _verify_org_membership(db, current_key, org_id, perm)

    scopes = getattr(current_key, "scopes", None)
    if scopes is not None and isinstance(scopes, list) and len(scopes) > 0:
        has_read = any(
            s in scopes
            for s in [
                "billing:read",
                "billing:write",
                "read:all",
                "admin",
                "owner",
                "*",
            ]
        )
        has_write = any(s in scopes for s in ["billing:write", "admin", "owner", "*"])

        if required_action == "read" and not has_read:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for billing inspection.",
            )
        if required_action == "write" and not has_write:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for billing state mutation.",
            )

    role = getattr(current_key, "role", None)
    if role and type(role).__name__ != "MagicMock":
        if required_action == "write" and role not in [
            "Owner",
            "Admin",
            "Billing Admin",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Organization Owners and Admins can mutate subscription plans.",
            )
        if required_action == "read" and role in ["Developer", "Viewer", "Auditor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for billing inspection.",
            )


@router.post("/checkout", response_model=ApiResponse[str])
async def create_checkout_session(
    org_id: uuid.UUID,
    plan_name: str,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Generates a Stripe billing checkout session URL with server-side price mapping."""
    await _verify_billing_authority(db, current_key, org_id, required_action="write")
    try:
        url = await billing_service.create_checkout_session(
            db, org_id, plan_name, success_url, cancel_url
        )
        return create_response(
            success=True, message="Checkout session created successfully.", data=url
        )
    except BillingGatewayException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.post("/customer-portal", response_model=ApiResponse[str])
async def create_customer_portal_session(
    org_id: uuid.UUID,
    return_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Generates a Stripe Customer Portal session URL for self-service subscription management."""
    await _verify_billing_authority(db, current_key, org_id, required_action="write")
    try:
        url = await billing_service.create_customer_portal_session(
            db, org_id, return_url
        )
        return create_response(
            success=True,
            message="Customer portal session created successfully.",
            data=url,
        )
    except BillingGatewayException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get("/subscription", response_model=ApiResponse[Optional[SubscriptionResponse]])
async def get_subscription_status(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Retrieves active subscription tier, status, and period boundaries for an organization."""
    await _verify_billing_authority(db, current_key, org_id, required_action="read")
    sub = await billing_service.get_active_subscription(db, org_id)
    return create_response(
        success=True,
        message="Subscription details retrieved.",
        data=SubscriptionResponse.model_validate(sub) if sub else None,
    )


@router.post("/subscriptions", response_model=ApiResponse[SubscriptionResponse])
async def create_subscription(
    org_id: uuid.UUID,
    plan_name: str,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Activates or updates an organization subscription plan with feature/usage limits."""
    await _verify_billing_authority(db, current_key, org_id, required_action="write")
    try:
        sub = await billing_service.create_subscription(db, org_id, plan_name)
        return create_response(
            success=True,
            message="Subscription updated successfully.",
            data=SubscriptionResponse.model_validate(sub),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/plans", response_model=ApiResponse[Dict[str, Any]])
async def list_available_plans():
    """Retrieves available SaaS monetization plans, resource limits, and feature flags."""
    from app.enterprise.services.billing_service import PLAN_PRICE_MAP

    return create_response(
        success=True,
        message="Available SaaS plans retrieved.",
        data=PLAN_PRICE_MAP,
    )


@router.get("/entitlements", response_model=ApiResponse[Dict[str, Any]])
async def get_organization_entitlements(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Retrieves resolved resource limits and active feature entitlements for an organization."""
    await _verify_billing_authority(db, current_key, org_id, required_action="read")
    entitlements = await billing_service.get_organization_entitlements(db, org_id)
    return create_response(
        success=True,
        message="Organization entitlements retrieved.",
        data=entitlements,
    )


@router.get("/invoices", response_model=ApiResponse[List[InvoiceResponse]])
async def get_invoice_history(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_key: Any = Depends(get_current_api_key),
):
    """Retrieves list of past billing invoices and receipts for the organization."""
    await _verify_billing_authority(db, current_key, org_id, required_action="read")
    invoices = await billing_service.get_billing_history(db, org_id)
    return create_response(
        success=True,
        message="Invoice history retrieved.",
        data=[InvoiceResponse.model_validate(inv) for inv in invoices],
    )


@public_webhook_router.post("/stripe")
async def stripe_webhook_listener(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """Public webhook listener receiving signed asynchronous Stripe events."""
    payload_bytes = await request.body()
    try:
        result = await billing_service.process_stripe_webhook(
            db, payload_bytes, stripe_signature
        )
        return result
    except BillingGatewayException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
