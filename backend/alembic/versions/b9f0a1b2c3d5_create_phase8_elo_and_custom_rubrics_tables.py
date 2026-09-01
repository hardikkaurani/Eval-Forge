"""create phase8 elo and custom rubrics tables

Revision ID: b9f0a1b2c3d5
Revises: a7f8e9c0b1d2
Create Date: 2026-09-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9f0a1b2c3d5"
down_revision: Union[str, Sequence[str], None] = "a7f8e9c0b1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. model_elo_ratings
    op.create_table(
        "model_elo_ratings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False, server_default="1500.0"),
        sa.Column("matches_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("draws", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_model_elo_ratings_project_id",
        "model_elo_ratings",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_model_elo_ratings_id", "model_elo_ratings", ["id"], unique=False
    )

    # 2. custom_rubrics
    op.create_table(
        "custom_rubrics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("rubric_key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("scoring_scale", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("prompt_template", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_custom_rubrics_project_id", "custom_rubrics", ["project_id"], unique=False
    )
    op.create_index(
        "ix_custom_rubrics_rubric_key", "custom_rubrics", ["rubric_key"], unique=False
    )
    op.create_index("ix_custom_rubrics_id", "custom_rubrics", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_custom_rubrics_id", table_name="custom_rubrics")
    op.drop_index("ix_custom_rubrics_rubric_key", table_name="custom_rubrics")
    op.drop_index("ix_custom_rubrics_project_id", table_name="custom_rubrics")
    op.drop_table("custom_rubrics")

    op.drop_index("ix_model_elo_ratings_id", table_name="model_elo_ratings")
    op.drop_index("ix_model_elo_ratings_project_id", table_name="model_elo_ratings")
    op.drop_table("model_elo_ratings")
