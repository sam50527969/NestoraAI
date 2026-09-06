import importlib

from alembic.config import Config


EXPECTED_TABLES = {
    "agent_tasks",
    "business_memberships",
    "businesses",
    "ceo_approvals",
    "ceo_execution_records",
    "clinic_leads",
    "collaboration_contributions",
    "collaboration_sessions",
    "executive_memory",
    "executive_messages",
    "follow_up_activities",
    "leads",
    "marketing_plans",
    "mission_events",
    "missions",
    "outreach_activities",
    "pipeline_activities",
    "users",
}


def test_canonical_metadata_has_exact_table_inventory():
    from app.database.metadata import metadata

    assert set(metadata.tables) == EXPECTED_TABLES
    assert len(metadata.tables) == len(EXPECTED_TABLES)


def test_canonical_metadata_table_names_are_unique():
    from app.database.metadata import metadata

    names = [table.name for table in metadata.sorted_tables]
    assert len(names) == len(set(names))


def test_runtime_uses_central_database_url():
    from app import config
    from app.database import database
    from app.database.configuration import normalize_database_url

    assert database.DATABASE_URL == config.DATABASE_URL
    assert (
        database.engine.url.render_as_string(hide_password=False)
        == normalize_database_url(config.DATABASE_URL)
    )


def test_environment_override_is_shared_by_runtime_and_alembic(monkeypatch):
    override = "sqlite:///./environment-override.db"
    monkeypatch.setenv("DATABASE_URL", override)

    from app import config
    from app.database import database

    importlib.reload(config)
    importlib.reload(database)

    from app.database.configuration import configure_alembic_database_url

    alembic_config = Config("alembic.ini")
    configure_alembic_database_url(alembic_config, config.DATABASE_URL)

    assert database.engine.url.render_as_string(hide_password=False) == override
    assert alembic_config.get_main_option("sqlalchemy.url") == override


def test_sqlite_only_connection_arguments():
    from app.database.configuration import connection_args

    assert connection_args("sqlite:///./nestora.db") == {"check_same_thread": False}
    assert connection_args("postgresql://localhost/nestora") == {}


def test_provider_postgresql_url_uses_psycopg3():
    from app.database.configuration import normalize_database_url

    assert (
        normalize_database_url(
            "postgresql://user:password@localhost:5432/nestora"
        )
        == "postgresql+psycopg://user:password@localhost:5432/nestora"
    )


def test_explicit_psycopg_url_is_unchanged():
    from app.database.configuration import normalize_database_url

    database_url = (
        "postgresql+psycopg://"
        "user:password@localhost:5432/nestora"
    )

    assert normalize_database_url(database_url) == database_url


def test_alembic_uses_psycopg3_for_provider_postgresql_url():
    from app.database.configuration import configure_alembic_database_url

    config = Config()
    configure_alembic_database_url(
        config,
        "postgresql://user:password@localhost:5432/nestora",
    )

    assert (
        config.get_main_option("sqlalchemy.url")
        == "postgresql+psycopg://user:password@localhost:5432/nestora"
    )


def test_alembic_database_urls_are_percent_safe():
    from app.database.configuration import alembic_database_url

    raw_url = "postgresql://user:p%40ss@localhost/nestora%20ai"
    escaped_url = alembic_database_url(raw_url)
    config = Config()
    config.set_main_option("sqlalchemy.url", escaped_url)

    assert (
        config.get_main_option("sqlalchemy.url")
        == "postgresql+psycopg://user:p%40ss@localhost/nestora%20ai"
    )
