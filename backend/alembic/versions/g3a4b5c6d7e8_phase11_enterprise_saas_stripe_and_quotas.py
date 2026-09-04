"""phase 11 enterprise saas stripe and quotas

Revision ID: g3a4b5c6d7e8
Revises: f2a3b4c5d6e7
Create Date: 2026-09-03 15:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend organizations with stripe_customer_id
    op.add_column(
        "organizations",
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_organizations_stripe_customer_id"),
        "organizations",
        ["stripe_customer_id"],
        unique=True,
    )

    # 2. Extend plans with stripe_price_id
    op.add_column(
        "plans",
        sa.Column("stripe_price_id", sa.String(length=255), nullable=True),
    )

    # 3. Extend subscriptions with stripe attributes
    op.add_column(
        "subscriptions",
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_subscriptions_stripe_subscription_id"),
        "subscriptions",
        ["stripe_subscription_id"],
        unique=True,
    )
    op.add_column(
        "subscriptions",
        sa.Column("stripe_price_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    # 4. Create stripe_webhook_events table
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("stripe_webhook_events")

    op.drop_column("subscriptions", "cancel_at_period_end")
    op.drop_column("subscriptions", "stripe_price_id")
    op.drop_index(
        op.f("ix_subscriptions_stripe_subscription_id"),
        table_name="subscriptions",
    )
    op.drop_column("subscriptions", "stripe_subscription_id")

    op.drop_column("plans", "stripe_price_id")

    op.drop_index(
        op.f("ix_organizations_stripe_customer_id"),
        table_name="organizations",
    )
    op.drop_column("organizations", "stripe_customer_id")
