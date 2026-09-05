"""Add executive communication workspace ownership.

Revision ID: 7c8e9f1a2b3c
Revises: 5944b6379386
"""

from alembic import op
import sqlalchemy as sa


revision = "7c8e9f1a2b3c"
down_revision = "5944b6379386"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("executive_messages") as batch_op:
        batch_op.add_column(
            sa.Column(
                "business_uid",
                sa.String(length=64),
                nullable=True,
            )
        )
        batch_op.create_index(
            "ix_executive_messages_business_uid",
            ["business_uid"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("executive_messages") as batch_op:
        batch_op.drop_index(
            "ix_executive_messages_business_uid"
        )
        batch_op.drop_column("business_uid")