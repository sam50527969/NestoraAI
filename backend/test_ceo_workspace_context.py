from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.business.access import get_current_business_uid
from app.database.database import get_db
from app.routes.objective import router
from app.services import mission_executor as executor_module
from app.services.mission_executor import MissionExecutor


def _override_db():
    yield None


def test_ceo_rejects_mismatched_workspace_identity():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_authorized"

    response = TestClient(app).post(
        "/ceo/objective",
        json={
            "business_id": "biz_other",
            "objective": "Grow qualified revenue",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": (
            "CEO business context does not match "
            "the active workspace."
        ),
    }


def test_mission_executor_scopes_created_leads(
    monkeypatch,
):
    captured = {}

    monkeypatch.setattr(
        executor_module,
        "update_mission_task_progress",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        executor_module,
        "update_mission",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        executor_module,
        "update_agent",
        lambda *args, **kwargs: None,
    )

    def capture_lead(*, db, lead_data):
        captured["lead"] = lead_data
        return lead_data

    monkeypatch.setattr(
        executor_module,
        "create_lead",
        capture_lead,
    )

    executor = MissionExecutor(
        db=object(),
        mission_id="mission-test",
        request=object(),
        business_uid="biz_authorized",
    )
    executor.accepted_count = 1
    executor.log = lambda *args: None

    executor.save_lead(
        {
            "category": "Retail",
            "location": "Sydney",
        },
        "Example Business",
        50,
    )

    assert (
        captured["lead"].business_uid
        == "biz_authorized"
    )
