from sqlalchemy.orm import Session

from app.executives.ceo import CEOBrain
from app.executives.ceo.state_builder import CEOCompanyStateBuilder


def ask_ceo(
    db: Session,
    question: str,
) -> dict[str, str]:
    """
    Answer a CEO question using live Nestora business data
    and the modern executive CEO Brain.
    """

    company_state = CEOCompanyStateBuilder(
        db
    ).build()

    brain = CEOBrain()

    plan = brain.evaluate(
        company_state=company_state,
        objective=question,
    )

    return {
        "answer": _format_executive_answer(
            plan
        )
    }


def _format_executive_answer(
    plan,
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