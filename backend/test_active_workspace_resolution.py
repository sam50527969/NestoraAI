from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.models import User
from app.auth.security import (
    create_access_token,
    hash_password,
)
from app.database.database import Base, get_db
from app.database.models import (
    Business,
    BusinessMembership,
    Lead,
)
from app.routes.crm import router as crm_router


@pytest.fixture
def workspace_api() -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    with session_factory() as db:
        user = User(
            user_uid="usr_workspace",
            email="workspace@example.com",
            full_name="Workspace User",
            password_hash=hash_password(
                "StrongPassword123!"
            ),
            role="user",
            is_active=True,
        )

        other_user = User(
            user_uid="usr_other",
            email="other@example.com",
            full_name="Other User",
            password_hash=hash_password(
                "StrongPassword123!"
            ),
            role="user",
            is_active=True,
        )

        businesses = [
            Business(
                business_uid="biz_alpha",
                name="Alpha",
                industry="OTHER",
                country="Australia",
                currency="AUD",
            ),
            Business(
                business_uid="biz_beta",
                name="Beta",
                industry="OTHER",
                country="Canada",
                currency="CAD",
            ),
            Business(
                business_uid="biz_other",
                name="Other",
                industry="OTHER",
                country="Germany",
                currency="EUR",
            ),
        ]

        db.add_all(
            [
                user,
                other_user,
                *businesses,
            ]
        )
        db.commit()

        db.add_all(
            [
                BusinessMembership(
                    membership_uid="mem_alpha",
                    user_uid=user.user_uid,
                    business_uid="biz_alpha",
                    role="owner",
                    is_active=True,
                ),
                BusinessMembership(
                    membership_uid="mem_beta",
                    user_uid=user.user_uid,
                    business_uid="biz_beta",
                    role="admin",
                    is_active=True,
                ),
                BusinessMembership(
                    membership_uid="mem_other",
                    user_uid=other_user.user_uid,
                    business_uid="biz_other",
                    role="owner",
                    is_active=True,
                ),
            ]
        )
        db.commit()

        db.add_all(
            [
                Lead(
                    business_uid="biz_alpha",
                    name="Alpha Lead",
                ),
                Lead(
                    business_uid="biz_beta",
                    name="Beta Lead",
                ),
                Lead(
                    business_uid="biz_other",
                    name="Other Lead",
                ),
            ]
        )
        db.commit()

    token, _ = create_access_token(
        "usr_workspace"
    )

    app = FastAPI()
    app.include_router(crm_router)

    def override_get_db() -> Generator[
        Session,
        None,
        None,
    ]:
        db = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = (
        override_get_db
    )

    with TestClient(app) as client:
        client.headers.update(
            {
                "Authorization":
                    f"Bearer {token}",
            }
        )

        yield client, session_factory

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_multiple_memberships_require_selection(
    workspace_api: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = workspace_api

    response = client.get(
        "/crm/leads"
    )

    assert response.status_code == 409
    assert (
        "X-Business-Uid"
        in response.json()["detail"]
    )


@pytest.mark.parametrize(
    ("business_uid", "lead_name"),
    [
        ("biz_alpha", "Alpha Lead"),
        ("biz_beta", "Beta Lead"),
    ],
)
def test_selected_active_workspace_scopes_crm(
    workspace_api: tuple[
        TestClient,
        sessionmaker,
    ],
    business_uid: str,
    lead_name: str,
) -> None:
    client, _ = workspace_api

    response = client.get(
        "/crm/leads",
        headers={
            "X-Business-Uid":
                business_uid,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert [
        item["name"]
        for item in body
    ] == [lead_name]


def test_unavailable_workspace_is_forbidden(
    workspace_api: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = workspace_api

    response = client.get(
        "/crm/leads",
        headers={
            "X-Business-Uid":
                "biz_other",
        },
    )

    assert response.status_code == 403


def test_inactive_workspace_is_forbidden(
    workspace_api: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        workspace_api
    )

    with session_factory() as db:
        membership = (
            db.query(BusinessMembership)
            .filter(
                BusinessMembership
                .membership_uid
                == "mem_alpha"
            )
            .one()
        )

        membership.is_active = False
        db.commit()

    response = client.get(
        "/crm/leads",
        headers={
            "X-Business-Uid":
                "biz_alpha",
        },
    )

    assert response.status_code == 403
