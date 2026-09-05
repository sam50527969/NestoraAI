"""create leads table

Revision ID: d22c6b17208a
Revises:
Create Date: 2026-07-06 01:42:06.125802
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.metadata import metadata


revision: str = "d22c6b17208a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AI_COLUMNS = {
    "ai_score", "ai_recommendation", "ai_opportunity", "ai_strengths",
    "ai_weaknesses", "ai_analyzed_at",
}
OPPORTUNITY_COLUMNS = {
    "opportunity_score", "estimated_value", "closing_probability",
    "business_potential", "opportunity_recommendation",
}
APPLICATION_TABLES = set(metadata.tables)


def _copy_column(column: sa.Column) -> sa.Column:
    return column._copy()  # SQLAlchemy's internal copy preserves the DDL snapshot.


def _reject_unversioned_application_schema(inspector: sa.Inspector) -> None:
    existing = APPLICATION_TABLES.intersection(inspector.get_table_names())
    if existing:
        names = ", ".join(sorted(existing))
        raise RuntimeError(
            "Refusing to migrate an unversioned database containing application "
            f"tables: {names}. Review and stamp it manually before migration."
        )


def upgrade() -> None:
    """Create the historical, pre-AI leads schema on a fresh database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    _reject_unversioned_application_schema(inspector)

    source = metadata.tables["leads"]
    excluded = AI_COLUMNS | OPPORTUNITY_COLUMNS
    table_metadata = sa.MetaData()
    leads = sa.Table(
        "leads",
        table_metadata,
        *[_copy_column(column) for column in source.columns if column.name not in excluded],
    )
    leads.create(bind)


def downgrade() -> None:
    """Downgrade is intentionally non-destructive."""
    raise RuntimeError("Downgrade is unsupported because it would delete lead data.")
