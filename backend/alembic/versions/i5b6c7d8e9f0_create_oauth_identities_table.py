"""create oauth identities table

Revision ID: i5b6c7d8e9f0
Revises: h4a5b6c7d8e9
Create Date: 2026-09-20 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "i5b6c7d8e9f0"
down_revision: Union[str, Sequence[str], None] = "h4a5b6c7d8e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "oauth_identities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_oauth_identities_provider_user",
        ),
    )
    op.create_index("ix_oauth_identities_user_id", "oauth_identities", ["user_id"])
    op.create_index(
        "ix_oauth_identities_provider_user_id",
        "oauth_identities",
        ["provider_user_id"],
    )
    op.create_index("ix_oauth_identities_email", "oauth_identities", ["email"])


def downgrade() -> None:
    op.drop_index("ix_oauth_identities_email", table_name="oauth_identities")
    op.drop_index(
        "ix_oauth_identities_provider_user_id", table_name="oauth_identities"
    )
    op.drop_index("ix_oauth_identities_user_id", table_name="oauth_identities")
    op.drop_table("oauth_identities")
