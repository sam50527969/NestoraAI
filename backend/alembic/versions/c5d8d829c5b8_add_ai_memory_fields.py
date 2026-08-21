"""add ai memory fields

Revision ID: c5d8d829c5b8
Revises: d22c6b17208a
Create Date: 2026-07-11 15:14:30.518154
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.metadata import metadata


revision: str = "c5d8d829c5b8"
down_revision: Union[str, Sequence[str], None] = "d22c6b17208a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AI_COLUMNS = (
    "ai_score", "ai_recommendation", "ai_opportunity", "ai_strengths",
    "ai_weaknesses", "ai_analyzed_at",
)
OPPORTUNITY_COLUMNS = {
    "opportunity_score", "estimated_value", "closing_probability",
    "business_potential", "opportunity_recommendation",
}


def _compatible(actual: dict, expected: sa.Column) -> bool:
    return (
        actual["type"]._type_affinity is expected.type._type_affinity
        and actual["nullable"] == expected.nullable
    )


def _preflight_existing_tables(inspector: sa.Inspector) -> None:
    for name in set(inspector.get_table_names()).intersection(metadata.tables):
        expected = metadata.tables[name]
        actual = {item["name"]: item for item in inspector.get_columns(name)}
        allowed = (set(AI_COLUMNS) | OPPORTUNITY_COLUMNS) if name == "leads" else set()
        problems = []
        for column in expected.columns:
            found = actual.get(column.name)
            if found is None:
                if column.name not in allowed:
                    problems.append(f"missing {column.name}")
            elif not _compatible(found, column):
                problems.append(f"incompatible {column.name}")
        if set(inspector.get_pk_constraint(name)["constrained_columns"]) != set(
            expected.primary_key.columns.keys()
        ):
            problems.append("incompatible primary key")
        actual_unique = {
            frozenset(item["column_names"])
            for item in inspector.get_unique_constraints(name) + inspector.get_indexes(name)
            if item.get("column_names") and item.get("unique")
        }
        expected_unique = {
            frozenset(item.columns.keys())
            for item in expected.constraints.union(expected.indexes)
            if isinstance(item, sa.UniqueConstraint)
            or (isinstance(item, sa.Index) and item.unique)
        }
        if expected_unique - actual_unique:
            problems.append("missing required uniqueness")
        if problems:
            raise RuntimeError(
                f"Incompatible existing {name} schema: " + "; ".join(problems)
            )


def upgrade() -> None:
    """Add only missing nullable AI fields to a valid leads table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "leads" not in inspector.get_table_names():
        raise RuntimeError(
            "Migration stamp is contradictory: d22c6b17208a is applied but "
            "the leads table is missing."
        )
    _preflight_existing_tables(inspector)
    actual = {column["name"]: column for column in inspector.get_columns("leads")}
    expected = metadata.tables["leads"]
    for name in AI_COLUMNS:
        column = expected.c[name]
        if name in actual:
            if not _compatible(actual[name], column):
                raise RuntimeError(f"Incompatible existing leads.{name} column.")
            continue
        op.add_column("leads", column._copy())


def downgrade() -> None:
    """Downgrade is intentionally non-destructive."""
    raise RuntimeError("Downgrade is unsupported because it would delete lead data.")
