"""phase 11 membership unique constraint

Revision ID: h4a5b6c7d8e9
Revises: g3a4b5c6d7e8
Create Date: 2026-09-03 17:15:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h4a5b6c7d8e9"
down_revision: Union[str, Sequence[str], None] = "g3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_memberships_org_user",
        "memberships",
        ["organization_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_memberships_org_user",
        "memberships",
        type_="unique",
    )
