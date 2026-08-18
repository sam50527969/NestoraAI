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
from app.repositories.agent_task_repository import (
    AgentTaskRepository,
)
from app.repositories.mission_repository import (
    MissionRepository,
)
from app.routes import (
    mission as mission_routes,
)
from app.routes.mission import (
    router as mission_router,
)


@pytest.fixture
def mission_api_environment(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-mission-api-test.db"
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
        mission_router
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


def mission_status_payload(
    mission_id: str,
) -> dict:
    return {
        "mission_id": mission_id,
        "status": "queued",
        "progress": 0,
        "current_step": (
            "Preparing mission"
        ),
        "searched": 0,
        "analyzed": 0,
        "outreach_generated": 0,
        "agents": [],
        "activity": [],
    }


def test_start_mission(
    mission_api_environment,
    monkeypatch,
):
    client, _ = (
        mission_api_environment
    )

    expected = mission_status_payload(
        "mission-test-001"
    )

    def fake_create_mission():
        return expected.copy()

    async def fake_run_real_mission(
        mission_id,
        request,
    ):
        return {
            "mission_id": mission_id,
            "status": "completed",
        }

    monkeypatch.setattr(
        mission_routes,
        "create_mission",
        fake_create_mission,
    )

    monkeypatch.setattr(
        mission_routes,
        "run_real_mission",
        fake_run_real_mission,
    )

    response = client.post(
        "/missions/start",
        json={
            "business_type": " clinic ",
            "location": " Doha ",
            "quantity": 10,
            "minimum_quality": 70,
            "priority_filter": "HIGH",
        },
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "business_type": "",
            "location": "Doha",
        },
        {
            "business_type": "clinic",
            "location": "   ",
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "quantity": 0,
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "quantity": 101,
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "minimum_quality": -1,
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "minimum_quality": 101,
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "priority_filter": "urgent",
        },
    ],
)
def test_start_rejects_invalid_payload(
    mission_api_environment,
    payload,
):
    client, _ = (
        mission_api_environment
    )

    response = client.post(
        "/missions/start",
        json=payload,
    )

    assert response.status_code == 422


def test_get_async_mission_status(
    mission_api_environment,
    monkeypatch,
):
    client, _ = (
        mission_api_environment
    )

    expected = mission_status_payload(
        "mission-status-001"
    )

    expected["status"] = "running"
    expected["progress"] = 45
    expected["searched"] = 8

    monkeypatch.setattr(
        mission_routes,
        "get_mission",
        lambda mission_id: (
            expected.copy()
        ),
    )

    response = client.get(
        "/missions/mission-status-001"
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_missing_async_mission_returns_404(
    mission_api_environment,
    monkeypatch,
):
    client, _ = (
        mission_api_environment
    )

    monkeypatch.setattr(
        mission_routes,
        "get_mission",
        lambda mission_id: None,
    )

    response = client.get(
        "/missions/missing-mission"
    )

    assert response.status_code == 404
    assert (
        "Mission not found"
        in response.json()["detail"]
    )


def create_persisted_mission(
    session_factory,
):
    db: Session = session_factory()

    try:
        repository = MissionRepository(
            db
        )

        return repository.create(
            business_uid="biz_test_001",
            objective_uid=(
                "obj_test_001"
            ),
            title="Grow clinic leads",
            objective=(
                "Find qualified clinics "
                "in Doha."
            ),
            description=(
                "Mission API test record."
            ),
            priority="high",
            estimated_value=5000,
            expected_roi=2.5,
            strategy_data={
                "channel": "search",
            },
            metadata={
                "created_by": "test",
            },
        )
    finally:
        db.close()


def test_list_persisted_missions(
    mission_api_environment,
):
    client, session_factory = (
        mission_api_environment
    )

    mission = (
        create_persisted_mission(
            session_factory
        )
    )

    response = client.get(
        "/missions",
        params={
            "limit": 10,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["missions"]) == 1

    returned = data["missions"][0]

    assert (
        returned["mission_uid"]
        == mission.mission_uid
    )
    assert (
        returned["business_uid"]
        == "biz_test_001"
    )
    assert (
        returned["strategy_data"]
        == {
            "channel": "search",
        }
    )
    assert returned["metadata"] == {
        "created_by": "test",
    }


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
def test_list_rejects_invalid_pagination(
    mission_api_environment,
    params,
):
    client, _ = (
        mission_api_environment
    )

    response = client.get(
        "/missions",
        params=params,
    )

    assert response.status_code == 422


def test_list_persisted_tasks(
    mission_api_environment,
):
    client, session_factory = (
        mission_api_environment
    )

    mission = (
        create_persisted_mission(
            session_factory
        )
    )

    mission_uid = (
        mission.mission_uid
    )

    db: Session = session_factory()

    try:
        task_repository = (
            AgentTaskRepository(db)
        )

        first_task = (
            task_repository.create(
                mission_id=mission_uid,
                executive="Research Agent",
                title="Find clinics",
                description=(
                    "Search for clinics."
                ),
                sequence_number=1,
                input_data={
                    "location": "Doha",
                },
            )
        )

        first_task_uid = (
            first_task.task_uid
        )

        second_task = (
            task_repository.create(
                mission_id=mission_uid,
                executive="Sales Agent",
                title="Score clinics",
                description=(
                    "Score discovered leads."
                ),
                sequence_number=2,
                depends_on=(
                    first_task_uid
                ),
            )
        )

        second_task_uid = (
            second_task.task_uid
        )
    finally:
        db.close()

    response = client.get(
        (
            f"/missions/"
            f"{mission_uid}/tasks"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2

    assert [
        task["task_uid"]
        for task in data["tasks"]
    ] == [
        first_task_uid,
        second_task_uid,
    ]

    assert (
        data["tasks"][0]["input_data"]
        == {
            "location": "Doha",
        }
    )

    assert (
        data["tasks"][1][
            "depends_on_task_uid"
        ]
        == first_task_uid
    )


def test_missing_persisted_mission_tasks_returns_404(
    mission_api_environment,
):
    client, _ = (
        mission_api_environment
    )

    response = client.get(
        "/missions/mis_missing/tasks"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "Persisted mission not found."
        ),
    }


def test_execute_persisted_mission(
    mission_api_environment,
    monkeypatch,
):
    client, _ = (
        mission_api_environment
    )

    class FakeOrchestrator:
        def __init__(
            self,
            db,
        ):
            self.db = db

        def execute_mission(
            self,
            mission_uid,
        ):
            return {
                "mission_uid": (
                    mission_uid
                ),
                "status": "completed",
                "completed_tasks": 2,
            }

    monkeypatch.setattr(
        mission_routes,
        "WorkforceOrchestrator",
        FakeOrchestrator,
    )

    response = client.post(
        "/missions/mis_execute/execute"
    )

    assert response.status_code == 200

    assert response.json() == {
        "mission_uid": "mis_execute",
        "status": "completed",
        "completed_tasks": 2,
    }