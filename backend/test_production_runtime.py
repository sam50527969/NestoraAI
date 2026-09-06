from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.bootstrap.health import router as health_router
from app.database.configuration import create_database_engine


def test_health_endpoint_is_public_and_alive():
    app = FastAPI()
    app.include_router(health_router)

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "nestora-backend",
    }


def test_ready_endpoint_checks_database():
    app = FastAPI()
    app.include_router(health_router)

    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "available",
    }


def test_database_engine_uses_pre_ping():
    engine = create_database_engine(
        "sqlite:///:memory:"
    )

    assert engine.pool._pre_ping is True

    engine.dispose()


def test_ready_endpoint_returns_503_when_database_is_unavailable(
    monkeypatch,
):
    from app.bootstrap import health

    class UnavailableEngine:
        def connect(self):
            raise OperationalError(
                "SELECT 1",
                {},
                Exception("database unavailable"),
            )

    monkeypatch.setattr(
        health,
        "engine",
        UnavailableEngine(),
    )

    app = FastAPI()
    app.include_router(health.router)

    response = TestClient(app).get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database is unavailable.",
    }



def test_main_does_not_create_database_schema_at_import_time():
    from pathlib import Path

    main_source = Path("main.py").read_text(
        encoding="utf-8",
    )

    assert "metadata.create_all" not in main_source
