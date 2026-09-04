import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import sqlalchemy as sa
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config.config import settings
from app.enterprise.exceptions import BillingGatewayException
from app.enterprise.models import (
    Invoice,
    Organization,
    Plan,
    StripeWebhookEvent,
    Subscription,
)

logger = structlog.get_logger()

try:
    import stripe
except ImportError:
    stripe = None  # Handled safely via SDK runtime fallback


PLAN_PRICE_MAP = {
    "starter": {
        "name": "Starter",
        "price": 0.0,
        "limits": {
            "api_requests": 1000,
            "storage_mb": 100,
            "evaluations": 100,
            "datasets": 10,
            "concurrent_jobs": 2,
        },
        "features": {
            "rag_evaluation": False,
            "advanced_metrics": False,
            "custom_webhooks": False,
            "sso_saml": False,
            "audit_export": False,
        },
    },
    "pro": {
        "name": "Pro",
        "price": 49.0,
        "limits": {
            "api_requests": 10000,
            "storage_mb": 1000,
            "evaluations": 1000,
            "datasets": 50,
            "concurrent_jobs": 5,
        },
        "features": {
            "rag_evaluation": True,
            "advanced_metrics": True,
            "custom_webhooks": False,
            "sso_saml": False,
            "audit_export": False,
        },
    },
    "team": {
        "name": "Team",
        "price": 149.0,
        "limits": {
            "api_requests": 50000,
            "storage_mb": 5000,
            "evaluations": 5000,
            "datasets": 200,
            "concurrent_jobs": 10,
        },
        "features": {
            "rag_evaluation": True,
            "advanced_metrics": True,
            "custom_webhooks": True,
            "sso_saml": False,
            "audit_export": True,
        },
    },
    "business": {
        "name": "Business",
        "price": 499.0,
        "limits": {
            "api_requests": 250000,
            "storage_mb": 25000,
            "evaluations": 25000,
            "datasets": 1000,
            "concurrent_jobs": 25,
        },
        "features": {
            "rag_evaluation": True,
            "advanced_metrics": True,
            "custom_webhooks": True,
            "sso_saml": True,
            "audit_export": True,
        },
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 1499.0,
        "limits": {
            "api_requests": 1000000,
            "storage_mb": 100000,
            "evaluations": 100000,
            "datasets": 10000,
            "concurrent_jobs": 100,
        },
        "features": {
            "rag_evaluation": True,
            "advanced_metrics": True,
            "custom_webhooks": True,
            "sso_saml": True,
            "audit_export": True,
        },
    },
}


class BillingService:
    """Enterprise Billing Service managing Stripe Checkout, Customer Portal, Webhook State Machine and Subscriptions."""

    def __init__(self):
        self._stripe_api_key = (
            settings.STRIPE_SECRET_KEY.get_secret_value()
            if settings.STRIPE_SECRET_KEY
            else None
        )
        if stripe and self._stripe_api_key:
            stripe.api_key = self._stripe_api_key

    def _get_stripe_key(self) -> Optional[str]:
        return (
            settings.STRIPE_SECRET_KEY.get_secret_value()
            if settings.STRIPE_SECRET_KEY
            else None
        )

    def _get_webhook_secret(self) -> Optional[str]:
        return (
            settings.STRIPE_WEBHOOK_SECRET.get_secret_value()
            if settings.STRIPE_WEBHOOK_SECRET
            else None
        )

    async def seed_plans(self, db: AsyncSession) -> None:
        """Seeds default SaaS plans to database idempotently."""
        for _key, p in PLAN_PRICE_MAP.items():
            stmt = select(Plan).where(Plan.name == p["name"])
            existing = await db.execute(stmt)
            plan_record = existing.scalar_one_or_none()
            if not plan_record:
                plan = Plan(
                    id=uuid.uuid4(),
                    name=p["name"],
                    price_monthly=p["price"],
                    limits={**p["limits"], "features": p["features"]},
                    created_at=datetime.now(timezone.utc),
                )
                db.add(plan)
            else:
                # Update limits and features if missing
                plan_record.limits = {**p["limits"], "features": p["features"]}
        await db.commit()

    async def get_organization_plan(self, db: AsyncSession, org_id: uuid.UUID) -> Plan:
        """Resolves the effective plan for an organization, defaulting to Starter if unsubscribed."""
        stmt = (
            select(Plan)
            .join(Subscription, Subscription.plan_id == Plan.id)
            .where(
                Subscription.organization_id == org_id,
                Subscription.status == "active",
            )
            .order_by(Subscription.created_at.desc())
        )
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()

        if not plan:
            # Fallback to Starter plan
            starter_stmt = select(Plan).where(Plan.name == "Starter")
            starter_res = await db.execute(starter_stmt)
            plan = starter_res.scalar_one_or_none()
            if not plan:
                await self.seed_plans(db)
                starter_res2 = await db.execute(starter_stmt)
                plan = starter_res2.scalar_one()

        return plan

    async def get_organization_entitlements(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Returns all resolved resource limits and feature entitlement flags."""
        plan = await self.get_organization_plan(db, org_id)
        limits = plan.limits if isinstance(plan.limits, dict) else {}
        features = limits.get("features", {})
        if not features:
            plan_key = plan.name.lower()
            features = PLAN_PRICE_MAP.get(plan_key, {}).get("features", {})

        return {
            "organization_id": str(org_id),
            "plan_name": plan.name,
            "price_monthly": plan.price_monthly,
            "limits": {k: v for k, v in limits.items() if k != "features"},
            "features": features,
        }

    async def has_entitlement(
        self, db: AsyncSession, org_id: uuid.UUID, feature: str
    ) -> bool:
        """Checks whether an organization is entitled to a specific feature flag."""
        entitlements = await self.get_organization_entitlements(db, org_id)
        features = entitlements.get("features", {})
        return bool(features.get(feature, False))

    async def require_entitlement(
        self, db: AsyncSession, org_id: uuid.UUID, feature: str
    ) -> None:
        """Fails closed if the organization does not have the required entitlement."""
        has_it = await self.has_entitlement(db, org_id, feature)
        if not has_it:
            from app.enterprise.exceptions import TenantAccessViolationException

            raise TenantAccessViolationException(
                f"Feature '{feature}' is not enabled for this organization's current plan. Upgrade required."
            )

    async def get_or_create_stripe_customer(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> str:
        """Atomically retrieves or creates a Stripe customer mapping for the organization."""
        stmt = select(Organization).where(Organization.id == org_id).with_for_update()
        try:
            res = await db.execute(stmt)
            org = res.scalar_one_or_none()
        except Exception:
            stmt_fallback = select(Organization).where(Organization.id == org_id)
            res = await db.execute(stmt_fallback)
            org = res.scalar_one_or_none()

        if not org:
            raise BillingGatewayException("Organization not found.")

        if org.stripe_customer_id:
            return org.stripe_customer_id

        stripe_key = self._get_stripe_key()
        if stripe and stripe_key and not stripe_key.startswith("mock_"):
            try:
                customer = stripe.Customer.create(
                    name=org.name,
                    metadata={"organization_id": str(org_id)},
                    idempotency_key=f"cust_create_{org_id}",
                )
                org.stripe_customer_id = customer.id
                await db.commit()
                return customer.id
            except Exception as e:
                logger.error(
                    "Stripe customer creation failed", error=str(e), org_id=str(org_id)
                )
                raise BillingGatewayException(
                    f"Failed to create Stripe customer: {str(e)}"
                ) from e

        # Mock / Test mode customer ID
        mock_cust_id = f"cus_test_{uuid.uuid4().hex[:14]}"
        org.stripe_customer_id = mock_cust_id
        await db.commit()
        return mock_cust_id

    async def create_checkout_session(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        plan_name: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> str:
        """Generates a Stripe Checkout Session URL with server-side price mapping and organization metadata."""
        norm_plan = plan_name.lower()
        if norm_plan not in PLAN_PRICE_MAP:
            raise BillingGatewayException(
                f"Invalid plan name '{plan_name}'. Must be one of {list(PLAN_PRICE_MAP.keys())}."
            )

        # Retrieve organization
        stmt = select(Organization).where(Organization.id == org_id)
        res = await db.execute(stmt)
        org = res.scalar_one_or_none()
        if not org:
            raise BillingGatewayException("Organization not found.")

        target_plan = PLAN_PRICE_MAP[norm_plan]
        fallback_success = (
            success_url or "https://evalforge.com/settings/billing?status=success"
        )
        fallback_cancel = (
            cancel_url or "https://evalforge.com/settings/billing?status=cancelled"
        )

        customer_id = await self.get_or_create_stripe_customer(db, org_id)

        # Free starter tier activates immediately without payment checkout
        if target_plan["price"] == 0.0:
            await self.create_subscription(db, org_id, target_plan["name"])
            return fallback_success

        stripe_key = self._get_stripe_key()
        if stripe and stripe_key and not stripe_key.startswith("mock_"):
            try:
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": f"EvalForge {target_plan['name']} Plan",
                                    "description": f"Enterprise evaluation licensing: {target_plan['limits']['evaluations']} monthly evaluations",
                                },
                                "unit_amount": int(target_plan["price"] * 100),
                                "recurring": {"interval": "month"},
                            },
                            "quantity": 1,
                        }
                    ],
                    mode="subscription",
                    success_url=fallback_success,
                    cancel_url=fallback_cancel,
                    metadata={
                        "organization_id": str(org_id),
                        "plan_name": target_plan["name"],
                    },
                    idempotency_key=f"checkout_{org_id}_{target_plan['name']}_{int(datetime.now(timezone.utc).timestamp() // 60)}",
                )
                return session.url
            except Exception as e:
                logger.error(
                    "Stripe checkout creation failed", error=str(e), org_id=str(org_id)
                )
                raise BillingGatewayException(f"Stripe checkout error: {str(e)}") from e

        # Mock / Test Mode checkout simulation
        mock_session_id = f"cs_test_{uuid.uuid4().hex[:16]}"
        return f"https://checkout.stripe.com/c/pay/{mock_session_id}?org={org_id}&plan={target_plan['name']}"

    def _validate_return_url(self, url: Optional[str]) -> str:
        if not url:
            return "https://evalforge.com/settings/billing"
        clean_url = url.strip()
        lower_url = clean_url.lower()
        if lower_url.startswith(("javascript:", "data:", "file:", "vbscript:")):
            raise BillingGatewayException("Invalid return URL scheme.")
        if not (
            lower_url.startswith("http://")
            or lower_url.startswith("https://")
            or lower_url.startswith("/")
        ):
            raise BillingGatewayException("Invalid return URL format.")
        return clean_url

    async def create_customer_portal_session(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        return_url: Optional[str] = None,
    ) -> str:
        """Generates a Stripe Customer Portal session URL for self-service subscription management."""
        stmt = select(Organization).where(Organization.id == org_id)
        res = await db.execute(stmt)
        org = res.scalar_one_or_none()
        if not org:
            raise BillingGatewayException("Organization not found.")

        validated_return = self._validate_return_url(return_url)
        customer_id = await self.get_or_create_stripe_customer(db, org_id)
        stripe_key = self._get_stripe_key()

        if stripe and stripe_key and not stripe_key.startswith("mock_"):
            try:
                portal_session = stripe.billing_portal.Session.create(
                    customer=customer_id,
                    return_url=validated_return,
                    idempotency_key=f"portal_{org_id}_{int(datetime.now(timezone.utc).timestamp() // 300)}",
                )
                return portal_session.url
            except Exception as e:
                logger.error(
                    "Stripe portal creation failed", error=str(e), org_id=str(org_id)
                )
                raise BillingGatewayException(f"Stripe portal error: {str(e)}") from e

        mock_portal_id = f"bps_test_{uuid.uuid4().hex[:16]}"
        return f"https://billing.stripe.com/p/session/{mock_portal_id}"

    async def process_stripe_webhook(
        self,
        db: AsyncSession,
        payload_bytes: bytes,
        sig_header: Optional[str],
    ) -> Dict[str, Any]:
        """Verifies Stripe HMAC-SHA256 signature, enforces event idempotency, and mutates subscription lifecycle state."""
        webhook_secret = self._get_webhook_secret()
        event = None

        if stripe and webhook_secret and not webhook_secret.startswith("mock_"):
            if not sig_header:
                raise BillingGatewayException("Missing Stripe-Signature header.")
            try:
                event = stripe.Webhook.construct_event(
                    payload_bytes, sig_header, webhook_secret
                )
            except Exception as e:
                logger.error("Invalid Stripe webhook signature", error=str(e))
                raise BillingGatewayException(
                    f"Stripe webhook signature validation failed: {str(e)}"
                ) from e
        else:
            # Fallback JSON parser for simulated/test events
            import json

            try:
                raw_json = json.loads(payload_bytes.decode("utf-8"))
                event = raw_json
            except Exception as e:
                raise BillingGatewayException("Invalid JSON webhook payload.") from e

        event_id = (
            event.get("id") if isinstance(event, dict) else getattr(event, "id", None)
        )
        event_type = (
            event.get("type")
            if isinstance(event, dict)
            else getattr(event, "type", None)
        )
        event_data = (
            event.get("data", {})
            if isinstance(event, dict)
            else getattr(event, "data", {})
        )
        data_object = (
            event_data.get("object", {})
            if isinstance(event_data, dict)
            else getattr(event_data, "object", {})
        )

        if not event_id or not event_type:
            raise BillingGatewayException("Malformed Stripe event object.")

        # 1. Enforce Idempotency
        stmt = select(StripeWebhookEvent).where(StripeWebhookEvent.id == event_id)
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            logger.info(
                "Stripe webhook already processed (idempotent no-op)", event_id=event_id
            )
            return {"status": "idempotent_duplicate", "event_id": event_id}

        try:
            # 2. Record Event
            webhook_record = StripeWebhookEvent(
                id=event_id,
                event_type=event_type,
                payload=data_object if isinstance(data_object, dict) else {},
                processed_at=datetime.now(timezone.utc),
            )
            db.add(webhook_record)

            # 3. State Machine Handler
            if event_type == "checkout.session.completed":
                metadata = data_object.get("metadata", {})
                org_id_str = metadata.get("organization_id")
                plan_name = metadata.get("plan_name", "Pro")
                customer_id = data_object.get("customer")
                subscription_id = data_object.get("subscription")

                if org_id_str:
                    org_uuid = uuid.UUID(org_id_str)
                    if customer_id:
                        org_stmt = select(Organization).where(
                            Organization.id == org_uuid
                        )
                        org_res = await db.execute(org_stmt)
                        org_obj = org_res.scalar_one_or_none()
                        if org_obj:
                            org_obj.stripe_customer_id = customer_id

                    await self.create_subscription(
                        db, org_uuid, plan_name, stripe_subscription_id=subscription_id
                    )
                    logger.info(
                        "Checkout completed: subscription activated",
                        org_id=org_id_str,
                        plan=plan_name,
                    )

            elif event_type in [
                "customer.subscription.updated",
                "customer.subscription.deleted",
            ]:
                stripe_sub_id = data_object.get("id")
                status = data_object.get("status", "active")
                cancel_at_period_end = data_object.get("cancel_at_period_end", False)

                if stripe_sub_id:
                    sub_stmt = select(Subscription).where(
                        Subscription.stripe_subscription_id == stripe_sub_id
                    )
                    sub_res = await db.execute(sub_stmt)
                    sub_obj = sub_res.scalar_one_or_none()
                    if sub_obj:
                        # Out of order defense: If already canceled and event is not deletion, prevent stale reactivation
                        if (
                            sub_obj.status == "canceled"
                            and event_type != "customer.subscription.deleted"
                            and status != "canceled"
                        ):
                            logger.warning(
                                "Ignoring stale subscription update for canceled subscription",
                                stripe_sub_id=stripe_sub_id,
                            )
                        else:
                            if event_type == "customer.subscription.deleted":
                                sub_obj.status = "canceled"
                            else:
                                sub_obj.status = status
                                sub_obj.cancel_at_period_end = cancel_at_period_end

                            await db.commit()
                            logger.info(
                                "Subscription state synchronized",
                                stripe_sub_id=stripe_sub_id,
                                status=sub_obj.status,
                            )

            elif event_type == "invoice.payment_succeeded":
                customer_id = data_object.get("customer")
                amount_paid = float(data_object.get("amount_paid", 0)) / 100.0
                pdf_url = data_object.get("hosted_invoice_url") or data_object.get(
                    "invoice_pdf"
                )

                if customer_id:
                    org_stmt = select(Organization).where(
                        Organization.stripe_customer_id == customer_id
                    )
                    org_res = await db.execute(org_stmt)
                    org_obj = org_res.scalar_one_or_none()
                    if org_obj:
                        invoice = Invoice(
                            id=uuid.uuid4(),
                            organization_id=org_obj.id,
                            amount=amount_paid,
                            status="paid",
                            pdf_url=pdf_url,
                            created_at=datetime.now(timezone.utc),
                        )
                        db.add(invoice)

            elif event_type == "invoice.payment_failed":
                customer_id = data_object.get("customer")
                if customer_id:
                    org_stmt = select(Organization).where(
                        Organization.stripe_customer_id == customer_id
                    )
                    org_res = await db.execute(org_stmt)
                    org_obj = org_res.scalar_one_or_none()
                    if org_obj:
                        sub_stmt = select(Subscription).where(
                            Subscription.organization_id == org_obj.id,
                            Subscription.status == "active",
                        )
                        sub_res = await db.execute(sub_stmt)
                        for sub_item in sub_res.scalars().all():
                            sub_item.status = "past_due"

            await db.commit()
            return {
                "status": "processed",
                "event_id": event_id,
                "event_type": event_type,
            }
        except Exception:
            await db.rollback()
            raise

    async def create_subscription(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        plan_name: str,
        stripe_subscription_id: Optional[str] = None,
    ) -> Subscription:
        """Activates or updates an organization subscription plan with feature/usage limits."""
        stmt = select(Plan).where(sa.func.lower(Plan.name) == plan_name.lower())
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan:
            # Auto-seed plan if not present
            await self.seed_plans(db)
            res2 = await db.execute(stmt)
            plan = res2.scalar_one_or_none()
            if not plan:
                raise BillingGatewayException(f"Plan '{plan_name}' not found.")

        # Deactivate existing active subscriptions
        old_stmt = select(Subscription).where(
            Subscription.organization_id == org_id, Subscription.status == "active"
        )
        old_res = await db.execute(old_stmt)
        for old_sub in old_res.scalars().all():
            old_sub.status = "canceled"

        subscription = Subscription(
            id=uuid.uuid4(),
            organization_id=org_id,
            plan_id=plan.id,
            stripe_subscription_id=stripe_subscription_id,
            status="active",
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            created_at=datetime.now(timezone.utc),
        )
        db.add(subscription)

        invoice = Invoice(
            id=uuid.uuid4(),
            organization_id=org_id,
            amount=plan.price_monthly,
            status="paid",
            pdf_url=f"https://api.evalforge.com/invoices/{uuid.uuid4().hex}.pdf",
            created_at=datetime.now(timezone.utc),
        )
        db.add(invoice)
        await db.commit()
        await db.refresh(subscription)
        return subscription

    async def get_active_subscription(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> Optional[Subscription]:
        """Retrieves the active subscription for an organization."""
        stmt = (
            select(Subscription)
            .where(
                Subscription.organization_id == org_id, Subscription.status == "active"
            )
            .order_by(Subscription.created_at.desc())
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_billing_history(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> List[Invoice]:
        """Retrieves past billing invoices and receipts."""
        stmt = (
            select(Invoice)
            .where(Invoice.organization_id == org_id)
            .order_by(Invoice.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())
