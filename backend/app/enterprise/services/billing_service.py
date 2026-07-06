import uuid
from datetime import datetime, timedelta
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.exceptions import BillingGatewayException
from app.enterprise.models import Invoice, Plan, Subscription


class BillingProviderConnector:
    """Interface abstraction for Stripe, Paddle, Lemon Squeezy, etc."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    async def create_checkout_session(self, org_id: str, plan_name: str) -> str:
        # Mock payment gateway checkout URL generation
        return f"https://checkout.{self.provider_name}.com/sessions/mock_{uuid.uuid4().hex}"

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True


class BillingService:
    """Manages SaaS plans, active subscription cycles, invoices, and integrates payment providers."""

    def __init__(self):
        # Default providers mapping
        self.connectors = {
            "stripe": BillingProviderConnector("stripe"),
            "paddle": BillingProviderConnector("paddle"),
            "lemonsqueezy": BillingProviderConnector("lemonsqueezy"),
        }

    async def get_connector(self, provider: str) -> BillingProviderConnector:
        connector = self.connectors.get(provider.lower())
        if not connector:
            raise BillingGatewayException(f"Unsupported billing provider: {provider}")
        return connector

    async def seed_plans(self, db: AsyncSession) -> None:
        """Seeds default Starter, Pro, Team, Business, and Enterprise plans."""
        plans_data = [
            {
                "name": "Starter",
                "price": 0.0,
                "limits": {"api_requests": 1000, "storage_mb": 100, "evaluations": 100},
            },
            {
                "name": "Pro",
                "price": 49.0,
                "limits": {
                    "api_requests": 10000,
                    "storage_mb": 1000,
                    "evaluations": 1000,
                },
            },
            {
                "name": "Team",
                "price": 149.0,
                "limits": {
                    "api_requests": 50000,
                    "storage_mb": 5000,
                    "evaluations": 5000,
                },
            },
            {
                "name": "Business",
                "price": 499.0,
                "limits": {
                    "api_requests": 250000,
                    "storage_mb": 25000,
                    "evaluations": 25000,
                },
            },
            {
                "name": "Enterprise",
                "price": 1499.0,
                "limits": {
                    "api_requests": 1000000,
                    "storage_mb": 100000,
                    "evaluations": 100000,
                },
            },
        ]

        for p in plans_data:
            stmt = select(Plan).where(Plan.name == p["name"])
            existing = await db.execute(stmt)
            if not existing.scalar_one_or_none():
                plan = Plan(
                    id=uuid.uuid4(),
                    name=p["name"],
                    price_monthly=p["price"],
                    limits=p["limits"],
                    created_at=datetime.utcnow(),
                )
                db.add(plan)
        await db.commit()

    async def create_subscription(
        self, db: AsyncSession, org_id: uuid.UUID, plan_name: str
    ) -> Subscription:
        # Fetch the plan
        stmt = select(Plan).where(sa.func.lower(Plan.name) == plan_name.lower())
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan:
            raise BillingGatewayException(f"Plan '{plan_name}' not found.")

        # Deactivate previous active subscription if exists
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
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            created_at=datetime.utcnow(),
        )
        db.add(subscription)

        # Create an invoice
        invoice = Invoice(
            id=uuid.uuid4(),
            organization_id=org_id,
            amount=plan.price_monthly,
            status="paid",
            pdf_url=f"https://api.evalforge.com/invoices/{uuid.uuid4().hex}.pdf",
            created_at=datetime.utcnow(),
        )
        db.add(invoice)
        await db.commit()
        await db.refresh(subscription)
        return subscription

    async def get_billing_history(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> List[Invoice]:
        stmt = (
            select(Invoice)
            .where(Invoice.organization_id == org_id)
            .order_by(Invoice.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())
