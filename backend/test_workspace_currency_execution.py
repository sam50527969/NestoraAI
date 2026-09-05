from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.mission_executor import MissionExecutor
from app.workforce.runtime.marketing import MarketingExecutive


@pytest.mark.parametrize(
    ("currency", "expected"),
    [
        ("AED", "AED"),
        ("USD", "USD"),
        ("QAR", "QAR"),
    ],
)
def test_mission_executor_uses_injected_workspace_currency(
    currency,
    expected,
):
    business_context = SimpleNamespace(
        currency=currency,
    )

    executor = MissionExecutor(
        db=object(),
        mission_id="mission-currency-test",
        request=object(),
        business_uid="biz-currency-test",
        business_context=business_context,
    )

    assert executor.currency == expected


@pytest.mark.parametrize(
    "currency",
    [
        "AED",
        "USD",
        "QAR",
    ],
)
def test_marketing_fallback_preserves_workspace_currency(
    currency,
):
    executive = MarketingExecutive()

    output = executive.fallback_output(
        title="Workspace campaign",
        description="Test workspace-aware marketing.",
        input_data={
            "business_uid": "biz-currency-test",
            "currency": currency,
        },
        error_message="Forced fallback for regression test.",
    )

    assert output["budget"]["currency"] == currency
    assert output["input_data"]["currency"] == currency


def test_workforce_injects_business_context_currency():
    from app.workforce.orchestrator import WorkforceOrchestrator

    orchestrator = object.__new__(
        WorkforceOrchestrator
    )

    orchestrator._task_repository = Mock()
    orchestrator._mission_event_repository = Mock()
    orchestrator._learning_service = Mock()
    orchestrator._business_repository = Mock()
    orchestrator._executive_router = Mock()

    orchestrator._task_repository.deserialize_input.return_value = {}
    orchestrator._task_repository.list_by_mission.return_value = []
    orchestrator._learning_service.build_context.return_value = Mock(
        model_dump=Mock(return_value={})
    )
    orchestrator._business_repository.get_context.return_value = (
        SimpleNamespace(currency="USD")
    )
    orchestrator._executive_router.execute_task.return_value = {
        "success": True,
    }
    orchestrator._save_task_memory = Mock()

    task = SimpleNamespace(
        task_uid="task-currency-test",
        agent_name="Marketing",
        task_type="marketing",
        title="US campaign",
        description="Create a US campaign.",
        sequence_number=1,
        depends_on_task_uid=None,
    )

    mission = SimpleNamespace(
        mission_uid="mission-currency-test",
        business_uid="biz-us-test",
        title="US Growth",
        objective="Grow the US workspace",
        description="Workspace currency regression test.",
        priority="high",
        estimated_value=10000,
        expected_roi=2.0,
    )

    orchestrator._execute_task(
        task=task,
        mission=mission,
    )

    orchestrator._business_repository.get_context.assert_called_once_with(
        "biz-us-test"
    )

    call = orchestrator._executive_router.execute_task.call_args

    assert call.kwargs["input_data"]["business_uid"] == "biz-us-test"
    assert call.kwargs["input_data"]["currency"] == "USD"