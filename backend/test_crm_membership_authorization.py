from __future__ import annotations

import warnings

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)
from sqlalchemy.pool import StaticPool

from app.auth.models import User
from app.auth.security import (
    create_access_token,
    hash_password,
)
from app.database.database import (
    Base,
    get_db,
)
from app.database.models import (
    Business,
    BusinessMembership,
    Lead,
)
from app.routes.crm import router as crm_router


warnings.filterwarnings(
    "ignore",
    message=(
        "Using `httpx` with "
        "`starlette.testclient` "
        "is deprecated.*"
    ),
    category=Warning,
)


@pytest.fixture
def scoped_api():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    user_a = User(
        user_uid="usr-scope-a",
        email="scope-a@example.com",
        full_name="Scope A",
        password_hash=hash_password(
            "Password123!"
        ),
        role="user",
        is_active=True,
    )

    user_b = User(
        user_uid="usr-scope-b",
        email="scope-b@example.com",
        full_name="Scope B",
        password_hash=hash_password(
            "Password123!"
        ),
        role="user",
        is_active=True,
    )

    user_none = User(
        user_uid="usr-scope-none",
        email="scope-none@example.com",
        full_name="Scope None",
        password_hash=hash_password(
            "Password123!"
        ),
        role="user",
        is_active=True,
    )

    business_a = Business(
        business_uid="biz-scope-a",
        name="Scope Business A",
        industry="OTHER",
        country="Australia",
        currency="AUD",
    )

    business_b = Business(
        business_uid="biz-scope-b",
        name="Scope Business B",
        industry="OTHER",
        country="Canada",
        currency="CAD",
    )

    db.add_all(
        [
            user_a,
            user_b,
            user_none,
            business_a,
            business_b,
        ]
    )

    db.commit()

    db.add_all(
        [
            BusinessMembership(
                membership_uid="mem-scope-a",
                user_uid=user_a.user_uid,
                business_uid=(
                    business_a.business_uid
                ),
                role="owner",
                is_active=True,
            ),
            BusinessMembership(
                membership_uid="mem-scope-b",
                user_uid=user_b.user_uid,
                business_uid=(
                    business_b.business_uid
                ),
                role="owner",
                is_active=True,
            ),
        ]
    )

    db.commit()

    user_a_uid = user_a.user_uid
    user_b_uid = user_b.user_uid
    user_none_uid = user_none.user_uid

    business_a_uid = business_a.business_uid
    business_b_uid = business_b.business_uid

    db.close()

    app = FastAPI()
    app.include_router(crm_router)

    def override_get_db():
        test_db: Session = SessionLocal()

        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    client = TestClient(app)

    try:
        yield (
            client,
            SessionLocal,
            user_a_uid,
            user_b_uid,
            user_none_uid,
            business_a_uid,
            business_b_uid,
        )
    finally:
        client.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def auth_header(user_uid: str) -> dict[str, str]:
    token, _ = create_access_token(
        user_uid
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_crm_requires_active_membership(
    scoped_api,
):
    (
        client,
        _,
        _,
        _,
        user_none,
        _,
        _,
    ) = scoped_api

    response = client.get(
        "/crm/leads",
        headers=auth_header(
            user_none
        ),
    )

    assert response.status_code == 403


def test_crm_creates_lead_in_authenticated_business(
    scoped_api,
):
    (
        client,
        SessionLocal,
        user_a,
        _,
        _,
        business_a,
        _,
    ) = scoped_api

    response = client.post(
        "/crm/leads",
        headers=auth_header(
            user_a
        ),
        json={
            "name": "Scoped Lead A",
        },
    )

    assert response.status_code == 201

    lead_id = response.json()["id"]

    db = SessionLocal()

    try:
        lead = db.get(
            Lead,
            lead_id,
        )

        assert lead is not None
        assert (
            lead.business_uid
            == business_a
        )
    finally:
        db.close()


def test_crm_ignores_client_business_override(
    scoped_api,
):
    (
        client,
        SessionLocal,
        user_a,
        _,
        _,
        business_a,
        business_b,
    ) = scoped_api

    response = client.post(
        "/crm/leads",
        headers=auth_header(
            user_a
        ),
        json={
            "name": "Override Attempt",
            "business_uid": (
                business_b
            ),
        },
    )

    assert response.status_code == 201

    lead_id = response.json()["id"]

    db = SessionLocal()

    try:
        lead = db.get(
            Lead,
            lead_id,
        )

        assert lead is not None
        assert (
            lead.business_uid
            == business_a
        )
        assert (
            lead.business_uid
            != business_b
        )
    finally:
        db.close()


def test_business_cannot_read_other_business_lead(
    scoped_api,
):
    (
        client,
        _,
        user_a,
        user_b,
        _,
        _,
        _,
    ) = scoped_api

    created = client.post(
        "/crm/leads",
        headers=auth_header(
            user_a
        ),
        json={
            "name": "Private Lead",
        },
    )

    assert created.status_code == 201

    lead_id = created.json()["id"]

    response = client.get(
        f"/crm/leads/{lead_id}",
        headers=auth_header(
            user_b
        ),
    )

    assert response.status_code == 404


def test_business_cannot_update_other_business_lead(
    scoped_api,
):
    (
        client,
        _,
        user_a,
        user_b,
        _,
        _,
        _,
    ) = scoped_api

    created = client.post(
        "/crm/leads",
        headers=auth_header(
            user_a
        ),
        json={
            "name": "Protected Lead",
        },
    )

    assert created.status_code == 201

    lead_id = created.json()["id"]

    response = client.put(
        f"/crm/leads/{lead_id}",
        headers=auth_header(
            user_b
        ),
        json={
            "status": "Contacted",
        },
    )

    assert response.status_code == 404


def test_pipeline_summary_is_business_scoped(
    scoped_api,
):
    (
        client,
        _,
        user_a,
        user_b,
        _,
        _,
        _,
    ) = scoped_api

    for name in (
        "A Lead One",
        "A Lead Two",
    ):
        response = client.post(
            "/crm/leads",
            headers=auth_header(
                user_a
            ),
            json={
                "name": name,
            },
        )

        assert response.status_code == 201

    response = client.post(
        "/crm/leads",
        headers=auth_header(
            user_b
        ),
        json={
            "name": "B Lead One",
        },
    )

    assert response.status_code == 201

    summary_a = client.get(
        "/crm/pipeline/summary",
        headers=auth_header(
            user_a
        ),
    )

    summary_b = client.get(
        "/crm/pipeline/summary",
        headers=auth_header(
            user_b
        ),
    )

    assert summary_a.status_code == 200
    assert summary_b.status_code == 200

    assert (
        summary_a.json()["total_leads"]
        == 2
    )

    assert (
        summary_b.json()["total_leads"]
        == 1
    )
