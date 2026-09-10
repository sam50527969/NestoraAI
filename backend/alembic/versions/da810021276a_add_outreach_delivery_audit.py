"""add outreach delivery audit

Revision ID: da810021276a
Revises: 20ca0f3c9d21
Create Date: 2026-09-10 09:00:39.149739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da810021276a'
down_revision: Union[str, Sequence[str], None] = '20ca0f3c9d21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table(
        "outreach_activities"
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "delivery_channel",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "delivery_recipient",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "delivery_provider",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "provider_message_id",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "delivery_attempted_at",
                sa.DateTime(),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table(
        "outreach_activities"
    ) as batch_op:
        batch_op.drop_column(
            "delivery_attempted_at"
        )
        batch_op.drop_column(
            "provider_message_id"
        )
        batch_op.drop_column(
            "delivery_provider"
        )
        batch_op.drop_column(
            "delivery_recipient"
        )
        batch_op.drop_column(
            "delivery_channel"
        )
