"""add executive memory workspace ownership

Revision ID: 5944b6379386
Revises: a41c8e7d2b90
Create Date: 2026-09-05 14:02:17.653020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5944b6379386"
down_revision: Union[str, Sequence[str], None] = "a41c8e7d2b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add workspace ownership to executive memory.

    Existing rows intentionally remain NULL because their original
    workspace ownership cannot be inferred safely.
    """
    op.add_column(
        "executive_memory",
        sa.Column(
            "business_uid",
            sa.String(),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_executive_memory_business_uid",
        "executive_memory",
        ["business_uid"],
        unique=False,
    )


def downgrade() -> None:
    """Remove workspace ownership from executive memory."""
    op.drop_index(
        "ix_executive_memory_business_uid",
        table_name="executive_memory",
    )
    op.drop_column(
        "executive_memory",
        "business_uid",
    )
