"""add marketing plans table

Revision ID: 687dc4717df8
Revises: c5d8d829c5b8
Create Date: 2026-07-19 11:45:47.202765
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.metadata import metadata


revision: str = "687dc4717df8"
down_revision: Union[str, Sequence[str], None] = "c5d8d829c5b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OPPORTUNITY_COLUMNS = {
    "opportunity_score", "estimated_value", "closing_probability",
    "business_potential", "opportunity_recommendation",
}


def _validate_table(inspector: sa.Inspector, name: str) -> None:
    expected = metadata.tables[name]
    actual = {column["name"]: column for column in inspector.get_columns(name)}
    for column in expected.columns:
        found = actual.get(column.name)
        if found is None or found["type"]._type_affinity is not column.type._type_affinity:
            raise RuntimeError(f"Incompatible existing {name}.{column.name} column.")
        if found["nullable"] != column.nullable:
            raise RuntimeError(f"Incompatible nullability for {name}.{column.name}.")
    if set(inspector.get_pk_constraint(name)["constrained_columns"]) != set(
        expected.primary_key.columns.keys()
    ):
        raise RuntimeError(f"Incompatible primary key for {name}.")


def _preflight_existing_tables(inspector: sa.Inspector) -> None:
    for name in set(inspector.get_table_names()).intersection(metadata.tables):
        expected = metadata.tables[name]
        actual = {item["name"]: item for item in inspector.get_columns(name)}
        allowed = OPPORTUNITY_COLUMNS if name == "leads" else set()
        problems = []
        for column in expected.columns:
            found = actual.get(column.name)
            if found is None:
                if column.name not in allowed:
                    problems.append(f"missing {column.name}")
            elif (
                found["type"]._type_affinity is not column.type._type_affinity
                or found["nullable"] != column.nullable
            ):
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
    """Create marketing_plans or validate a compatible existing table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "leads" not in inspector.get_table_names():
        raise RuntimeError("Migration stamp is contradictory: leads is missing.")
    _preflight_existing_tables(inspector)
    if "marketing_plans" in inspector.get_table_names():
        _validate_table(inspector, "marketing_plans")
        return
    metadata.tables["marketing_plans"].to_metadata(sa.MetaData()).create(bind)


def downgrade() -> None:
    """Downgrade is intentionally non-destructive."""
    raise RuntimeError("Downgrade is unsupported because it would delete plan data.")
