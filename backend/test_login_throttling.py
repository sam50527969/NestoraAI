from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.login_throttle import (
    LoginFailureThrottle,
    login_failure_throttle,
)
from app.auth.routes import router as auth_router
from app.database.database import Base, get_db


@pytest.fixture
def throttle_client(
    tmp_path: Path,
) -> Generator[TestClient, None, None]:
    database_path = (
        tmp_path
        / "nestora-login-throttle-test.db"
    )

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={
            "check_same_thread": False,
        },
    )

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(
        bind=engine
    )

    test_app = FastAPI()
    test_app.include_router(auth_router)

    def override_get_db():
        db: Session = session_factory()

        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[
        get_db
    ] = override_get_db

    login_failure_throttle.clear()

    try:
        with TestClient(test_app) as client:
            yield client
    finally:
        login_failure_throttle.clear()

        test_app.dependency_overrides.clear()

        Base.metadata.drop_all(
            bind=engine
        )

        engine.dispose()


def test_throttle_blocks_after_failure_limit():
    throttle = LoginFailureThrottle(
        max_failures=3,
        window_seconds=900,
        max_identities=100,
    )

    identity = "blocked@example.com"

    assert throttle.is_blocked(identity) is False

    throttle.record_failure(identity)
    throttle.record_failure(identity)

    assert throttle.is_blocked(identity) is False

    throttle.record_failure(identity)

    assert throttle.is_blocked(identity) is True


def test_throttle_reset_removes_failures():
    throttle = LoginFailureThrottle(
        max_failures=2,
        window_seconds=900,
        max_identities=100,
    )

    identity = "reset@example.com"

    throttle.record_failure(identity)
    throttle.record_failure(identity)

    assert throttle.is_blocked(identity) is True

    throttle.reset(identity)

    assert throttle.is_blocked(identity) is False


def test_throttle_bounds_tracked_identities():
    throttle = LoginFailureThrottle(
        max_failures=5,
        window_seconds=900,
        max_identities=2,
    )

    throttle.record_failure(
        "first@example.com"
    )
    throttle.record_failure(
        "second@example.com"
    )
    throttle.record_failure(
        "third@example.com"
    )

    assert len(throttle._failures) == 2

    assert (
        "first@example.com"
        not in throttle._failures
    )


def test_login_returns_429_after_repeated_failures(
    throttle_client: TestClient,
):
    payload = {
        "email": "throttle-missing@example.com",
        "password": "DefinitelyWrong123!",
    }

    for _ in range(5):
        response = throttle_client.post(
            "/auth/login",
            json=payload,
        )

        assert response.status_code == 401

    blocked = throttle_client.post(
        "/auth/login",
        json=payload,
    )

    assert blocked.status_code == 429

    assert blocked.json() == {
        "detail": (
            "Too many failed login attempts. "
            "Please try again later."
        )
    }

    assert (
        blocked.headers["retry-after"]
        == "900"
    )


def test_login_throttle_uses_normalized_email(
    throttle_client: TestClient,
):
    for _ in range(5):
        response = throttle_client.post(
            "/auth/login",
            json={
                "email": "CaseUser@Example.COM",
                "password": "DefinitelyWrong123!",
            },
        )

        assert response.status_code == 401

    blocked = throttle_client.post(
        "/auth/login",
        json={
            "email": "caseuser@example.com",
            "password": "DefinitelyWrong123!",
        },
    )

    assert blocked.status_code == 429


def test_throttle_failures_expire_after_window():
    now = [1000.0]

    throttle = LoginFailureThrottle(
        max_failures=2,
        window_seconds=60,
        max_identities=100,
        clock=lambda: now[0],
    )

    identity = "expiry@example.com"

    throttle.record_failure(identity)
    throttle.record_failure(identity)

    assert throttle.is_blocked(identity) is True

    now[0] += 61

    assert throttle.is_blocked(identity) is False
