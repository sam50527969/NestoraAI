import asyncio

from app.approvals.executor import (
    execute_action,
)
from app.core.execution.execution_service import (
    execution_service,
)
from app.core.execution.executive_registry import (
    executive_registry,
)
from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
)
from app.executives.ceo.serialization import (
    serialize_executive_plan,
)


class FollowUpExecutive:
    async def execute(
        self,
        payload,
    ):
        return {
            "status": "completed",
            "department": "follow_up",
            "instruction": payload[
                "instruction"
            ],
        }


class MarketingExecutive:
    def execute(
        self,
        payload,
    ):
        return {
            "status": "completed",
            "department": "marketing",
            "instruction": payload[
                "instruction"
            ],
        }


def build_test_plan() -> ExecutivePlan:
    return ExecutivePlan(
        objective=(
            "Recover inactive customers"
        ),
        summary=(
            "Identify inactive customers "
            "and prepare a recovery campaign."
        ),
        actions=[
            ExecutiveAction(
                title=(
                    "Identify inactive "
                    "customers"
                ),
                department="Follow Up",
                instruction=(
                    "Find customers who have "
                    "not engaged recently."
                ),
                recommendation_score=92.0,
                requires_approval=True,
                metadata={
                    "priority_level": "high",
                },
            ),
            ExecutiveAction(
                title=(
                    "Prepare recovery campaign"
                ),
                department="Marketing",
                instruction=(
                    "Create a recovery "
                    "campaign for inactive "
                    "customers."
                ),
                recommendation_score=87.0,
                requires_approval=True,
                metadata={
                    "priority_level": "medium",
                },
            ),
        ],
    )


def setup_executives() -> None:
    execution_service.clear()
    executive_registry.clear()

    executive_registry.register(
        "follow_up",
        FollowUpExecutive(),
    )

    executive_registry.register(
        "marketing",
        MarketingExecutive(),
    )


def teardown_executives() -> None:
    execution_service.clear()
    executive_registry.clear()


def test_executive_action_executes_plan():
    setup_executives()

    try:
        plan = build_test_plan()

        payload = {
            "executive_plan": (
                serialize_executive_plan(
                    plan
                )
            )
        }

        result = asyncio.run(
            execute_action(
                "executive_action",
                None,
                payload,
                "apr_test_execution",
            )
        )

        assert (
            result["action_type"]
            == "executive_action"
        )

        assert (
            result["status"]
            == "completed"
        )

        assert result["success"] is True

        assert (
            result["completed_task_count"]
            == 2
        )

        assert (
            result["failed_task_count"]
            == 0
        )

        assert result["mission_id"]
        assert result["workflow_id"]

    finally:
        teardown_executives()


def test_executive_action_builds_real_mission():
    setup_executives()

    try:
        plan = build_test_plan()

        payload = {
            "executive_plan": (
                serialize_executive_plan(
                    plan
                )
            )
        }

        result = asyncio.run(
            execute_action(
                "executive_action",
                None,
                payload,
                "apr_test_mission",
            )
        )

        mission = (
            execution_service.get_mission(
                result["mission_id"]
            )
        )

        assert mission is not None

        assert (
            mission.objective
            == "Recover inactive customers"
        )

        assert "follow_up" in (
            mission.assigned_to
        )

        assert "marketing" in (
            mission.assigned_to
        )

    finally:
        teardown_executives()


def test_executive_action_executes_departments():
    setup_executives()

    try:
        plan = build_test_plan()

        payload = {
            "executive_plan": (
                serialize_executive_plan(
                    plan
                )
            )
        }

        result = asyncio.run(
            execute_action(
                "executive_action",
                None,
                payload,
                "apr_test_departments",
            )
        )

        workflow = (
            execution_service.get_workflow(
                result["workflow_id"]
            )
        )

        executors = {
            task.executor
            for task in workflow.tasks
        }

        assert executors == {
            "follow_up",
            "marketing",
        }

        assert all(
            task.status.value
            == "completed"
            for task in workflow.tasks
        )

    finally:
        teardown_executives()


def test_missing_executive_plan_is_rejected():
    setup_executives()

    try:
        try:
            asyncio.run(
                execute_action(
                    "executive_action",
                    None,
                    {},
                    "apr_test_missing",
                )
            )
        except ValueError as error:
            assert str(error) == (
                "Executive action payload "
                "must contain an "
                "executive_plan."
            )
        else:
            raise AssertionError(
                "Expected ValueError."
            )

    finally:
        teardown_executives()


def test_unregistered_department_fails_execution():
    execution_service.clear()
    executive_registry.clear()

    try:
        plan = ExecutivePlan(
            objective=(
                "Execute unsupported "
                "department action"
            ),
            summary=(
                "Test dispatcher failure."
            ),
            actions=[
                ExecutiveAction(
                    title=(
                        "Run finance action"
                    ),
                    department="Finance",
                    instruction=(
                        "Prepare financial "
                        "analysis."
                    ),
                    recommendation_score=90.0,
                    requires_approval=True,
                    metadata={
                        "priority_level": (
                            "high"
                        ),
                    },
                )
            ],
        )

        payload = {
            "executive_plan": (
                serialize_executive_plan(
                    plan
                )
            )
        }

        result = asyncio.run(
            execute_action(
                "executive_action",
                None,
                payload,
                "apr_test_failure",
            )
        )

        assert result["success"] is False

        assert (
            result["status"]
            == "failed"
        )

        assert (
            result["completed_task_count"]
            == 0
        )

        assert (
            result["failed_task_count"]
            == 1
        )

    finally:
        execution_service.clear()
        executive_registry.clear()