from __future__ import annotations

from app.core.executives import (
    ExecutiveBase,
    ExecutiveContext,
    ExecutiveResult,
)
from app.core.workforce import (
    assignment_engine,
)


class MarketingDirector(ExecutiveBase):
    """
    Nestora Marketing Executive.

    Responsible for marketing strategy,
    campaign planning, customer acquisition,
    and delegation to specialist workers.
    """

    async def analyze(
        self,
        context: ExecutiveContext,
    ) -> None:
        print(
            f"[Marketing] Analyzing mission: "
            f"{context.mission}"
        )

    async def plan(
        self,
        context: ExecutiveContext,
    ) -> None:
        print(
            "[Marketing] Building strategy..."
        )

    async def execute(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveResult:
        print(
            "[Marketing] Delegating copywriting "
            "to the AI workforce..."
        )

        content_result = await assignment_engine.assign(
            capability="copywriting",
            title=context.mission,
            description=(
                "Create persuasive marketing content "
                f"for this mission: {context.mission}"
            ),
            payload={
                "mission": context.mission,
                "department": "marketing",
            },
            metadata={
                "requested_by": "marketing_director",
            },
        )

        if not content_result.success:
            return ExecutiveResult(
                success=False,
                summary=(
                    "Marketing execution failed because "
                    "the delegated content task failed."
                ),
                data={
                    "mission": context.mission,
                    "status": "failed",
                    "worker_summary": content_result.summary,
                    "worker_output": content_result.output,
                },
                recommendations=[
                    "Review the Content Writer result",
                    "Retry the marketing content task",
                ],
            )

        return ExecutiveResult(
            success=True,
            summary=(
                "Marketing strategy and content "
                "generated successfully."
            ),
            data={
                "mission": context.mission,
                "status": "completed",
                "delegated_worker": "content_writer",
                "content": content_result.output,
                "worker_summary": content_result.summary,
            },
            recommendations=[
                "Publish the generated content",
                "Increase social media activity",
                "Improve SEO",
                "Launch paid advertising",
            ],
        )

    async def learn(
        self,
        context: ExecutiveContext,
        result: ExecutiveResult,
    ) -> None:
        print(
            "[Marketing] Learning from the "
            "delegated worker result..."
        )

    async def report(
        self,
        context: ExecutiveContext,
        result: ExecutiveResult,
    ) -> None:
        print(
            "[Marketing] Reporting executive "
            "and workforce results..."
        )