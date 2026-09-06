from pathlib import Path
from unittest.mock import patch

import pytest
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text

import prepare_production_database as bootstrap


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def current_head() -> str:
    config = bootstrap.alembic_config(
        "sqlite:///:memory:"
    )
    return ScriptDirectory.from_config(
        config
    ).get_current_head()


def test_empty_database_bootstraps_canonical_schema_and_stamps_head(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "fresh.db"
    database_url = sqlite_url(database_path)

    monkeypatch.setattr(
        bootstrap,
        "DATABASE_URL",
        database_url,
    )

    bootstrap.prepare_database()

    engine = create_engine(database_url)

    try:
        tables = set(inspect(engine).get_table_names())

        assert set(bootstrap.metadata.tables).issubset(tables)
        assert bootstrap.ALEMBIC_VERSION_TABLE in tables

        with engine.connect() as connection:
            revision = connection.execute(
                text(
                    "SELECT version_num "
                    "FROM alembic_version"
                )
            ).scalar_one()

        assert revision == current_head()
    finally:
        engine.dispose()


def test_non_empty_unversioned_database_is_rejected(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "ambiguous.db"
    database_url = sqlite_url(database_path)

    engine = create_engine(database_url)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE legacy_table "
                    "(id INTEGER PRIMARY KEY)"
                )
            )
    finally:
        engine.dispose()

    monkeypatch.setattr(
        bootstrap,
        "DATABASE_URL",
        database_url,
    )

    with pytest.raises(
        RuntimeError,
        match="non-empty but has no Alembic revision",
    ):
        bootstrap.prepare_database()


def test_versioned_database_uses_normal_alembic_upgrade(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "versioned.db"
    database_url = sqlite_url(database_path)

    engine = create_engine(database_url)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE alembic_version "
                    "(version_num VARCHAR(32) NOT NULL)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO alembic_version(version_num) "
                    "VALUES (:revision)"
                ),
                {"revision": current_head()},
            )
            connection.execute(
                text(
                    "CREATE TABLE existing_application_table "
                    "(id INTEGER PRIMARY KEY)"
                )
            )
    finally:
        engine.dispose()

    monkeypatch.setattr(
        bootstrap,
        "DATABASE_URL",
        database_url,
    )

    with patch(
        "prepare_production_database.command.upgrade",
    ) as upgrade:
        bootstrap.prepare_database()

    upgrade.assert_called_once()

    config, revision = upgrade.call_args.args

    assert revision == "head"
    assert (
        config.get_main_option("sqlalchemy.url")
        == database_url
    )


def test_bootstrap_alembic_config_uses_requested_database_url():
    database_url = "sqlite:///./bootstrap-test.db"

    config = bootstrap.alembic_config(database_url)

    assert (
        config.get_main_option("sqlalchemy.url")
        == database_url
    )

def test_alembic_only_database_is_recovered_as_fresh_database(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "render-partial.db"
    database_url = sqlite_url(database_path)

    engine = create_engine(database_url)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE alembic_version "
                    "(version_num VARCHAR(32) NOT NULL)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO alembic_version(version_num) "
                    "VALUES ('d22c6b17208a')"
                )
            )
    finally:
        engine.dispose()

    monkeypatch.setattr(
        bootstrap,
        "DATABASE_URL",
        database_url,
    )

    bootstrap.prepare_database()

    engine = create_engine(database_url)

    try:
        tables = set(inspect(engine).get_table_names())

        assert set(bootstrap.metadata.tables).issubset(tables)
        assert bootstrap.ALEMBIC_VERSION_TABLE in tables

        with engine.connect() as connection:
            revision = connection.execute(
                text(
                    "SELECT version_num "
                    "FROM alembic_version"
                )
            ).scalar_one()

        assert revision == current_head()
    finally:
        engine.dispose()
