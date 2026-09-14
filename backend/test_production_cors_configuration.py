import os
import subprocess
import sys


def run_config_import(
    cors_origins: str,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()

    env.update(
        {
            "APP_ENV": "production",
            "DATABASE_URL": (
                "postgresql+psycopg://"
                "user:password@localhost/nestora"
            ),
            "AUTH_SECRET_KEY": (
                "production-test-secret-"
                "that-is-not-development"
            ),
            "CORS_ALLOWED_ORIGINS": cors_origins,
        }
    )

    return subprocess.run(
        [
            sys.executable,
            "-c",
            "import app.config",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_production_accepts_explicit_https_origin():
    result = run_config_import(
        "https://app.example.com"
    )

    assert result.returncode == 0


def test_production_rejects_empty_cors_origins():
    result = run_config_import("")

    assert result.returncode != 0
    assert (
        "at least one production origin"
        in result.stderr
    )


def test_production_rejects_cors_wildcard():
    result = run_config_import("*")

    assert result.returncode != 0
    assert (
        "must not contain a wildcard"
        in result.stderr
    )


def test_production_rejects_localhost_origin():
    result = run_config_import(
        "http://localhost:5173"
    )

    assert result.returncode != 0
    assert (
        "must not contain localhost origins"
        in result.stderr
    )


def test_production_rejects_loopback_origin():
    result = run_config_import(
        "http://127.0.0.1:5173"
    )

    assert result.returncode != 0
    assert (
        "must not contain localhost origins"
        in result.stderr
    )


def test_development_defaults_remain_supported():
    env = os.environ.copy()

    env.update(
        {
            "APP_ENV": "development",
            "DATABASE_URL": "sqlite:///./nestora.db",
        }
    )

    env.pop(
        "CORS_ALLOWED_ORIGINS",
        None,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from app.config import "
                "CORS_ALLOWED_ORIGINS; "
                "assert "
                "'http://localhost:5173' "
                "in CORS_ALLOWED_ORIGINS"
            ),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
