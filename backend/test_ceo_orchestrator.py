from __future__ import annotations

from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
)
from app.executives.ceo import (
    orchestrator as orchestrator_module,
)
from app.executives.ceo.orchestrator import (
    CEOExecutionOrchestrator,
)


def build_plan(
    *,
    requires_approval: bool = True,
) -> ExecutivePlan:
    return ExecutivePlan(
        objective="Increase company revenue",
        summary=(
            "Focus on the highest-value "
            "commercial opportunities."
        ),
        actions=[
            ExecutiveAction(
                title="Prioritize CRM opportunities",
                department="CRM",
                instruction=(
                    "Contact the highest-value "
                    "qualified leads."
                ),
                recommendation_score=95.0,
                requires_approval=(
                    requires_approval
                ),
                metadata={
                    "priority_level": "high",
                },
            ),
        ],
        metadata={
            "source": "test",
        },
    )


def test_approval_required_action_creates_approval(
    monkeypatch,
):
    created_requests = []

    def fake_create_approval(data):
        created_requests.append(data)

        return {
            "approval_uid": "apr_test_001",
            "status": "pending",
            "title": data.title,
            "payload": data.payload,
        }

    monkeypatch.setattr(
        orchestrator_module,
        "create_approval",
        fake_create_approval,
    )

    orchestrator = (
        CEOExecutionOrchestrator()
    )

    result = orchestrator.prepare_plan(
        build_plan(),
        source_uid="plan_test_001",
    )

    assert result.approval_count == 1
    assert result.executable_count == 0
    assert result.requires_approval is True

    assert len(created_requests) == 1

    request = created_requests[0]

    assert (
        request.decision_type
        == "executive_action"
    )
    assert (
        request.source_type
        == "ceo_executive_plan"
    )
    assert (
        request.source_uid
        == "plan_test_001"
    )

    assert (
        request.payload[
            "executive_plan"
        ]["actions"][0]["department"]
        == "CRM"
    )


def test_non_approval_action_is_not_submitted(
    monkeypatch,
):
    def fail_create_approval(data):
        raise AssertionError(
            "Approval should not be created."
        )

    monkeypatch.setattr(
        orchestrator_module,
        "create_approval",
        fail_create_approval,
    )

    orchestrator = (
        CEOExecutionOrchestrator()
    )

    result = orchestrator.prepare_plan(
        build_plan(
            requires_approval=False
        )
    )

    assert result.approval_count == 0
    assert result.executable_count == 1
    assert result.requires_approval is False

    assert (
        result.executable_actions[0].department
        == "CRM"
    )


def test_each_action_receives_separate_approval(
    monkeypatch,
):
    created_requests = []

    def fake_create_approval(data):
        created_requests.append(data)

        return {
            "approval_uid": (
                f"apr_{len(created_requests)}"
            ),
            "status": "pending",
            "title": data.title,
            "payload": data.payload,
        }

    monkeypatch.setattr(
        orchestrator_module,
        "create_approval",
        fake_create_approval,
    )

    plan = build_plan()

    plan.actions.append(
        ExecutiveAction(
            title="Launch marketing campaign",
            department="Marketing",
            instruction=(
                "Prepare a targeted campaign "
                "for qualified prospects."
            ),
            recommendation_score=88.0,
            requires_approval=True,
            metadata={
                "priority_level": "medium",
            },
        )
    )

    orchestrator = (
        CEOExecutionOrchestrator()
    )

    result = orchestrator.prepare_plan(
        plan,
        source_uid="plan_test_002",
    )

    assert result.approval_count == 2
    assert len(created_requests) == 2

    first_plan = (
        created_requests[0]
        .payload["executive_plan"]
    )

    second_plan = (
        created_requests[1]
        .payload["executive_plan"]
    )

    assert len(first_plan["actions"]) == 1
    assert len(second_plan["actions"]) == 1

    assert (
        first_plan["actions"][0]["department"]
        == "CRM"
    )

    assert (
        second_plan["actions"][0]["department"]
        == "Marketing"
    )


def test_single_action_approval_preserves_plan_context(
    monkeypatch,
):
    captured = {}

    def fake_create_approval(data):
        captured["request"] = data

        return {
            "approval_uid": "apr_context",
            "status": "pending",
            "title": data.title,
            "payload": data.payload,
        }

    monkeypatch.setattr(
        orchestrator_module,
        "create_approval",
        fake_create_approval,
    )

    plan = build_plan()

    CEOExecutionOrchestrator().prepare_plan(
        plan
    )

    serialized_plan = (
        captured["request"]
        .payload["executive_plan"]
    )

    assert (
        serialized_plan["objective"]
        == "Increase company revenue"
    )

    assert (
        serialized_plan["metadata"][
            "orchestration_scope"
        ]
        == "single_action"
    )

    assert (
        serialized_plan["metadata"][
            "original_action_count"
        ]
        == 1
    )


def test_empty_objective_is_rejected(
    monkeypatch,
):
    def fail_create_approval(data):
        raise AssertionError(
            "Approval should not be created."
        )

    monkeypatch.setattr(
        orchestrator_module,
        "create_approval",
        fail_create_approval,
    )

    plan = build_plan()
    plan.objective = "   "

    try:
        CEOExecutionOrchestrator().prepare_plan(
            plan
        )
    except ValueError as error:
        assert str(error) == (
            "Executive plan objective "
            "cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_invalid_action_is_rejected(
    monkeypatch,
):
    def fail_create_approval(data):
        raise AssertionError(
            "Approval should not be created."
        )

    monkeypatch.setattr(
        orchestrator_module,
        "create_approval",
        fail_create_approval,
    )

    plan = build_plan()
    plan.actions[0].department = " "

    try:
        CEOExecutionOrchestrator().prepare_plan(
            plan
        )
    except ValueError as error:
        assert str(error) == (
            "Executive action department "
            "cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )