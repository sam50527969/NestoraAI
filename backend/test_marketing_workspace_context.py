from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.business.access import get_current_business_uid
from app.database.database import get_db
from app.routes.marketing import router


def _override_db():
    yield None


def test_marketing_director_rejects_mismatched_workspace_identity():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_authorized"

    client = TestClient(app)
    response = client.post(
        "/marketing/director",
        json={
            "business": {
                "business_id": "biz_other",
                "business_name": "Other Business",
                "industry": "Retail",
            },
            "goal": {
                "objective": "Grow qualified leads",
                "currency": "AUD",
            },
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": (
            "Marketing business context does not match "
            "the active workspace."
        ),
    }
