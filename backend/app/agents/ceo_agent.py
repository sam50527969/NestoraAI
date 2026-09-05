from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.executives.ceo import CEOBrain
from app.executives.ceo.models import (
    ExecutivePlan,
)
from app.executives.ceo.orchestrator import (
    CEOExecutionOrchestrator,
)
from app.executives.ceo.state_builder import (
    CEOCompanyStateBuilder,
)


def build_ceo_plan(
    db: Session,
    objective: str,
    *,
    business_uid: str,
) -> ExecutivePlan:
    """
    Build an executive plan from live Nestora
    company data.
    """

    company_state = CEOCompanyStateBuilder(
        db,
        business_uid=business_uid,
    ).build()

    brain = CEOBrain()

    return brain.evaluate(
        company_state=company_state,
        objective=objective,
    )


def ask_ceo(
    db: Session,
    question: str,
    *,
    business_uid: str,
) -> dict[str, str]:
    """
    Answer a CEO question using live Nestora
    business data.
    """

    plan = build_ceo_plan(
        db,
        question,
        business_uid=business_uid,
    )

    return {
        "answer": _format_executive_answer(
            plan
        )
    }


def prepare_ceo_plan(
    db: Session,
    objective: str,
    *,
    business_uid: str,
    source_uid: str | None = None,
) -> dict[str, Any]:
    """
    Build a CEO plan and prepare its actions for
    Nestora's approval and execution lifecycle.
    """

    plan = build_ceo_plan(
        db,
        objective,
        business_uid=business_uid,
    )

    result = CEOExecutionOrchestrator().prepare_plan(
        plan,
        business_uid=business_uid,
        source_uid=source_uid,
    )

    return {
        "objective": plan.objective,
        "summary": plan.summary,
        "action_count": len(
            plan.actions
        ),
        "recommendation_count": len(
            plan.recommendations
        ),
        "approval_count": (
            result.approval_count
        ),
        "executable_count": (
            result.executable_count
        ),
        "requires_approval": (
            result.requires_approval
        ),
        "approvals": [
            {
                "approval_uid": approval[
                    "approval_uid"
                ],
                "title": approval["title"],
                "status": approval["status"],
            }
            for approval in result.approvals
        ],
        "executable_actions": [
            {
                "title": action.title,
                "department": (
                    action.department
                ),
                "instruction": (
                    action.instruction
                ),
                "recommendation_score": (
                    action.recommendation_score
                ),
            }
            for action
            in result.executable_actions
        ],
    }


def _format_executive_answer(
    plan: ExecutivePlan,
) -> str:
    parts = [
        plan.summary,
    ]

    if plan.recommendations:
        parts.append(
            "Top recommendations:"
        )

        for recommendation in (
            plan.recommendations[:3]
        ):
            parts.append(
                f"- {recommendation.title}: "
                f"{recommendation.description}"
            )

    if plan.actions:
        parts.append(
            "Recommended actions:"
        )

        for action in plan.actions[:3]:
            parts.append(
                f"- {action.department}: "
                f"{action.instruction}"
            )

    return "\n".join(parts)