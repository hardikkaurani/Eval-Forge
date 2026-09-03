"""create webhook outbox and harden plugins
Revision ID: f2a3b4c5d6e7
Revises: f1a2b3c4d5e6, b9f0a1b2c3d5
Create Date: 2026-09-03 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = ("f1a2b3c4d5e6", "b9f0a1b2c3d5")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create webhook_outbox_events table
    op.create_table(
        "webhook_outbox_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_webhook_outbox_events_id"),
        "webhook_outbox_events",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_webhook_outbox_events_project_id"),
        "webhook_outbox_events",
        ["project_id"],
        unique=False,
    )

    # 2. Add capabilities, workspace_id, is_global to plugin_descriptors
    op.add_column(
        "plugin_descriptors",
        sa.Column("capabilities", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "plugin_descriptors",
        sa.Column("workspace_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "plugin_descriptors",
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index(
        op.f("ix_plugin_descriptors_workspace_id"),
        "plugin_descriptors",
        ["workspace_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_plugin_descriptors_workspace_id_workspaces",
        "plugin_descriptors",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_plugin_descriptors_workspace_id_workspaces",
        "plugin_descriptors",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_plugin_descriptors_workspace_id"),
        table_name="plugin_descriptors",
    )
    op.drop_column("plugin_descriptors", "is_global")
    op.drop_column("plugin_descriptors", "workspace_id")
    op.drop_column("plugin_descriptors", "capabilities")

    op.drop_index(
        op.f("ix_webhook_outbox_events_project_id"),
        table_name="webhook_outbox_events",
    )
    op.drop_index(
        op.f("ix_webhook_outbox_events_id"),
        table_name="webhook_outbox_events",
    )
    op.drop_table("webhook_outbox_events")
