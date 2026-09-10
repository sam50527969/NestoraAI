"""add lead contact email

Revision ID: 20ca0f3c9d21
Revises: 7c8e9f1a2b3c
Create Date: 2026-09-10 08:47:17.059157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20ca0f3c9d21'
down_revision: Union[str, Sequence[str], None] = '7c8e9f1a2b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("leads") as batch_op:
        batch_op.add_column(
            sa.Column(
                "email",
                sa.String(),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("leads") as batch_op:
        batch_op.drop_column("email")
