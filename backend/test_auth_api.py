import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

warnings.filterwarnings(
    "ignore",
    message=(
        "Using `httpx` with "
        "`starlette.testclient` "
        "is deprecated.*"
    ),
    category=Warning,
)

from fastapi.testclient import TestClient

from app.auth.models import User
from app.auth.routes import (
    router as auth_router,
)
from app.database.database import (
    Base,
    get_db,
)


TEST_EMAIL = "owner@nestora.test"
TEST_PASSWORD = "StrongPassword123!"


@pytest.fixture
def auth_environment(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-auth-test.db"
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
        yield client, session_factory

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )

    engine.dispose()


def register_user(
    client: TestClient,
    *,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
    full_name: str = "Nestora Owner",
):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
        },
    )


def login_user(
    client: TestClient,
    *,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def test_registers_user_securely(
    auth_environment,
) -> None:
    client, session_factory = (
        auth_environment
    )

    response = register_user(client)

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == TEST_EMAIL
    assert data["full_name"] == (
        "Nestora Owner"
    )
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert data["user_uid"].startswith(
        "usr_"
    )

    assert "password" not in data
    assert "password_hash" not in data

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == TEST_EMAIL
            )
            .first()
        )

        assert user is not None
        assert (
            user.password_hash
            != TEST_PASSWORD
        )
        assert user.password_hash.startswith(
            "$argon2"
        )


def test_registration_normalizes_email(
    auth_environment,
) -> None:
    client, _ = auth_environment

    response = register_user(
        client,
        email="  OWNER@NESTORA.TEST  ",
    )

    assert response.status_code == 201
    assert (
        response.json()["email"]
        == TEST_EMAIL
    )


def test_duplicate_email_returns_409(
    auth_environment,
) -> None:
    client, _ = auth_environment

    first_response = register_user(
        client
    )

    second_response = register_user(
        client,
        email="OWNER@NESTORA.TEST",
    )

    assert (
        first_response.status_code
        == 201
    )

    assert (
        second_response.status_code
        == 409
    )

    assert (
        "already exists"
        in second_response.json()[
            "detail"
        ]
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "email": "invalid-email",
            "full_name": "Test User",
            "password":
                TEST_PASSWORD,
        },
        {
            "email":
                "valid@nestora.test",
            "full_name": "T",
            "password":
                TEST_PASSWORD,
        },
        {
            "email":
                "valid@nestora.test",
            "full_name": "Test User",
            "password": "short",
        },
    ],
)
def test_registration_rejects_invalid_data(
    auth_environment,
    payload: dict,
) -> None:
    client, _ = auth_environment

    response = client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 422


def test_login_and_current_user(
    auth_environment,
) -> None:
    client, _ = auth_environment

    assert (
        register_user(client).status_code
        == 201
    )

    login_response = login_user(
        client
    )

    assert (
        login_response.status_code
        == 200
    )

    login_data = (
        login_response.json()
    )

    assert (
        login_data["token_type"]
        == "bearer"
    )

    assert (
        login_data["expires_in"]
        == 3600
    )

    access_token = (
        login_data["access_token"]
    )

    assert isinstance(
        access_token,
        str,
    )

    assert access_token.count(".") == 2

    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
        },
    )

    assert me_response.status_code == 200

    assert (
        me_response.json()["email"]
        == TEST_EMAIL
    )


def test_invalid_login_returns_401(
    auth_environment,
) -> None:
    client, _ = auth_environment

    register_user(client)

    wrong_password = login_user(
        client,
        password="WrongPassword123!",
    )

    missing_user = login_user(
        client,
        email="missing@nestora.test",
    )

    assert (
        wrong_password.status_code
        == 401
    )

    assert (
        missing_user.status_code
        == 401
    )


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "Bearer invalid-token",
        "Basic invalid-token",
    ],
)
def test_current_user_requires_valid_token(
    auth_environment,
    authorization: str | None,
) -> None:
    client, _ = auth_environment

    headers = {}

    if authorization is not None:
        headers["Authorization"] = (
            authorization
        )

    response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert response.status_code == 401
    assert (
        response.headers[
            "www-authenticate"
        ]
        == "Bearer"
    )


def test_inactive_user_is_rejected(
    auth_environment,
) -> None:
    client, session_factory = (
        auth_environment
    )

    register_user(client)

    login_response = login_user(
        client
    )

    access_token = (
        login_response.json()[
            "access_token"
        ]
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == TEST_EMAIL
            )
            .first()
        )

        user.is_active = False
        db.commit()

    second_login = login_user(
        client
    )

    assert (
        second_login.status_code
        == 401
    )

    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
        },
    )

    assert me_response.status_code == 401