from __future__ import annotations

from app.executives.ceo.decision_engine import CEODecisionEngine
from app.executives.ceo.models import ExecutivePlan
from app.executives.ceo.planner import CEOPlanner
from app.executives.ceo.state import CompanyState


class CEOBrain:
    """
    Top-level executive orchestrator for Nestora AI.

    The CEO Brain evaluates the overall company state,
    generates strategic recommendations, prioritizes them,
    and produces an actionable executive plan.
    """

    def __init__(self) -> None:
        self.decision_engine = CEODecisionEngine()
        self.planner = CEOPlanner()

    def evaluate(
        self,
        company_state: CompanyState,
        objective: str = "Improve overall business performance",
    ) -> ExecutivePlan:
        recommendations = (
            self.decision_engine.generate_state_recommendations(
                company_state
            )
        )

        return self.planner.create_plan(
            objective=objective,
            recommendations=recommendations,
        )