"""add business ownership to leads

Revision ID: 5a6b3bd633ff
Revises: b358ef0851c3
Create Date: 2026-08-29 14:09:35.995834

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a6b3bd633ff"
down_revision: Union[str, Sequence[str], None] = "b358ef0851c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add optional business ownership to CRM leads."""

    with op.batch_alter_table("leads") as batch_op:
        batch_op.add_column(
            sa.Column(
                "business_uid",
                sa.String(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_leads_business_uid",
            ["business_uid"],
            unique=False,
        )


def downgrade() -> None:
    """Remove CRM lead business ownership."""

    with op.batch_alter_table("leads") as batch_op:
        batch_op.drop_index(
            "ix_leads_business_uid"
        )

        batch_op.drop_column(
            "business_uid"
        )
