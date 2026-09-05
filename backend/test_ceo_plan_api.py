from __future__ import annotations

import warnings

import pytest
from fastapi import FastAPI

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from fastapi.testclient import (
        TestClient,
    )

from app.agents import (
    ceo_agent,
)
from app.business.access import get_current_business_uid
from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
)
from app.routes.ceo import (
    router as ceo_router,
)


@pytest.fixture()
def ceo_plan_api(
    monkeypatch,
):
    def fake_build_ceo_plan(
        db,
        objective,
        *,
        business_uid,
    ):
        assert business_uid == "biz_atlas"
        return ExecutivePlan(
            objective=objective,
            summary=(
                "Prioritize the strongest "
                "commercial opportunities."
            ),
            actions=[
                ExecutiveAction(
                    title=(
                        "Contact priority leads"
                    ),
                    department="CRM",
                    instruction=(
                        "Prepare outreach for "
                        "high-value leads."
                    ),
                    recommendation_score=94.0,
                    requires_approval=True,
                    metadata={
                        "priority_level": "high",
                    },
                ),
            ],
            metadata={
                "source": "api_test",
            },
        )

    monkeypatch.setattr(
        ceo_agent,
        "build_ceo_plan",
        fake_build_ceo_plan,
    )

    def override_prepare_plan(
        self,
        plan,
        *,
        business_uid,
        source_uid=None,
        requested_by="CEO Agent",
    ):
        from app.executives.ceo.orchestrator import (
            CEOOrchestrationResult,
        )

        return CEOOrchestrationResult(
            plan=plan,
            approvals=[
                {
                    "approval_uid": (
                        "apr_plan_test_001"
                    ),
                    "title": (
                        "Contact priority leads"
                    ),
                    "status": "pending",
                },
            ],
            executable_actions=[],
        )

    monkeypatch.setattr(
        ceo_agent.CEOExecutionOrchestrator,
        "prepare_plan",
        override_prepare_plan,
    )

    app = FastAPI()
    app.include_router(ceo_router)

    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_atlas"

    with TestClient(app) as client:
        yield client


def test_ceo_plan_creates_pending_approval(
    ceo_plan_api,
):
    response = ceo_plan_api.post(
        "/ceo/plan",
        json={
            "objective": (
                "Increase revenue from "
                "qualified opportunities."
            ),
            "source_uid": (
                "ceo_plan_api_test"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["objective"]
        == (
            "Increase revenue from "
            "qualified opportunities."
        )
    )

    assert data["action_count"] == 1
    assert data["approval_count"] == 1
    assert data["executable_count"] == 0
    assert data["requires_approval"] is True

    assert len(data["approvals"]) == 1

    approval = data["approvals"][0]

    assert (
        approval["approval_uid"]
        == "apr_plan_test_001"
    )

    assert approval["status"] == "pending"

    assert (
        approval["title"]
        == "Contact priority leads"
    )


def test_ceo_plan_requires_objective(
    ceo_plan_api,
):
    response = ceo_plan_api.post(
        "/ceo/plan",
        json={},
    )

    assert response.status_code == 422


def test_ceo_plan_rejects_empty_objective(
    ceo_plan_api,
):
    response = ceo_plan_api.post(
        "/ceo/plan",
        json={
            "objective": "",
        },
    )

    assert response.status_code == 422


def test_ceo_plan_reports_non_approval_actions(
    ceo_plan_api,
    monkeypatch,
):
    def fake_prepare_plan(
        self,
        plan,
        *,
        business_uid,
        source_uid=None,
        requested_by="CEO Agent",
    ):
        from app.executives.ceo.orchestrator import (
            CEOOrchestrationResult,
        )

        action = ExecutiveAction(
            title="Refresh dashboard metrics",
            department="Analytics",
            instruction=(
                "Refresh executive dashboard "
                "metrics."
            ),
            recommendation_score=80.0,
            requires_approval=False,
        )

        plan.actions = [
            action,
        ]

        return CEOOrchestrationResult(
            plan=plan,
            approvals=[],
            executable_actions=[
                action,
            ],
        )

    monkeypatch.setattr(
        ceo_agent.CEOExecutionOrchestrator,
        "prepare_plan",
        fake_prepare_plan,
    )

    response = ceo_plan_api.post(
        "/ceo/plan",
        json={
            "objective": (
                "Refresh executive metrics."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_count"] == 0
    assert data["executable_count"] == 1
    assert data["requires_approval"] is False

    assert len(
        data["executable_actions"]
    ) == 1

    action = data[
        "executable_actions"
    ][0]

    assert (
        action["department"]
        == "Analytics"
    )

    assert (
        action["recommendation_score"]
        == 80.0
    )