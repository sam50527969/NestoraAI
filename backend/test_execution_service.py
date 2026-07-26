import asyncio

from app.core.execution.execution_service import execution_service
from app.core.execution.executive_registry import executive_registry
from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
)


class FollowUpExecutive:
    async def execute(self, payload):
        return {
            "status": "completed",
            "department": "follow_up",
            "instruction": payload["instruction"],
        }


class MarketingExecutive:
    def execute(self, payload):
        return {
            "status": "completed",
            "department": "marketing",
            "instruction": payload["instruction"],
        }


async def main():
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

    plan = ExecutivePlan(
        objective="Recover lost patients",
        summary=(
            "Identify inactive patients and prepare "
            "a recovery campaign."
        ),
        actions=[
            ExecutiveAction(
                title="Identify inactive patients",
                department="Follow Up",
                instruction=(
                    "Find patients who have not visited recently."
                ),
                recommendation_score=9.2,
                metadata={
                    "priority_level": "high",
                },
            ),
            ExecutiveAction(
                title="Prepare recovery campaign",
                department="Marketing",
                instruction=(
                    "Create a campaign for inactive patients."
                ),
                recommendation_score=8.7,
                metadata={
                    "priority_level": "medium",
                },
            ),
        ],
    )

    result = await execution_service.execute_plan(plan)

    print(result.success)
    print(result.mission.objective)
    print(result.workflow.task_count)
    print(result.completed_task_count)
    print(result.failed_task_count)
    print(result.workflow_result.success)
    print(result.scheduler_result.success)

    for dispatch_result in result.dispatch_results:
        print(
            dispatch_result.executor,
            dispatch_result.success,
            dispatch_result.result["status"],
        )


if __name__ == "__main__":
    asyncio.run(main())