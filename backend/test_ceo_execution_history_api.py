import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
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

from app.bootstrap.routes import (
    register_routes,
)
from app.business.access import (
    get_current_business_uid,
)
from app.database.database import (
    Base,
    get_db,
)
from app.execution_history.models import (
    CEOExecutionRecord,
)
from app.execution_history.service import (
    save_execution_record,
)


TEST_EMAIL = "execution-history@nestora.test"
TEST_PASSWORD = "StrongPassword123!"


@pytest.fixture
def execution_history_api(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-execution-history-api.db"
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

    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_atlas"

    with TestClient(app) as client:
        yield client, session_factory

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )

    engine.dispose()


def register_and_login(
    client: TestClient,
) -> str:
    registration = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "full_name":
                "Execution History User",
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

    return login.json()["access_token"]


def auth_headers(
    client: TestClient,
) -> dict[str, str]:
    token = register_and_login(
        client
    )

    return {
        "Authorization":
            f"Bearer {token}",
    }


def create_execution(
    session_factory: sessionmaker,
    *,
    approval_uid: str,
    mission_id: str = "mission-test",
    workflow_id: str = "workflow-test",
    success: bool = True,
):
    db: Session = session_factory()

    try:
        record = save_execution_record(
            db,
            approval_uid=approval_uid,
            business_uid="biz_atlas",
            objective="Test CEO objective",
            execution_result={
                "success": success,
                "status": (
                    "completed"
                    if success
                    else "failed"
                ),
                "mission_id": mission_id,
                "workflow_id": workflow_id,
                "completed_task_count": (
                    3 if success else 1
                ),
                "failed_task_count": (
                    0 if success else 2
                ),
            },
        )

        db.commit()
        db.refresh(record)

        execution_uid = (
            record.execution_uid
        )

        return execution_uid
    finally:
        db.close()


@pytest.mark.parametrize(
    "path",
    [
        "/ceo-executions",
        "/ceo-executions/missing-execution",
        (
            "/ceo-executions/approval/"
            "missing-approval"
        ),
    ],
)
def test_execution_history_requires_authentication(
    execution_history_api,
    path: str,
) -> None:
    client, _ = execution_history_api

    response = client.get(path)

    assert response.status_code == 401

    assert (
        response.headers[
            "www-authenticate"
        ]
        == "Bearer"
    )


def test_execution_history_list(
    execution_history_api,
) -> None:
    client, session_factory = (
        execution_history_api
    )

    create_execution(
        session_factory,
        approval_uid="approval-list-1",
    )

    create_execution(
        session_factory,
        approval_uid="approval-list-2",
    )

    headers = auth_headers(client)

    response = client.get(
        "/ceo-executions",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["limit"] == 50
    assert data["offset"] == 0
    assert len(data["executions"]) == 2


def test_execution_detail_by_execution_uid(
    execution_history_api,
) -> None:
    client, session_factory = (
        execution_history_api
    )

    execution_uid = create_execution(
        session_factory,
        approval_uid="approval-detail",
        mission_id="mission-detail",
        workflow_id="workflow-detail",
    )

    headers = auth_headers(client)

    response = client.get(
        f"/ceo-executions/{execution_uid}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["execution_uid"]
        == execution_uid
    )
    assert (
        data["approval_uid"]
        == "approval-detail"
    )
    assert (
        data["mission_id"]
        == "mission-detail"
    )
    assert (
        data["workflow_id"]
        == "workflow-detail"
    )
    assert data["success"] is True
    assert data["status"] == "completed"

    assert data["result"] is not None
    assert (
        data["result"]["mission_id"]
        == "mission-detail"
    )


def test_execution_detail_by_approval_uid(
    execution_history_api,
) -> None:
    client, session_factory = (
        execution_history_api
    )

    execution_uid = create_execution(
        session_factory,
        approval_uid="approval-lookup",
    )

    headers = auth_headers(client)

    response = client.get(
        (
            "/ceo-executions/approval/"
            "approval-lookup"
        ),
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["execution_uid"]
        == execution_uid
    )
    assert (
        data["approval_uid"]
        == "approval-lookup"
    )


def test_missing_execution_returns_404(
    execution_history_api,
) -> None:
    client, _ = execution_history_api

    headers = auth_headers(client)

    response = client.get(
        "/ceo-executions/exec_missing",
        headers=headers,
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "CEO execution record not found."
    )


def test_missing_approval_returns_404(
    execution_history_api,
) -> None:
    client, _ = execution_history_api

    headers = auth_headers(client)

    response = client.get(
        (
            "/ceo-executions/approval/"
            "approval-missing"
        ),
        headers=headers,
    )

    assert response.status_code == 404


def test_execution_history_pagination(
    execution_history_api,
) -> None:
    client, session_factory = (
        execution_history_api
    )

    for number in range(5):
        create_execution(
            session_factory,
            approval_uid=(
                f"approval-page-{number}"
            ),
        )

    headers = auth_headers(client)

    response = client.get(
        (
            "/ceo-executions"
            "?limit=2&offset=1"
        ),
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["executions"]) == 2


@pytest.mark.parametrize(
    "query",
    [
        "?limit=0",
        "?limit=101",
        "?offset=-1",
    ],
)
def test_invalid_pagination_returns_422(
    execution_history_api,
    query: str,
) -> None:
    client, _ = execution_history_api

    headers = auth_headers(client)

    response = client.get(
        f"/ceo-executions{query}",
        headers=headers,
    )

    assert response.status_code == 422

def test_execution_history_isolated_by_workspace(
    execution_history_api,
):
    client, session_factory = (
        execution_history_api
    )

    headers = auth_headers(client)

    db = session_factory()

    try:
        dental = CEOExecutionRecord(
            execution_uid="exec_dental_private",
            business_uid="biz_dental",
            approval_uid="apr_dental_private",
            objective=(
                "Dental private execution"
            ),
            status="completed",
            success=True,
            completed_task_count=1,
            failed_task_count=0,
        )

        legacy = CEOExecutionRecord(
            execution_uid="exec_legacy_null",
            business_uid=None,
            approval_uid="apr_legacy_null",
            objective=(
                "Legacy unowned execution"
            ),
            status="completed",
            success=True,
            completed_task_count=1,
            failed_task_count=0,
        )

        db.add_all([
            dental,
            legacy,
        ])
        db.commit()

    finally:
        db.close()

    response = client.get(
        "/ceo-executions",
        headers=headers,
    )

    assert response.status_code == 200

    payload = response.json()

    records = (
        payload["executions"]
        if "executions" in payload
        else payload.get("records", [])
    )

    execution_uids = {
        item["execution_uid"]
        for item in records
    }

    assert (
        "exec_dental_private"
        not in execution_uids
    )
    assert (
        "exec_legacy_null"
        not in execution_uids
    )

    protected_urls = [
        (
            "/ceo-executions/"
            "exec_dental_private"
        ),
        (
            "/ceo-executions/"
            "approval/"
            "apr_dental_private"
        ),
        (
            "/ceo-executions/"
            "exec_legacy_null"
        ),
        (
            "/ceo-executions/"
            "approval/"
            "apr_legacy_null"
        ),
    ]

    for url in protected_urls:
        response = client.get(
            url,
            headers=headers,
        )

        assert response.status_code == 404
