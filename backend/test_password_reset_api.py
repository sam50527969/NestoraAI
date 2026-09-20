from collections.abc import Generator
from pathlib import Path
from urllib.parse import (
    parse_qs,
    urlparse,
)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

import app.auth.routes as auth_routes
from app.auth.login_throttle import (
    password_reset_throttle,
)
from app.auth.models import User
from app.auth.routes import (
    router as auth_router,
)
from app.database.database import (
    Base,
    get_db,
)


TEST_EMAIL = (
    "password-reset@nestora.test"
)

OLD_PASSWORD = (
    "OldPassword123!"
)

NEW_PASSWORD = (
    "NewPassword456!"
)


class RecordingEmailProvider:
    def __init__(self):
        self.messages = []

    def send_email(
        self,
        **kwargs,
    ):
        self.messages.append(kwargs)

        return {
            "provider": "test",
            "message_id": "test-message",
        }


class FailingEmailProvider:
    def send_email(
        self,
        **kwargs,
    ):
        raise RuntimeError(
            "Email disabled."
        )


@pytest.fixture
def password_reset_environment(
    tmp_path: Path,
) -> Generator[
    tuple[
        TestClient,
        sessionmaker,
    ],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "password-reset.db"
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

    password_reset_throttle.clear()

    app = FastAPI()
    app.include_router(auth_router)

    def override_get_db():
        db: Session = (
            session_factory()
        )

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as client:
        yield (
            client,
            session_factory,
        )

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )

    engine.dispose()

    password_reset_throttle.clear()


def register_user(
    client: TestClient,
):
    response = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "full_name":
                "Password Reset User",
            "password":
                OLD_PASSWORD,
        },
    )

    assert response.status_code == 201


def extract_reset_token(
    provider: RecordingEmailProvider,
) -> str:
    assert len(provider.messages) == 1

    body = provider.messages[0][
        "body"
    ]

    reset_line = next(
        line
        for line in body.splitlines()
        if "reset_token=" in line
    )

    query = parse_qs(
        urlparse(reset_line).query
    )

    return query["reset_token"][0]


def test_password_reset_request_is_generic(
    password_reset_environment,
    monkeypatch: pytest.MonkeyPatch,
):
    client, _ = (
        password_reset_environment
    )

    register_user(client)

    provider = RecordingEmailProvider()

    monkeypatch.setattr(
        auth_routes,
        "email_provider",
        provider,
    )

    existing = client.post(
        "/auth/password-reset/request",
        json={
            "email": TEST_EMAIL,
        },
    )

    missing = client.post(
        "/auth/password-reset/request",
        json={
            "email":
                "missing@nestora.test",
        },
    )

    assert existing.status_code == 200
    assert missing.status_code == 200

    assert (
        existing.json()
        == missing.json()
    )

    assert len(provider.messages) == 1


def test_password_reset_changes_password_and_invalidates_token(
    password_reset_environment,
    monkeypatch: pytest.MonkeyPatch,
):
    client, _ = (
        password_reset_environment
    )

    register_user(client)

    provider = RecordingEmailProvider()

    monkeypatch.setattr(
        auth_routes,
        "email_provider",
        provider,
    )

    request_response = client.post(
        "/auth/password-reset/request",
        json={
            "email": TEST_EMAIL,
        },
    )

    assert (
        request_response.status_code
        == 200
    )

    token = extract_reset_token(
        provider
    )

    reset_response = client.post(
        "/auth/password-reset/confirm",
        json={
            "token": token,
            "password":
                NEW_PASSWORD,
        },
    )

    assert (
        reset_response.status_code
        == 200
    )

    old_login = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password":
                OLD_PASSWORD,
        },
    )

    new_login = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password":
                NEW_PASSWORD,
        },
    )

    assert old_login.status_code == 401
    assert new_login.status_code == 200

    reused = client.post(
        "/auth/password-reset/confirm",
        json={
            "token": token,
            "password":
                "AnotherPassword789!",
        },
    )

    assert reused.status_code == 400


def test_invalid_reset_token_is_rejected(
    password_reset_environment,
):
    client, _ = (
        password_reset_environment
    )

    response = client.post(
        "/auth/password-reset/confirm",
        json={
            "token":
                "x" * 30,
            "password":
                NEW_PASSWORD,
        },
    )

    assert response.status_code == 400


def test_email_failure_does_not_reveal_account(
    password_reset_environment,
    monkeypatch: pytest.MonkeyPatch,
):
    client, _ = (
        password_reset_environment
    )

    register_user(client)

    monkeypatch.setattr(
        auth_routes,
        "email_provider",
        FailingEmailProvider(),
    )

    response = client.post(
        "/auth/password-reset/request",
        json={
            "email": TEST_EMAIL,
        },
    )

    assert response.status_code == 200

    assert (
        "If an account exists"
        in response.json()["message"]
    )



def test_password_reset_requests_are_rate_limited(
    password_reset_environment,
    monkeypatch: pytest.MonkeyPatch,
):
    client, _ = (
        password_reset_environment
    )

    register_user(client)

    provider = RecordingEmailProvider()

    monkeypatch.setattr(
        auth_routes,
        "email_provider",
        provider,
    )

    for _ in range(3):
        response = client.post(
            "/auth/password-reset/request",
            json={
                "email": TEST_EMAIL,
            },
        )

        assert response.status_code == 200

    blocked = client.post(
        "/auth/password-reset/request",
        json={
            "email": TEST_EMAIL,
        },
    )

    assert blocked.status_code == 429

    assert (
        blocked.headers["retry-after"]
        == "900"
    )

    assert len(provider.messages) == 3
