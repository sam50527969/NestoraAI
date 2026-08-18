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
from app.routes.dashboard import (
    router as dashboard_router,
)


@pytest.fixture
def dashboard_environment(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-dashboard-test.db"
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
    app.include_router(
        dashboard_router
    )

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


def add_lead(
    session_factory,
    *,
    name: str,
    status: str,
    priority: str,
    estimated_value: int | None,
    ai_score: int | None,
) -> None:
    db: Session = session_factory()

    try:
        db.add(
            Lead(
                name=name,
                category="clinic",
                status=status,
                priority=priority,
                estimated_value=(
                    estimated_value
                ),
                ai_score=ai_score,
            )
        )

        db.commit()
    finally:
        db.close()


def test_empty_dashboard_summary(
    dashboard_environment,
):
    client, _ = (
        dashboard_environment
    )

    response = client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["kpis"] == {
        "total_leads": 0,
        "high_priority_leads": 0,
        "qualified_leads": 0,
        "won_leads": 0,
        "pipeline_value": 0,
        "ai_score": 0,
    }

    assert data["pipeline"] == [
        {
            "label": "New",
            "value": 0,
        },
        {
            "label": "Contacted",
            "value": 0,
        },
        {
            "label": "Qualified",
            "value": 0,
        },
        {
            "label": "Proposal",
            "value": 0,
        },
        {
            "label": "Won",
            "value": 0,
        },
        {
            "label": "Lost",
            "value": 0,
        },
    ]


def test_dashboard_uses_live_crm_data(
    dashboard_environment,
):
    client, session_factory = (
        dashboard_environment
    )

    add_lead(
        session_factory,
        name="New Clinic",
        status="New",
        priority="High",
        estimated_value=1000,
        ai_score=80,
    )

    add_lead(
        session_factory,
        name="Qualified Clinic",
        status="Qualified",
        priority="High",
        estimated_value=2000,
        ai_score=100,
    )

    add_lead(
        session_factory,
        name="Won Clinic",
        status="Won",
        priority="Medium",
        estimated_value=5000,
        ai_score=90,
    )

    add_lead(
        session_factory,
        name="Lost Clinic",
        status="Lost",
        priority="Low",
        estimated_value=9000,
        ai_score=None,
    )

    response = client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["kpis"] == {
        "total_leads": 4,
        "high_priority_leads": 2,
        "qualified_leads": 1,
        "won_leads": 1,
        "pipeline_value": 8000,
        "ai_score": 90,
    }

    stage_counts = {
        stage["label"]: stage["value"]
        for stage in data["pipeline"]
    }

    assert stage_counts == {
        "New": 1,
        "Contacted": 0,
        "Qualified": 1,
        "Proposal": 0,
        "Won": 1,
        "Lost": 1,
    }


def test_lost_value_is_excluded(
    dashboard_environment,
):
    client, session_factory = (
        dashboard_environment
    )

    add_lead(
        session_factory,
        name="Lost Opportunity",
        status="Lost",
        priority="High",
        estimated_value=7500,
        ai_score=50,
    )

    response = client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["kpis"]["pipeline_value"]
        == 0
    )

    assert (
        data["kpis"]["total_leads"]
        == 1
    )


def test_negative_value_is_ignored(
    dashboard_environment,
):
    client, session_factory = (
        dashboard_environment
    )

    add_lead(
        session_factory,
        name="Invalid Value Lead",
        status="New",
        priority="Medium",
        estimated_value=-500,
        ai_score=None,
    )

    response = client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    assert (
        response.json()["kpis"][
            "pipeline_value"
        ]
        == 0
    )


def test_ai_score_uses_available_scores_only(
    dashboard_environment,
):
    client, session_factory = (
        dashboard_environment
    )

    add_lead(
        session_factory,
        name="Scored Lead",
        status="New",
        priority="Medium",
        estimated_value=None,
        ai_score=70,
    )

    add_lead(
        session_factory,
        name="Unscored Lead",
        status="Contacted",
        priority="Medium",
        estimated_value=None,
        ai_score=None,
    )

    response = client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    assert (
        response.json()["kpis"][
            "ai_score"
        ]
        == 70
    )


def test_dashboard_contains_operational_lists(
    dashboard_environment,
):
    client, _ = (
        dashboard_environment
    )

    response = client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["ai_brief"]) == 4
    assert len(data["tasks"]) == 4
    assert len(data["activity"]) == 4

    assert all(
        isinstance(item, str)
        and item.strip()
        for item in data["ai_brief"]
    )

    assert all(
        isinstance(item, str)
        and item.strip()
        for item in data["tasks"]
    )

    assert all(
        isinstance(item, str)
        and item.strip()
        for item in data["activity"]
    )