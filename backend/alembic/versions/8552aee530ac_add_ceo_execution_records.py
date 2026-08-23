"""add ceo execution records

Revision ID: 8552aee530ac
Revises: 522d2ff063fe
Create Date: 2026-08-23 23:23:23.210036
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8552aee530ac"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "522d2ff063fe"
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


TABLE_NAME = "ceo_execution_records"


def upgrade() -> None:
    """Create persistent CEO execution history."""
    op.create_table(
        TABLE_NAME,
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "execution_uid",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "approval_uid",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "mission_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "workflow_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "objective",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "success",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "completed_task_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "failed_task_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "result_json",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
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
    )

    op.create_index(
        "ix_ceo_execution_records_id",
        TABLE_NAME,
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_ceo_execution_records_execution_uid",
        TABLE_NAME,
        ["execution_uid"],
        unique=True,
    )

    op.create_index(
        "ix_ceo_execution_records_approval_uid",
        TABLE_NAME,
        ["approval_uid"],
        unique=False,
    )

    op.create_index(
        "ix_ceo_execution_records_mission_id",
        TABLE_NAME,
        ["mission_id"],
        unique=False,
    )

    op.create_index(
        "ix_ceo_execution_records_workflow_id",
        TABLE_NAME,
        ["workflow_id"],
        unique=False,
    )

    op.create_index(
        "ix_ceo_execution_records_status",
        TABLE_NAME,
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_ceo_execution_records_success",
        TABLE_NAME,
        ["success"],
        unique=False,
    )

    op.create_index(
        "ix_ceo_execution_records_created_at",
        TABLE_NAME,
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove persistent CEO execution history."""
    op.drop_index(
        "ix_ceo_execution_records_created_at",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_success",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_status",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_workflow_id",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_mission_id",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_approval_uid",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_execution_uid",
        table_name=TABLE_NAME,
    )
    op.drop_index(
        "ix_ceo_execution_records_id",
        table_name=TABLE_NAME,
    )

    op.drop_table(TABLE_NAME)