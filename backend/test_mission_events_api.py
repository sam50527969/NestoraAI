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
from app.business.access import get_current_business_uid
from app.database.models import (
    MissionEvent,
)
from app.repositories.mission_event_repository import (
    MissionEventRepository,
)
from app.repositories.mission_repository import (
    MissionRepository,
)
from app.routes.mission_events import (
    router as mission_events_router,
)


@pytest.fixture
def mission_events_environment(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-mission-events.db"
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
        mission_events_router
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
    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_timeline_test"

    with TestClient(app) as client:
        yield client, session_factory

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )
    engine.dispose()


def create_mission(
    session_factory,
) -> str:
    db: Session = session_factory()

    try:
        mission = MissionRepository(
            db
        ).create(
            business_uid=(
                "biz_timeline_test"
            ),
            title="Timeline Test",
            objective=(
                "Test mission events."
            ),
        )

        return mission.mission_uid
    finally:
        db.close()


def test_empty_timeline_returns_200(
    mission_events_environment,
):
    client, session_factory = (
        mission_events_environment
    )

    mission_uid = create_mission(
        session_factory
    )

    response = client.get(
        f"/missions/{mission_uid}/events"
    )

    assert response.status_code == 200


def test_other_workspace_timeline_returns_404(
    mission_events_environment,
):
    client, session_factory = mission_events_environment
    db: Session = session_factory()
    try:
        mission = MissionRepository(db).create(
            business_uid="biz_other",
            title="Private timeline",
            objective="Remain private",
        )
        mission_uid = mission.mission_uid
    finally:
        db.close()

    response = client.get(
        f"/missions/{mission_uid}/events"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Persisted mission not found.",
    }

    assert response.json() == {
        "mission_uid": mission_uid,
        "count": 0,
        "events": [],
    }


def test_missing_mission_returns_404(
    mission_events_environment,
):
    client, _ = (
        mission_events_environment
    )

    response = client.get(
        "/missions/mis_missing/events"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "Persisted mission not found."
        ),
    }


def test_returns_events_in_creation_order(
    mission_events_environment,
):
    client, session_factory = (
        mission_events_environment
    )

    mission_uid = create_mission(
        session_factory
    )

    db: Session = session_factory()

    try:
        repository = (
            MissionEventRepository(db)
        )

        first_event = (
            repository.create_event(
                mission_uid=mission_uid,
                executive="CEO Agent",
                event_type=(
                    "mission_started"
                ),
                status="running",
                message="Mission started.",
                metadata={
                    "task_count": 2,
                },
            )
        )

        first_event_uid = (
            first_event.event_uid
        )

        second_event = (
            repository.create_event(
                mission_uid=mission_uid,
                executive=(
                    "Research Agent"
                ),
                event_type=(
                    "task_completed"
                ),
                status="completed",
                message=(
                    "Business research "
                    "completed."
                ),
                metadata={
                    "results": 10,
                },
            )
        )

        second_event_uid = (
            second_event.event_uid
        )
    finally:
        db.close()

    response = client.get(
        f"/missions/{mission_uid}/events"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2

    assert [
        event["event_uid"]
        for event in data["events"]
    ] == [
        first_event_uid,
        second_event_uid,
    ]

    assert data["events"][0] == {
        "event_uid": first_event_uid,
        "executive": "CEO Agent",
        "event_type": (
            "mission_started"
        ),
        "status": "running",
        "message": "Mission started.",
        "metadata": {
            "task_count": 2,
        },
        "created_at": (
            data["events"][0][
                "created_at"
            ]
        ),
    }

    assert (
        data["events"][1]["metadata"]
        == {
            "results": 10,
        }
    )


def test_timeline_pagination(
    mission_events_environment,
):
    client, session_factory = (
        mission_events_environment
    )

    mission_uid = create_mission(
        session_factory
    )

    db: Session = session_factory()

    try:
        repository = (
            MissionEventRepository(db)
        )

        repository.create_event(
            mission_uid=mission_uid,
            executive="CEO Agent",
            event_type="first",
            message="First event.",
        )

        second_event = (
            repository.create_event(
                mission_uid=mission_uid,
                executive="CEO Agent",
                event_type="second",
                message="Second event.",
            )
        )

        second_event_uid = (
            second_event.event_uid
        )
    finally:
        db.close()

    response = client.get(
        f"/missions/{mission_uid}/events",
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["events"]) == 1

    assert (
        data["events"][0]["event_uid"]
        == second_event_uid
    )


@pytest.mark.parametrize(
    "params",
    [
        {
            "limit": 0,
        },
        {
            "limit": 501,
        },
        {
            "offset": -1,
        },
    ],
)
def test_rejects_invalid_pagination(
    mission_events_environment,
    params,
):
    client, session_factory = (
        mission_events_environment
    )

    mission_uid = create_mission(
        session_factory
    )

    response = client.get(
        f"/missions/{mission_uid}/events",
        params=params,
    )

    assert response.status_code == 422


def test_invalid_metadata_returns_none(
    mission_events_environment,
):
    client, session_factory = (
        mission_events_environment
    )

    mission_uid = create_mission(
        session_factory
    )

    db: Session = session_factory()

    try:
        event = MissionEvent(
            mission_uid=mission_uid,
            executive="CEO Agent",
            event_type="invalid_metadata",
            status="info",
            message=(
                "Invalid metadata test."
            ),
            metadata_json=(
                "not-valid-json"
            ),
        )

        db.add(event)
        db.commit()
    finally:
        db.close()

    response = client.get(
        f"/missions/{mission_uid}/events"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1

    assert (
        data["events"][0]["metadata"]
        is None
    )
