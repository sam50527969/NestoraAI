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

from app.database.database import Base
from app.database.models import Lead
from app.outreach_activity import (
    service as outreach_service,
)
from app.outreach_activity.models import (
    OutreachActivity,
)
from app.outreach_activity.routes import (
    router as outreach_router,
)
from app.pipeline_activity import (
    service as pipeline_service,
)
from app.pipeline_activity.models import (
    PipelineActivity,
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
        / "outreach-api-test.db"
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
        outreach_service,
        "SessionLocal",
        session_factory,
    )

    monkeypatch.setattr(
        pipeline_service,
        "SessionLocal",
        session_factory,
    )

    app = FastAPI()
    app.include_router(outreach_router)

    with TestClient(app) as client:
        yield client, session_factory

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_test_lead(
    session_factory: sessionmaker,
    *,
    name: str,
    status: str = "New",
) -> int:
    db: Session = session_factory()

    try:
        lead = Lead(
            name=name,
            category="clinic",
            status=status,
            priority="High",
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead.id
    finally:
        db.close()


def create_outreach_activity(
    session_factory: sessionmaker,
    *,
    lead_id: int,
    lead_name: str,
    status: str = "prepared",
    approval_uid: str = "approval-api-test",
) -> str:
    db: Session = session_factory()

    try:
        activity = OutreachActivity(
            approval_uid=approval_uid,
            lead_id=lead_id,
            lead_name=lead_name,
            status=status,
            prepared_by="CEO Agent",
            phone="+97450000001",
            website="https://example.com",
            email_subject="API Test",
            email_body="API test message",
            whatsapp_message=(
                "API test WhatsApp message"
            ),
            cold_call_script=(
                "API test call script"
            ),
            proposal_summary=(
                "API test proposal"
            ),
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity.activity_uid
    finally:
        db.close()


def test_list_and_get_prepared_outreach(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        api_environment
    )

    lead_name = "Outreach API Clinic"

    lead_id = create_test_lead(
        session_factory,
        name=lead_name,
    )

    activity_uid = create_outreach_activity(
        session_factory,
        lead_id=lead_id,
        lead_name=lead_name,
    )

    list_response = client.get(
        "/outreach-activities",
        params={
            "status": "prepared",
            "limit": 10,
        },
    )

    assert list_response.status_code == 200

    activities = list_response.json()

    assert len(activities) == 1
    assert (
        activities[0]["activity_uid"]
        == activity_uid
    )
    assert activities[0]["status"] == "prepared"

    get_response = client.get(
        (
            "/outreach-activities/"
            f"{activity_uid}"
        )
    )

    assert get_response.status_code == 200

    activity = get_response.json()

    assert activity["lead_id"] == lead_id
    assert activity["lead_name"] == lead_name
    assert activity["status"] == "prepared"


def test_list_filters_by_approval_uid(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        api_environment
    )

    lead_id = create_test_lead(
        session_factory,
        name="Approval Filter Clinic",
    )

    create_outreach_activity(
        session_factory,
        lead_id=lead_id,
        lead_name="Approval Filter Clinic",
        approval_uid="approval-one",
    )

    create_outreach_activity(
        session_factory,
        lead_id=lead_id,
        lead_name="Approval Filter Clinic",
        approval_uid="approval-two",
    )

    response = client.get(
        "/outreach-activities",
        params={
            "approval_uid": "approval-two",
        },
    )

    assert response.status_code == 200

    activities = response.json()

    assert len(activities) == 1
    assert (
        activities[0]["approval_uid"]
        == "approval-two"
    )


def test_mark_sent_updates_lead_and_pipeline(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        api_environment
    )

    lead_name = "Sent Outreach API Clinic"

    lead_id = create_test_lead(
        session_factory,
        name=lead_name,
    )

    activity_uid = create_outreach_activity(
        session_factory,
        lead_id=lead_id,
        lead_name=lead_name,
    )

    response = client.post(
        (
            "/outreach-activities/"
            f"{activity_uid}/mark-sent"
        )
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "sent"
    assert result["sent_at"] is not None

    db: Session = session_factory()

    try:
        lead = db.get(Lead, lead_id)

        pipeline_activity = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .one()
        )

        assert lead is not None
        assert lead.status == "Contacted"
        assert lead.last_contacted is not None
        assert lead.next_follow_up is not None

        assert (
            pipeline_activity.previous_status
            == "New"
        )
        assert (
            pipeline_activity.new_status
            == "Contacted"
        )
        assert (
            pipeline_activity.source
            == "Sent Outreach"
        )
        assert (
            pipeline_activity.changed_by
            == "CEO Agent"
        )
    finally:
        db.close()


def test_missing_activity_returns_404(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    get_response = client.get(
        "/outreach-activities/out_missing"
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": (
            "Outreach activity was "
            "not found."
        ),
    }

    mark_response = client.post(
        (
            "/outreach-activities/"
            "out_missing/mark-sent"
        )
    )

    assert mark_response.status_code == 404


def test_invalid_activity_state_returns_409(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        api_environment
    )

    lead_id = create_test_lead(
        session_factory,
        name="Invalid Outreach State",
    )

    activity_uid = create_outreach_activity(
        session_factory,
        lead_id=lead_id,
        lead_name="Invalid Outreach State",
        status="cancelled",
    )

    response = client.post(
        (
            "/outreach-activities/"
            f"{activity_uid}/mark-sent"
        )
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Only prepared outreach can be "
            "marked as sent."
        ),
    }