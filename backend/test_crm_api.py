import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
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

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database.database import (
    Base,
    get_db,
)
from app.auth.models import User
from app.auth.security import (
    create_access_token,
    hash_password,
)
from app.database.models import (
    Business,
    BusinessMembership,
    Lead,
)
from app.pipeline_activity import (
    service as pipeline_service,
)
from app.pipeline_activity.models import (
    PipelineActivity,
)
from app.pipeline_activity.routes import (
    router as pipeline_router,
)
from app.routes.crm import (
    router as crm_router,
)


@pytest.fixture
def api_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-api-test.db"
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

    Base.metadata.create_all(bind=engine)

    setup_db: Session = session_factory()

    try:
        user = User(
            user_uid="usr-crm-api-test",
            email="crm-api@nestora.test",
            full_name="CRM API Test User",
            password_hash=hash_password(
                "StrongPassword123!"
            ),
            role="user",
            is_active=True,
        )

        business = Business(
            business_uid="biz-crm-api-test",
            name="CRM API Test Business",
            industry="OTHER",
            country="Australia",
            currency="AUD",
        )

        setup_db.add_all(
            [
                user,
                business,
            ]
        )
        setup_db.commit()

        setup_db.add(
            BusinessMembership(
                membership_uid=(
                    "mem-crm-api-test"
                ),
                user_uid=user.user_uid,
                business_uid=(
                    business.business_uid
                ),
                role="owner",
                is_active=True,
            )
        )
        setup_db.commit()

        user_uid = user.user_uid

    finally:
        setup_db.close()

    token, _ = create_access_token(
        user_uid
    )

    monkeypatch.setattr(
        pipeline_service,
        "SessionLocal",
        session_factory,
    )

    app = FastAPI()
    app.include_router(crm_router)
    app.include_router(pipeline_router)

    def override_get_db():
        db: Session = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

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


def test_create_and_read_lead_through_api(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    create_response = client.post(
        "/crm/leads",
        json={
            "name": "API Test Clinic",
            "category": "clinic",
            "phone": "+97450000001",
            "source": "API Test",
        },
    )

    assert create_response.status_code == 201

    created_lead = create_response.json()

    assert created_lead["name"] == (
        "API Test Clinic"
    )

    assert created_lead["status"] == "New"
    assert created_lead["priority"] == "Medium"

    lead_id = created_lead["id"]

    read_response = client.get(
        f"/crm/leads/{lead_id}"
    )

    assert read_response.status_code == 200
    assert read_response.json()["id"] == lead_id


def test_stage_update_creates_pipeline_history_through_api(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        api_environment
    )

    create_response = client.post(
        "/crm/leads",
        json={
            "name": "API Pipeline Test",
            "category": "clinic",
        },
    )

    assert create_response.status_code == 201

    lead_id = create_response.json()["id"]

    update_response = client.put(
        f"/crm/leads/{lead_id}",
        json={
            "status": "Contacted",
        },
    )

    assert update_response.status_code == 200
    assert (
        update_response.json()["status"]
        == "Contacted"
    )

    history_response = client.get(
        "/pipeline-activities",
        params={
            "lead_id": lead_id,
            "limit": 10,
        },
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["lead_id"] == lead_id
    assert (
        history[0]["previous_status"]
        == "New"
    )
    assert (
        history[0]["new_status"]
        == "Contacted"
    )
    assert (
        history[0]["source"]
        == "CRM Pipeline"
    )

    db: Session = session_factory()

    try:
        lead = db.get(Lead, lead_id)

        activity_count = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .count()
        )

        assert lead is not None
        assert lead.status == "Contacted"
        assert activity_count == 1
    finally:
        db.close()


def test_pipeline_summary_through_api(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    leads = [
        {
            "name": "New API Lead",
            "status": "New",
        },
        {
            "name": "Contacted API Lead",
            "status": "Contacted",
        },
        {
            "name": "Qualified API Lead",
            "status": "Qualified",
        },
    ]

    for lead_data in leads:
        create_response = client.post(
            "/crm/leads",
            json={
                "name": lead_data["name"],
                "category": "clinic",
            },
        )

        assert (
            create_response.status_code
            == 201
        )

        if lead_data["status"] != "New":
            lead_id = (
                create_response.json()["id"]
            )

            update_response = client.put(
                f"/crm/leads/{lead_id}",
                json={
                    "status": (
                        lead_data["status"]
                    ),
                },
            )

            assert (
                update_response.status_code
                == 200
            )

    summary_response = client.get(
        "/crm/pipeline/summary"
    )

    assert summary_response.status_code == 200

    summary = summary_response.json()

    assert summary["total_leads"] == 3
    assert summary["stages"]["new"] == 1
    assert summary["stages"]["contacted"] == 1
    assert summary["stages"]["qualified"] == 1
    assert summary["stages"]["won"] == 0
    assert summary["stages"]["lost"] == 0


def test_invalid_stage_returns_400(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    create_response = client.post(
        "/crm/leads",
        json={
            "name": "Invalid Stage Test",
        },
    )

    lead_id = create_response.json()["id"]

    response = client.put(
        f"/crm/leads/{lead_id}",
        json={
            "status": "Invalid Stage",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid lead status",
    }


def test_missing_lead_returns_404(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    response = client.get(
        "/crm/leads/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Lead not found",
    }
def test_create_lead_persists_contact_email(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = api_environment

    response = client.post(
        "/crm/leads",
        json={
            "name": "Email Contact Lead",
            "category": "consulting",
            "email": "contact@example.com",
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["email"] == "contact@example.com"

    lead_id = result["id"]

    db: Session = session_factory()

    try:
        lead = db.get(Lead, lead_id)

        assert lead is not None
        assert lead.email == "contact@example.com"
    finally:
        db.close()


def test_update_lead_contact_email(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    create_response = client.post(
        "/crm/leads",
        json={
            "name": "Updated Email Lead",
            "category": "consulting",
        },
    )

    assert create_response.status_code == 201

    lead_id = create_response.json()["id"]

    update_response = client.put(
        f"/crm/leads/{lead_id}",
        json={
            "email": "updated@example.com",
        },
    )

    assert update_response.status_code == 200
    assert (
        update_response.json()["email"]
        == "updated@example.com"
    )


def test_duplicate_lead_merges_missing_contact_email(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    first_response = client.post(
        "/crm/leads",
        json={
            "name": "Merge Email Lead",
            "category": "consulting",
        },
    )

    assert first_response.status_code == 201

    lead_id = first_response.json()["id"]

    duplicate_response = client.post(
        "/crm/leads",
        json={
            "name": "Merge Email Lead",
            "email": "merged@example.com",
        },
    )

    assert duplicate_response.status_code == 201

    result = duplicate_response.json()

    assert result["id"] == lead_id
    assert result["email"] == "merged@example.com"
