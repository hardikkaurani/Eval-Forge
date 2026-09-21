"""add workspace_id to projects

Revision ID: f1a2b3c4d5e6
Revises: e7f8a1b2c3d4
Create Date: 2026-08-29 17:35:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e7f8a1b2c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema by adding nullable workspace_id column, index, and foreign key constraint to projects table."""
    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(
            sa.Column("workspace_id", sa.String(length=36), nullable=True)
        )
        batch_op.create_index(
            op.f("ix_projects_workspace_id"), ["workspace_id"], unique=False
        )
        batch_op.create_foreign_key(
            "fk_projects_workspace_id_workspaces",
            "workspaces",
            ["workspace_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    """Downgrade schema by removing workspace_id foreign key, index, and column from projects table."""
    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_constraint(
            "fk_projects_workspace_id_workspaces", type_="foreignkey"
        )
        batch_op.drop_index(op.f("ix_projects_workspace_id"))
        batch_op.drop_column("workspace_id")
