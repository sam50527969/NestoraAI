"""add universal business context

Revision ID: b358ef0851c3
Revises: 8552aee530ac
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b358ef0851c3"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "8552aee530ac"
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


TABLE_NAME = "businesses"


def upgrade() -> None:
    """Add universal location and localization context."""

    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.add_column(
            sa.Column(
                "city",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "region",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "timezone",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "locale",
                sa.String(),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Remove universal location and localization context."""

    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.drop_column("locale")
        batch_op.drop_column("timezone")
        batch_op.drop_column("region")
        batch_op.drop_column("city")
