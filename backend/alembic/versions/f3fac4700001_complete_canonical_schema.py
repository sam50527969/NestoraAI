"""complete canonical application schema

Revision ID: f3fac4700001
Revises: 522d2ff063fe
Create Date: 2026-08-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.metadata import metadata


revision: str = "f3fac4700001"
down_revision: Union[str, Sequence[str], None] = "522d2ff063fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FOUNDATIONAL_TABLES = {"leads", "marketing_plans", "missions"}
OPPORTUNITY_COLUMNS = (
    "opportunity_score",
    "estimated_value",
    "closing_probability",
    "business_potential",
    "opportunity_recommendation",
)


def _type_is_compatible(actual: sa.types.TypeEngine, expected: sa.types.TypeEngine) -> bool:
    if actual._type_affinity is not expected._type_affinity:
        return False
    actual_length = getattr(actual, "length", None)
    expected_length = getattr(expected, "length", None)
    return expected_length is None or actual_length == expected_length


def _unique_column_sets(inspector: sa.Inspector, table_name: str) -> set[frozenset[str]]:
    unique = {
        frozenset(item["column_names"])
        for item in inspector.get_unique_constraints(table_name)
        if item.get("column_names")
    }
    unique.update(
        frozenset(item["column_names"])
        for item in inspector.get_indexes(table_name)
        if item.get("unique") and item.get("column_names")
    )
    return unique


def _validate_existing_table(
    inspector: sa.Inspector,
    table_name: str,
    allowed_missing: set[str] | None = None,
) -> None:
    allowed_missing = allowed_missing or set()
    expected = metadata.tables[table_name]
    actual = {
        column["name"]: column
        for column in inspector.get_columns(table_name)
    }
    problems: list[str] = []
    for column in expected.columns:
        found = actual.get(column.name)
        if found is None:
            if column.name not in allowed_missing:
                problems.append(f"missing column {column.name}")
            continue
        if not _type_is_compatible(found["type"], column.type):
            problems.append(f"incompatible type for {column.name}")
        if found["nullable"] != column.nullable:
            problems.append(f"incompatible nullability for {column.name}")

    actual_pk = set(inspector.get_pk_constraint(table_name)["constrained_columns"])
    expected_pk = set(expected.primary_key.columns.keys())
    if actual_pk != expected_pk:
        problems.append("incompatible primary key")

    actual_unique = _unique_column_sets(inspector, table_name)
    expected_unique = {
        frozenset(constraint.columns.keys())
        for constraint in expected.constraints
        if isinstance(constraint, sa.UniqueConstraint)
    }
    expected_unique.update(
        frozenset(index.columns.keys())
        for index in expected.indexes
        if index.unique
    )
    missing_unique = expected_unique - actual_unique
    if missing_unique:
        problems.append(
            "missing uniqueness for "
            + ", ".join(sorted("/".join(sorted(columns)) for columns in missing_unique))
        )

    if problems:
        raise RuntimeError(
            f"Incompatible existing {table_name} schema: " + "; ".join(problems)
        )


def upgrade() -> None:
    """Preflight, then converge safely to all 16 canonical tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    missing_foundational = FOUNDATIONAL_TABLES - existing
    if missing_foundational:
        raise RuntimeError(
            "Migration stamp is contradictory; required tables are missing: "
            + ", ".join(sorted(missing_foundational))
        )

    # Complete every validation before issuing the first schema change.
    for table_name in sorted(existing.intersection(metadata.tables)):
        allowed_missing = (
            set(OPPORTUNITY_COLUMNS) if table_name == "leads" else set()
        )
        _validate_existing_table(inspector, table_name, allowed_missing)

    leads = metadata.tables["leads"]
    lead_columns = {column["name"] for column in inspector.get_columns("leads")}
    for column_name in OPPORTUNITY_COLUMNS:
        if column_name not in lead_columns:
            op.add_column("leads", leads.c[column_name]._copy())

    for table_name in sorted(set(metadata.tables) - existing):
        metadata.tables[table_name].to_metadata(sa.MetaData()).create(bind)


def downgrade() -> None:
    """Refuse destructive schema removal."""
    raise RuntimeError(
        "Downgrade is intentionally unsupported because it would delete application data."
    )
