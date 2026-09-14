import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import User
from app.bootstrap.routes import register_routes
from app.database.database import Base, get_db
from app.database.models import (
    Business,
    BusinessMembership,
)
from app.repositories.agent_task_repository import (
    AgentTaskRepository,
)
from app.repositories.mission_repository import (
    MissionRepository,
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


TEST_EMAIL = "task-security@nestora.test"
TEST_PASSWORD = "StrongPassword123!"

WORKSPACE_A = "biz_task_security_a"
WORKSPACE_B = "biz_task_security_b"


@pytest.fixture
def task_security_api(
    tmp_path: Path,
) -> Generator[TestClient, None, None]:
    database_path = (
        tmp_path
        / "nestora-task-security.db"
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

    app = FastAPI()
    register_routes(app)

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
        client.session_factory = (
            session_factory
        )
        yield client

    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def register_login_and_create_workspaces(
    client: TestClient,
):
    registration = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "full_name":
                "Task Security User",
            "password": TEST_PASSWORD,
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    session_factory = client.session_factory

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == TEST_EMAIL
            )
            .one()
        )

        db.add_all(
            [
                Business(
                    business_uid=WORKSPACE_A,
                    name="Task Security A",
                    industry="other",
                    country="Qatar",
                    currency="QAR",
                ),
                Business(
                    business_uid=WORKSPACE_B,
                    name="Task Security B",
                    industry="other",
                    country="Qatar",
                    currency="QAR",
                ),
            ]
        )

        db.add_all(
            [
                BusinessMembership(
                    membership_uid=(
                        "mem_task_security_a"
                    ),
                    user_uid=user.user_uid,
                    business_uid=WORKSPACE_A,
                    role="owner",
                    is_active=True,
                ),
                BusinessMembership(
                    membership_uid=(
                        "mem_task_security_b"
                    ),
                    user_uid=user.user_uid,
                    business_uid=WORKSPACE_B,
                    role="owner",
                    is_active=True,
                ),
            ]
        )

        db.commit()

    return token


def headers_for(
    token: str,
    business_uid: str,
):
    return {
        "Authorization":
            f"Bearer {token}",
        "X-Business-Uid":
            business_uid,
    }


def create_mission_and_task(
    client: TestClient,
    *,
    business_uid: str,
    mission_title: str,
    task_title: str,
):
    session_factory = client.session_factory

    with session_factory() as db:
        mission = MissionRepository(db).create(
            business_uid=business_uid,
            title=mission_title,
            objective=(
                f"Objective for {mission_title}"
            ),
        )

        mission_uid = mission.mission_uid

        task = AgentTaskRepository(db).create(
            mission_id=mission_uid,
            executive="Research Agent",
            title=task_title,
            description=(
                f"Description for {task_title}"
            ),
            sequence_number=1,
        )

        task_uid = task.task_uid

    return mission_uid, task_uid


@pytest.mark.parametrize(
    "path",
    [
        "/agent-tasks",
        "/agent-tasks/missions/missing",
        "/mission-scheduler/missing/summary",
    ],
)
def test_task_surfaces_require_authentication(
    task_security_api: TestClient,
    path: str,
):
    response = task_security_api.get(path)

    assert response.status_code == 401
    assert (
        response.headers["www-authenticate"]
        == "Bearer"
    )


def test_global_task_list_is_workspace_scoped(
    task_security_api: TestClient,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    mission_a, task_a = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_A,
            mission_title="Mission A",
            task_title="Task A",
        )
    )

    _, task_b = create_mission_and_task(
        task_security_api,
        business_uid=WORKSPACE_B,
        mission_title="Mission B",
        task_title="Task B",
    )

    response = task_security_api.get(
        "/agent-tasks",
        headers=headers_for(
            token,
            WORKSPACE_A,
        ),
    )

    assert response.status_code == 200

    returned = response.json()
    returned_uids = {
        task["task_uid"]
        for task in returned
    }

    assert task_a in returned_uids
    assert task_b not in returned_uids

    assert {
        task["mission_id"]
        for task in returned
    } == {mission_a}


def test_foreign_task_read_returns_404(
    task_security_api: TestClient,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    _, foreign_task = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_B,
            mission_title="Private Mission",
            task_title="Private Task",
        )
    )

    response = task_security_api.get(
        f"/agent-tasks/{foreign_task}",
        headers=headers_for(
            token,
            WORKSPACE_A,
        ),
    )

    assert response.status_code == 404


def test_foreign_task_mutation_returns_404(
    task_security_api: TestClient,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    _, foreign_task = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_B,
            mission_title="Private Mission",
            task_title="Private Task",
        )
    )

    response = task_security_api.post(
        f"/agent-tasks/{foreign_task}/start",
        headers=headers_for(
            token,
            WORKSPACE_A,
        ),
    )

    assert response.status_code == 404

    session_factory = (
        task_security_api.session_factory
    )

    with session_factory() as db:
        task = (
            AgentTaskRepository(db)
            .get_by_uid(foreign_task)
        )

        assert task is not None
        assert task.status == "pending"


def test_foreign_mission_task_list_returns_404(
    task_security_api: TestClient,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    foreign_mission, _ = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_B,
            mission_title="Private Mission",
            task_title="Private Task",
        )
    )

    response = task_security_api.get(
        (
            "/agent-tasks/missions/"
            f"{foreign_mission}"
        ),
        headers=headers_for(
            token,
            WORKSPACE_A,
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail":
            "Persisted mission not found.",
    }


@pytest.mark.parametrize(
    "suffix",
    [
        "summary",
        "next",
        "ready",
    ],
)
def test_foreign_scheduler_mission_returns_404(
    task_security_api: TestClient,
    suffix: str,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    foreign_mission, _ = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_B,
            mission_title="Private Mission",
            task_title="Private Task",
        )
    )

    response = task_security_api.get(
        (
            "/mission-scheduler/"
            f"{foreign_mission}/{suffix}"
        ),
        headers=headers_for(
            token,
            WORKSPACE_A,
        ),
    )

    assert response.status_code == 404


def test_foreign_mission_cannot_receive_new_task(
    task_security_api: TestClient,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    foreign_mission, _ = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_B,
            mission_title="Private Mission",
            task_title="Existing Task",
        )
    )

    session_factory = (
        task_security_api.session_factory
    )

    with session_factory() as db:
        before = len(
            AgentTaskRepository(db)
            .list_by_mission(
                foreign_mission
            )
        )

    response = task_security_api.post(
        "/agent-tasks",
        headers=headers_for(
            token,
            WORKSPACE_A,
        ),
        json={
            "mission_id": foreign_mission,
            "agent_name": "Sales Agent",
            "task_type": "outreach",
            "title": "Unauthorized Task",
            "description":
                "Must never be created.",
            "priority": "high",
            "sequence_number": 2,
        },
    )

    assert response.status_code == 404

    with session_factory() as db:
        after = len(
            AgentTaskRepository(db)
            .list_by_mission(
                foreign_mission
            )
        )

    assert after == before


def test_valid_workspace_task_and_scheduler_access(
    task_security_api: TestClient,
):
    token = (
        register_login_and_create_workspaces(
            task_security_api
        )
    )

    mission_uid, task_uid = (
        create_mission_and_task(
            task_security_api,
            business_uid=WORKSPACE_A,
            mission_title="Owned Mission",
            task_title="Owned Task",
        )
    )

    headers = headers_for(
        token,
        WORKSPACE_A,
    )

    task_response = task_security_api.get(
        f"/agent-tasks/{task_uid}",
        headers=headers,
    )

    assert task_response.status_code == 200
    assert (
        task_response.json()["task_uid"]
        == task_uid
    )

    mission_response = task_security_api.get(
        (
            "/agent-tasks/missions/"
            f"{mission_uid}"
        ),
        headers=headers,
    )

    assert mission_response.status_code == 200
    assert {
        task["task_uid"]
        for task in mission_response.json()
    } == {task_uid}

    summary_response = task_security_api.get(
        (
            "/mission-scheduler/"
            f"{mission_uid}/summary"
        ),
        headers=headers,
    )

    assert summary_response.status_code == 200
