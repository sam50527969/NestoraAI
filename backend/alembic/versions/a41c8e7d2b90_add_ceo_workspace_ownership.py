"""add CEO workspace ownership

Revision ID: a41c8e7d2b90
Revises: 9967640e759b
Create Date: 2026-09-04

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a41c8e7d2b90"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "9967640e759b"
branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None
depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """
    Add workspace ownership to CEO approval and
    execution-history records.

    Existing records intentionally remain NULL.
    Their ownership cannot be inferred safely.
    """

    op.add_column(
        "ceo_approvals",
        sa.Column(
            "business_uid",
            sa.String(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_ceo_approvals_business_uid",
        "ceo_approvals",
        ["business_uid"],
        unique=False,
    )

    op.add_column(
        "ceo_execution_records",
        sa.Column(
            "business_uid",
            sa.String(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_ceo_execution_records_business_uid",
        "ceo_execution_records",
        ["business_uid"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ceo_execution_records_business_uid",
        table_name="ceo_execution_records",
    )

    op.drop_column(
        "ceo_execution_records",
        "business_uid",
    )

    op.drop_index(
        "ix_ceo_approvals_business_uid",
        table_name="ceo_approvals",
    )

    op.drop_column(
        "ceo_approvals",
        "business_uid",
    )
