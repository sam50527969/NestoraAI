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

from app.business.access import get_current_business_uid
from app.database.database import Base
from app.database.models import Lead
from app.follow_up_activity import (
    service as follow_up_service,
)
from app.follow_up_activity.models import (
    FollowUpActivity,
)
from app.follow_up_activity.routes import (
    router as follow_up_router,
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
        / "follow-up-api-test.db"
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
        follow_up_service,
        "SessionLocal",
        session_factory,
    )

    monkeypatch.setattr(
        pipeline_service,
        "SessionLocal",
        session_factory,
    )

    app = FastAPI()
    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_atlas"
    app.include_router(follow_up_router)

    with TestClient(app) as client:
        yield client, session_factory

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_test_lead(
    session_factory: sessionmaker,
    *,
    name: str,
    status: str = "Contacted",
) -> int:
    db: Session = session_factory()

    try:
        lead = Lead(
            name=name,
            category="clinic",
            status=status,
            priority="High",
            business_uid="biz_atlas",
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead.id
    finally:
        db.close()


def test_record_outcome_and_read_history(
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
        name="Follow-up API Clinic",
    )

    response = client.post(
        (
            "/follow-up-activities/"
            f"leads/{lead_id}/outcome"
        ),
        json={
            "outcome": "qualified",
            "notes": (
                "Qualified through API test."
            ),
            "completed_by": "CEO",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["lead_id"] == lead_id
    assert result["outcome"] == "qualified"
    assert (
        result["previous_status"]
        == "Contacted"
    )
    assert (
        result["new_status"]
        == "Qualified"
    )

    history_response = client.get(
        "/follow-up-activities",
        params={
            "lead_id": lead_id,
            "limit": 10,
        },
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert (
        history[0]["activity_uid"]
        == result["activity_uid"]
    )

    db: Session = session_factory()

    try:
        lead = db.get(Lead, lead_id)

        follow_up_count = (
            db.query(FollowUpActivity)
            .filter(
                FollowUpActivity.lead_id
                == lead_id
            )
            .count()
        )

        pipeline_count = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .count()
        )

        assert lead is not None
        assert lead.status == "Qualified"
        assert follow_up_count == 1
        assert pipeline_count == 1
    finally:
        db.close()


def test_reschedule_requires_next_date(
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
        name="Reschedule API Test",
    )

    response = client.post(
        (
            "/follow-up-activities/"
            f"leads/{lead_id}/outcome"
        ),
        json={
            "outcome": "rescheduled",
            "notes": "Call again later.",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "A new follow-up date is "
            "required when rescheduling."
        ),
    }


def test_missing_lead_returns_404(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, _ = api_environment

    response = client.post(
        (
            "/follow-up-activities/"
            "leads/999999/outcome"
        ),
        json={
            "outcome": "contacted",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "CRM lead was not found."
        ),
    }


def test_follow_up_metrics_through_api(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = (
        api_environment
    )

    qualified_id = create_test_lead(
        session_factory,
        name="Qualified Metrics Lead",
    )

    no_response_id = create_test_lead(
        session_factory,
        name="No Response Metrics Lead",
    )

    rescheduled_id = create_test_lead(
        session_factory,
        name="Rescheduled Metrics Lead",
    )

    responses = [
        client.post(
            (
                "/follow-up-activities/"
                f"leads/{qualified_id}/outcome"
            ),
            json={
                "outcome": "qualified",
            },
        ),
        client.post(
            (
                "/follow-up-activities/"
                f"leads/{no_response_id}/outcome"
            ),
            json={
                "outcome": "no_response",
            },
        ),
        client.post(
            (
                "/follow-up-activities/"
                f"leads/{rescheduled_id}/outcome"
            ),
            json={
                "outcome": "rescheduled",
                "next_follow_up": (
                    "2026-08-20T09:00:00"
                ),
            },
        ),
    ]

    assert all(
        response.status_code == 200
        for response in responses
    )

    metrics_response = client.get(
        "/follow-up-activities/metrics"
    )

    assert metrics_response.status_code == 200

    metrics = metrics_response.json()

    assert metrics["total_activities"] == 3
    assert metrics["unique_leads"] == 3
    assert metrics["response_count"] == 1
    assert metrics["response_rate"] == 50
    assert metrics["win_rate"] == 0

    assert (
        metrics["outcomes"]["qualified"]
        == 1
    )

    assert (
        metrics["outcomes"]["no_response"]
        == 1
    )

    assert (
        metrics["outcomes"]["rescheduled"]
        == 1
    )


def test_csv_export_is_downloadable_and_safe(
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
        name="=Formula Test Clinic",
    )

    outcome_response = client.post(
        (
            "/follow-up-activities/"
            f"leads/{lead_id}/outcome"
        ),
        json={
            "outcome": "contacted",
            "notes": "=SUM(1,1)",
            "completed_by": "CEO",
        },
    )

    assert outcome_response.status_code == 200

    export_response = client.get(
        "/follow-up-activities/export",
        params={
            "lead_id": lead_id,
            "limit": 10,
        },
    )

    assert export_response.status_code == 200

    assert (
        export_response.headers[
            "content-type"
        ].startswith("text/csv")
    )

    assert (
        "nestora-follow-up-history.csv"
        in export_response.headers[
            "content-disposition"
        ]
    )

    csv_content = export_response.text

    assert "Activity UID" in csv_content
    assert "'=Formula Test Clinic" in (
        csv_content
    )
    assert "'=SUM(1,1)" in csv_content

def test_follow_up_isolated_by_workspace(
    api_environment: tuple[
        TestClient,
        sessionmaker,
    ],
) -> None:
    client, session_factory = api_environment

    db: Session = session_factory()

    try:
        atlas_lead = Lead(
            name="Atlas Follow-up Lead",
            category="auto repair",
            status="Contacted",
            priority="High",
            business_uid="biz_atlas",
        )

        dental_lead = Lead(
            name="Dental Follow-up Lead",
            category="dental",
            status="Contacted",
            priority="High",
            business_uid="biz_dental",
        )

        db.add_all([
            atlas_lead,
            dental_lead,
        ])
        db.commit()
        db.refresh(atlas_lead)
        db.refresh(dental_lead)

        atlas_activity = FollowUpActivity(
            lead_id=atlas_lead.id,
            lead_name=atlas_lead.name,
            outcome="qualified",
            previous_status="Contacted",
            new_status="Qualified",
            completed_by="CEO",
        )

        dental_activity = FollowUpActivity(
            lead_id=dental_lead.id,
            lead_name=dental_lead.name,
            outcome="won",
            previous_status="Contacted",
            new_status="Won",
            completed_by="CEO",
        )

        db.add_all([
            atlas_activity,
            dental_activity,
        ])
        db.commit()

        dental_lead_id = dental_lead.id

    finally:
        db.close()

    history_response = client.get(
        "/follow-up-activities"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert (
        history[0]["lead_name"]
        == "Atlas Follow-up Lead"
    )
    assert history[0]["outcome"] == "qualified"

    foreign_history = client.get(
        "/follow-up-activities",
        params={
            "lead_id": dental_lead_id,
        },
    )

    assert foreign_history.status_code == 200
    assert foreign_history.json() == []

    metrics_response = client.get(
        "/follow-up-activities/metrics"
    )

    assert metrics_response.status_code == 200

    metrics = metrics_response.json()

    assert metrics["total_activities"] == 1
    assert metrics["unique_leads"] == 1
    assert metrics["outcomes"]["qualified"] == 1
    assert metrics["outcomes"]["won"] == 0

    export_response = client.get(
        "/follow-up-activities/export"
    )

    assert export_response.status_code == 200

    csv_content = export_response.text

    assert "Atlas Follow-up Lead" in csv_content
    assert "Dental Follow-up Lead" not in csv_content

    foreign_export = client.get(
        "/follow-up-activities/export",
        params={
            "lead_id": dental_lead_id,
        },
    )

    assert foreign_export.status_code == 200
    assert (
        "Dental Follow-up Lead"
        not in foreign_export.text
    )

    foreign_outcome = client.post(
        (
            "/follow-up-activities/"
            f"leads/{dental_lead_id}/outcome"
        ),
        json={
            "outcome": "won",
            "notes": (
                "Atlas must not modify Dental."
            ),
        },
    )

    assert foreign_outcome.status_code == 404

    db = session_factory()

    try:
        dental_lead = db.get(
            Lead,
            dental_lead_id,
        )

        dental_activity_count = (
            db.query(FollowUpActivity)
            .filter(
                FollowUpActivity.lead_id
                == dental_lead_id
            )
            .count()
        )

        assert dental_lead is not None
        assert dental_lead.status == "Contacted"
        assert dental_activity_count == 1

    finally:
        db.close()
