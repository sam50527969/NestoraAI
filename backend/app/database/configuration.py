from typing import Protocol

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url


class AlembicConfig(Protocol):
    def set_main_option(self, name: str, value: str) -> None: ...


def connection_args(database_url: str) -> dict[str, bool]:
    """Return driver arguments required by the configured database."""

    if make_url(database_url).get_backend_name() == "sqlite":
        return {"check_same_thread": False}

    return {}


def create_database_engine(database_url: str) -> Engine:
    """Create an engine with backend-appropriate connection arguments."""

    return create_engine(
        database_url,
        connect_args=connection_args(database_url),
        pool_pre_ping=True,
    )


def alembic_database_url(database_url: str) -> str:
    """Escape ConfigParser interpolation characters in a database URL."""

    return database_url.replace("%", "%%")


def configure_alembic_database_url(
    config: AlembicConfig,
    database_url: str,
) -> None:
    """Set Alembic's URL without exposing it in the ini file."""

    config.set_main_option(
        "sqlalchemy.url",
        alembic_database_url(database_url),
    )
