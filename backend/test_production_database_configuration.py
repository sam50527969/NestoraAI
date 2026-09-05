import os
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent


def run_config_import(**environment):
    env = os.environ.copy()
    env.update(environment)

    return subprocess.run(
        [
            sys.executable,
            "-c",
            "import app.config",
        ],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_rejects_default_sqlite_database():
    result = run_config_import(
        APP_ENV="production",
        DATABASE_URL="sqlite:///./nestora.db",
        AUTH_SECRET_KEY="production-secret-for-test",
    )

    assert result.returncode != 0
    assert (
        "DATABASE_URL must use a production database"
        in result.stderr
    )


def test_production_accepts_postgresql_database_url():
    result = run_config_import(
        APP_ENV="production",
        DATABASE_URL=(
            "postgresql+psycopg://"
            "user:password@localhost:5432/nestora"
        ),
        AUTH_SECRET_KEY="production-secret-for-test",
    )

    assert result.returncode == 0, result.stderr


def test_development_keeps_sqlite_support():
    result = run_config_import(
        APP_ENV="development",
        DATABASE_URL="sqlite:///./nestora.db",
        AUTH_SECRET_KEY=(
            "nestora-development-secret-"
            "replace-before-production"
        ),
    )

    assert result.returncode == 0, result.stderr
