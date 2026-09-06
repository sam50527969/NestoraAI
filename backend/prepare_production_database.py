"""Safe production database bootstrap and migration handling."""

from __future__ import annotations

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.config import DATABASE_URL
from app.database.configuration import (
    configure_alembic_database_url,
    create_database_engine,
)
from app.database.metadata import metadata


ALEMBIC_VERSION_TABLE = "alembic_version"


def alembic_config(database_url: str) -> Config:
    """Return Alembic configuration for one database URL."""

    config = Config("alembic.ini")

    configure_alembic_database_url(
        config,
        database_url,
    )

    config.attributes["database_url_configured"] = True

    return config


def database_tables(engine) -> set[str]:
    """Return user-visible table names currently present."""

    return set(inspect(engine).get_table_names())


def has_application_tables(tables: set[str]) -> bool:
    """Return whether any table other than Alembic metadata exists."""

    return bool(
        tables - {ALEMBIC_VERSION_TABLE}
    )


def prepare_database() -> None:
    """Bootstrap a fresh database or upgrade a versioned database."""

    database_url = DATABASE_URL
    engine = create_database_engine(database_url)
    config = alembic_config(database_url)

    try:
        tables = database_tables(engine)

        if not has_application_tables(tables):
            metadata.create_all(bind=engine)
            command.stamp(
                config,
                "head",
                purge=True,
            )
            return

        if ALEMBIC_VERSION_TABLE not in tables:
            raise RuntimeError(
                "Database is non-empty but has no Alembic revision. "
                "Refusing to modify an ambiguous database."
            )

        command.upgrade(config, "head")
    finally:
        engine.dispose()


if __name__ == "__main__":
    prepare_database()
