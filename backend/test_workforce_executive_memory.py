from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.workforce.orchestrator import (
    WorkforceOrchestrator,
)


def make_orchestrator():
    orchestrator = object.__new__(
        WorkforceOrchestrator
    )

    orchestrator._db = Mock()

    return orchestrator


def test_save_task_memory_uses_mission_business_uid():
    orchestrator = make_orchestrator()

    task = SimpleNamespace(
        task_uid="task_atlas_001",
        agent_name="CEO",
        task_type="analysis",
        title="Review Atlas growth",
    )

    mission = SimpleNamespace(
        mission_uid="mission_atlas_001",
        business_uid="biz_atlas",
        title="Atlas Growth Mission",
    )

    memory_service = Mock()

    with patch(
        "app.workforce.orchestrator.ExecutiveMemoryService",
        return_value=memory_service,
    ):
        orchestrator._save_task_memory(
            task=task,
            mission=mission,
            output={
                "summary": "Atlas growth reviewed.",
            },
        )

    memory_service.create_memory.assert_called_once()

    call = memory_service.create_memory.call_args

    payload = call.args[0]

    assert call.kwargs == {
        "business_uid": "biz_atlas",
    }

    assert payload.executive == "CEO"
    assert payload.category == "analysis"

    assert (
        payload.source
        == "mission:mission_atlas_001"
    )

    assert "Atlas Growth Mission" in payload.memory


def test_learning_context_requires_mission_workspace():
    import inspect

    from app.learning.service import (
        ExecutiveLearningService,
    )

    signature = inspect.signature(
        ExecutiveLearningService.build_context
    )

    parameter = signature.parameters[
        "business_uid"
    ]

    assert (
        parameter.kind
        == inspect.Parameter.KEYWORD_ONLY
    )

    assert (
        parameter.default
        is inspect.Parameter.empty
    )


def test_workforce_passes_mission_workspace_to_learning():
    import inspect

    source = inspect.getsource(
        WorkforceOrchestrator._execute_task
    )

    assert (
        "self._learning_service.build_context("
        in source
    )

    assert (
        "business_uid=mission.business_uid"
        in source
    )
