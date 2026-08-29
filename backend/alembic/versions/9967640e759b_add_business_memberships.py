"""add business memberships

Revision ID: 9967640e759b
Revises: 5a6b3bd633ff
Create Date: 2026-08-29 14:18:37.625133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9967640e759b"
down_revision: Union[str, Sequence[str], None] = "5a6b3bd633ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create business membership foundation."""

    op.create_table(
        "business_memberships",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "membership_uid",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "user_uid",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "business_uid",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "membership_uid",
            name=(
                "uq_business_memberships_"
                "membership_uid"
            ),
        ),
        sa.UniqueConstraint(
            "user_uid",
            "business_uid",
            name=(
                "uq_business_memberships_"
                "user_business"
            ),
        ),
    )

    op.create_index(
        "ix_business_memberships_user_uid",
        "business_memberships",
        ["user_uid"],
        unique=False,
    )

    op.create_index(
        "ix_business_memberships_business_uid",
        "business_memberships",
        ["business_uid"],
        unique=False,
    )


def downgrade() -> None:
    """Remove business membership foundation."""

    op.drop_index(
        "ix_business_memberships_business_uid",
        table_name="business_memberships",
    )

    op.drop_index(
        "ix_business_memberships_user_uid",
        table_name="business_memberships",
    )

    op.drop_table(
        "business_memberships"
    )
