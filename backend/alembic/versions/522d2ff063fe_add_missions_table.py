"""add missions table

Revision ID: 522d2ff063fe
Revises: 687dc4717df8
Create Date: 2026-07-26 14:57:18.305338
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "522d2ff063fe"
down_revision: Union[str, Sequence[str], None] = "687dc4717df8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the missions table."""

    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_uid", sa.String(), nullable=False),
        sa.Column("business_uid", sa.String(), nullable=False),
        sa.Column("objective_uid", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("estimated_value", sa.Float(), nullable=True),
        sa.Column("expected_roi", sa.Float(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("strategy_data", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_missions_business_uid"),
        "missions",
        ["business_uid"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_created_at"),
        "missions",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_id"),
        "missions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_mission_uid"),
        "missions",
        ["mission_uid"],
        unique=True,
    )

    op.create_index(
        op.f("ix_missions_objective_uid"),
        "missions",
        ["objective_uid"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_priority"),
        "missions",
        ["priority"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_status"),
        "missions",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_title"),
        "missions",
        ["title"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the missions table."""

    op.drop_index(
        op.f("ix_missions_title"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_status"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_priority"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_objective_uid"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_mission_uid"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_id"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_created_at"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_business_uid"),
        table_name="missions",
    )

    op.drop_table("missions")