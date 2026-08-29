import warnings
from collections.abc import (
    Generator,
)
from pathlib import Path

import pytest
from fastapi import FastAPI
from sqlalchemy import (
    create_engine,
)
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

from fastapi.testclient import (
    TestClient,
)

from app.bootstrap.routes import (
    register_routes,
)
from app.database.database import (
    Base,
    get_db,
)


TEST_EMAIL = (
    "protected@nestora.test"
)

TEST_PASSWORD = (
    "StrongPassword123!"
)


@pytest.fixture
def protected_api(
    tmp_path: Path,
) -> Generator[
    TestClient,
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-protected-api.db"
    )

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={
            "check_same_thread":
                False,
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

    register_routes(app)

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
        yield client

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )

    engine.dispose()


def register_and_login(
    client: TestClient,
) -> str:
    registration = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "full_name":
                "Protected API User",
            "password":
                TEST_PASSWORD,
        },
    )

    assert (
        registration.status_code
        == 201
    )

    login = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password":
                TEST_PASSWORD,
        },
    )

    assert login.status_code == 200

    return login.json()[
        "access_token"
    ]


def test_registration_and_login_are_public(
    protected_api: TestClient,
) -> None:
    registration = (
        protected_api.post(
            "/auth/register",
            json={
                "email": TEST_EMAIL,
                "full_name":
                    "Protected API User",
                "password":
                    TEST_PASSWORD,
            },
        )
    )

    assert (
        registration.status_code
        == 201
    )

    login = protected_api.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password":
                TEST_PASSWORD,
        },
    )

    assert login.status_code == 200
    assert (
        login.json()["token_type"]
        == "bearer"
    )


@pytest.mark.parametrize(
    "path",
    [
        "/crm/leads",
        "/dashboard/summary",
        "/clinic/leads",
        "/realtime/workforce",
    ],
)
def test_business_api_requires_authentication(
    protected_api: TestClient,
    path: str,
) -> None:
    response = protected_api.get(
        path
    )

    assert response.status_code == 401

    assert (
        response.headers[
            "www-authenticate"
        ]
        == "Bearer"
    )


def test_invalid_token_is_rejected(
    protected_api: TestClient,
) -> None:
    response = protected_api.get(
        "/crm/leads",
        headers={
            "Authorization":
                "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_crm_requires_business_membership(
    protected_api: TestClient,
) -> None:
    token = register_and_login(
        protected_api
    )

    response = protected_api.get(
        "/crm/leads",
        headers={
            "Authorization":
                f"Bearer {token}",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "/dashboard/summary",
        "/clinic/leads",
        "/realtime/workforce",
    ],
)
def test_valid_token_allows_business_api_access(
    protected_api: TestClient,
    path: str,
) -> None:
    token = register_and_login(
        protected_api
    )

    response = protected_api.get(
        path,
        headers={
            "Authorization":
                f"Bearer {token}",
        },
    )

    assert response.status_code == 200
