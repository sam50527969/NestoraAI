import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, inspect, text

from app.database.metadata import metadata


BACKEND = Path(__file__).resolve().parent
HISTORICAL_REVISIONS = (
    "d22c6b17208a",
    "c5d8d829c5b8",
    "687dc4717df8",
    "522d2ff063fe",
)
EXPECTED_TABLES = set(metadata.tables)


def database_url(path: Path) -> str:
    return f"sqlite:///{path}"


def alembic(path: Path, *arguments: str, succeeds: bool = True):
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url(path)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if succeeds and result.returncode:
        pytest.fail(result.stdout + result.stderr)
    if not succeeds and not result.returncode:
        pytest.fail("Alembic unexpectedly succeeded")
    return result


def application_tables(path: Path) -> set[str]:
    return set(inspect(create_engine(database_url(path))).get_table_names()) - {
        "alembic_version"
    }


def current_revision(path: Path) -> str | None:
    engine = create_engine(database_url(path))
    with engine.connect() as connection:
        if "alembic_version" not in inspect(connection).get_table_names():
            return None
        return connection.scalar(text("SELECT version_num FROM alembic_version"))


def assert_column_parity(path: Path) -> None:
    inspector = inspect(create_engine(database_url(path)))
    for table_name, table in metadata.tables.items():
        actual = {
            column["name"]: column
            for column in inspector.get_columns(table_name)
        }
        assert set(actual) == set(table.columns.keys()), table_name
        for expected in table.columns:
            found = actual[expected.name]
            assert found["type"]._type_affinity is expected.type._type_affinity
            assert found["nullable"] == expected.nullable
        assert set(inspector.get_pk_constraint(table_name)["constrained_columns"]) == set(
            table.primary_key.columns.keys()
        )


def test_fresh_database_migrates_to_all_canonical_tables(tmp_path):
    path = tmp_path / "fresh.db"
    alembic(path, "upgrade", "head")

    assert application_tables(path) == EXPECTED_TABLES
    assert len(application_tables(path)) == 16
    assert current_revision(path) == "f3fac4700001"
    assert_column_parity(path)


@pytest.mark.parametrize("revision", HISTORICAL_REVISIONS)
def test_every_historical_revision_upgrades_to_head(tmp_path, revision):
    path = tmp_path / f"{revision}.db"
    alembic(path, "upgrade", revision)
    assert current_revision(path) == revision

    alembic(path, "upgrade", "head")

    assert application_tables(path) == EXPECTED_TABLES
    assert current_revision(path) == "f3fac4700001"


def test_existing_lead_data_is_preserved(tmp_path):
    path = tmp_path / "populated.db"
    alembic(path, "upgrade", "c5d8d829c5b8")
    engine = create_engine(database_url(path))
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO leads "
                "(id, name, status, priority, notes, created_at, updated_at) "
                "VALUES (7, 'Preserved', 'New', 'High', 'keep me', "
                "'2026-01-01 00:00:00', '2026-01-02 00:00:00')"
            )
        )

    alembic(path, "upgrade", "head")

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT id, name, status, priority, notes, created_at, updated_at "
                "FROM leads WHERE id = 7"
            )
        ).mappings().one()
        assert dict(row) == {
            "id": 7,
            "name": "Preserved",
            "status": "New",
            "priority": "High",
            "notes": "keep me",
            "created_at": "2026-01-01 00:00:00",
            "updated_at": "2026-01-02 00:00:00",
        }


@pytest.mark.parametrize("revision", HISTORICAL_REVISIONS)
def test_compatible_create_all_schema_and_data_are_preserved(tmp_path, revision):
    path = tmp_path / f"compatible-{revision}.db"
    alembic(path, "upgrade", revision)
    engine = create_engine(database_url(path))
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            metadata.tables["users"].insert().values(
                id=3,
                user_uid="usr_preserved",
                email="preserved@example.test",
                full_name="Preserved User",
                password_hash="not-a-real-secret",
                role="user",
                is_active=True,
            )
        )
        connection.execute(
            metadata.tables["businesses"].insert().values(
                id=4,
                business_uid="biz_preserved",
                name="Preserved Business",
                industry="Testing",
                country="QA",
            )
        )

    alembic(path, "upgrade", "head")

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT email FROM users WHERE id=3")) == (
            "preserved@example.test"
        )
        assert connection.scalar(text("SELECT name FROM businesses WHERE id=4")) == (
            "Preserved Business"
        )
    assert application_tables(path) == EXPECTED_TABLES


def test_unversioned_database_with_application_data_is_rejected(tmp_path):
    path = tmp_path / "unversioned.db"
    engine = create_engine(database_url(path))
    metadata.tables["users"].create(engine)
    with engine.begin() as connection:
        connection.execute(
            metadata.tables["users"].insert().values(
                id=9,
                user_uid="usr_unversioned",
                email="unversioned@example.test",
                full_name="Existing User",
                password_hash="test-only",
            )
        )

    result = alembic(path, "upgrade", "head", succeeds=False)

    assert "Refusing to migrate an unversioned database" in result.stderr
    assert application_tables(path) == {"users"}
    assert current_revision(path) is None
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM users")) == 1


def test_contradictory_stamp_is_rejected_without_revision_change(tmp_path):
    path = tmp_path / "contradictory.db"
    alembic(path, "stamp", "d22c6b17208a")

    result = alembic(path, "upgrade", "head", succeeds=False)

    assert "stamp is contradictory" in result.stderr
    assert current_revision(path) == "d22c6b17208a"
    assert application_tables(path) == set()


def test_incompatible_existing_schema_is_rejected_before_changes(tmp_path):
    path = tmp_path / "incompatible.db"
    alembic(path, "upgrade", "522d2ff063fe")
    engine = create_engine(database_url(path))
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id TEXT PRIMARY KEY)"))
        connection.execute(text("INSERT INTO users VALUES ('preserve-me')"))

    result = alembic(path, "upgrade", "head", succeeds=False)

    assert "Incompatible existing users schema" in result.stderr
    assert current_revision(path) == "522d2ff063fe"
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT id FROM users")) == "preserve-me"
        lead_columns = {item["name"] for item in inspect(connection).get_columns("leads")}
        assert "opportunity_score" not in lead_columns


def test_unique_identifiers_and_expected_types(tmp_path):
    path = tmp_path / "constraints.db"
    alembic(path, "upgrade", "head")
    inspector = inspect(create_engine(database_url(path)))

    def unique_sets(table_name):
        result = {
            frozenset(item["column_names"])
            for item in inspector.get_unique_constraints(table_name)
            if item.get("column_names")
        }
        result.update(
            frozenset(item["column_names"])
            for item in inspector.get_indexes(table_name)
            if item.get("unique")
        )
        return result

    assert frozenset({"email"}) in unique_sets("users")
    assert frozenset({"user_uid"}) in unique_sets("users")
    assert frozenset({"business_uid"}) in unique_sets("businesses")
    assert frozenset({"mission_uid"}) in unique_sets("missions")
    assert inspector.get_columns("leads")[0]["type"]._type_affinity is metadata.tables[
        "leads"
    ].c.id.type._type_affinity


def test_startup_create_all_behavior_remains_available(tmp_path):
    path = tmp_path / "startup.db"
    source = (BACKEND / "main.py").read_text()
    assert "metadata.create_all(\n    bind=engine,\n)" in source
    metadata.create_all(create_engine(database_url(path)))
    assert application_tables(path) == EXPECTED_TABLES
    assert current_revision(path) is None
