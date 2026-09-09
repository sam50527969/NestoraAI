"""add missions table

Revision ID: 522d2ff063fe
Revises: 687dc4717df8
Create Date: 2026-07-26 14:57:18.305338
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.metadata import metadata


# revision identifiers, used by Alembic.
revision: str = "522d2ff063fe"
down_revision: Union[str, Sequence[str], None] = "687dc4717df8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OPPORTUNITY_COLUMNS = {
    "opportunity_score", "estimated_value", "closing_probability",
    "business_potential", "opportunity_recommendation",
}


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
    """Create the missions table."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "leads" not in tables or "marketing_plans" not in tables:
        raise RuntimeError(
            "Migration stamp is contradictory: leads or marketing_plans is missing."
        )
    _preflight_existing_tables(inspector)
    if "missions" in tables:
        expected = metadata.tables["missions"]
        actual = {
            column["name"]: column
            for column in inspector.get_columns("missions")
        }
        for column in expected.columns:
            found = actual.get(column.name)
            if (
                found is None
                or found["type"]._type_affinity is not column.type._type_affinity
                or found["nullable"] != column.nullable
            ):
                raise RuntimeError(
                    f"Incompatible existing missions.{column.name} column."
                )
        return

    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_uid", sa.String(), nullable=False),
        sa.Column("business_uid", sa.String(), nullable=False),
        sa.Column("objective_uid", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("estimated_value", sa.Float(), nullable=True),
        sa.Column("expected_roi", sa.Float(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("strategy_data", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_missions_business_uid"),
        "missions",
        ["business_uid"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_created_at"),
        "missions",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_id"),
        "missions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_mission_uid"),
        "missions",
        ["mission_uid"],
        unique=True,
    )

    op.create_index(
        op.f("ix_missions_objective_uid"),
        "missions",
        ["objective_uid"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_priority"),
        "missions",
        ["priority"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_status"),
        "missions",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_missions_title"),
        "missions",
        ["title"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the missions table."""

    op.drop_index(
        op.f("ix_missions_title"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_status"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_priority"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_objective_uid"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_mission_uid"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_id"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_created_at"),
        table_name="missions",
    )

    op.drop_index(
        op.f("ix_missions_business_uid"),
        table_name="missions",
    )

    op.drop_table("missions")