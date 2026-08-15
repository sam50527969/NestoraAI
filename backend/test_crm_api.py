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
from app.database.models import Lead
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