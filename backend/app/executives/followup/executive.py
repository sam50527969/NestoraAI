from __future__ import annotations

from app.core.executives.base import ExecutiveBase
from app.core.executives.context import ExecutiveContext
from app.core.executives.result import ExecutiveResult

from app.executives.followup.prompts import SYSTEM_PROMPT
from app.services.llm import llm


class FollowupExecutive(ExecutiveBase):
    """
    AI Executive responsible for lead follow-up recommendations.
    """

    async def analyze(
        self,
        context: ExecutiveContext,
    ) -> None:
        context.shared_data["analysis_complete"] = True

    async def plan(
        self,
        context: ExecutiveContext,
    ) -> None:
        context.shared_data["plan"] = (
            "Generate follow-up recommendation."
        )

    async def execute(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveResult:

        response = await llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=(
                f"""
Mission:
{context.mission}

Objective:
{context.objective}

Business:
{context.business_name}

Metadata:
{context.metadata}
"""
            ),
        )

        return ExecutiveResult(
            success=True,
            summary="Follow-up recommendation generated.",
            data={
                "response": response,
            },
            recommendations=[
                response,
            ],
        )