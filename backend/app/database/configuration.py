from typing import Protocol

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url


class AlembicConfig(Protocol):
    def set_main_option(self, name: str, value: str) -> None: ...


def normalize_database_url(database_url: str) -> str:
    """Use Psycopg 3 for provider-style PostgreSQL URLs."""

    if database_url.lower().startswith("postgresql://"):
        return (
            "postgresql+psycopg://"
            + database_url[len("postgresql://"):]
        )

    return database_url


def connection_args(database_url: str) -> dict[str, bool]:
    """Return driver arguments required by the configured database."""

    normalized_url = normalize_database_url(database_url)

    if make_url(normalized_url).get_backend_name() == "sqlite":
        return {"check_same_thread": False}

    return {}


def create_database_engine(database_url: str) -> Engine:
    """Create an engine with backend-appropriate connection arguments."""

    normalized_url = normalize_database_url(database_url)

    return create_engine(
        normalized_url,
        connect_args=connection_args(normalized_url),
        pool_pre_ping=True,
    )


def alembic_database_url(database_url: str) -> str:
    """Normalize and escape a database URL for Alembic."""

    normalized_url = normalize_database_url(database_url)
    return normalized_url.replace("%", "%%")


def configure_alembic_database_url(
    config: AlembicConfig,
    database_url: str,
) -> None:
    """Set Alembic's URL without exposing it in the ini file."""

    config.set_main_option(
        "sqlalchemy.url",
        alembic_database_url(database_url),
    )
