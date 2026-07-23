from __future__ import annotations

from collections.abc import Iterable

from app.executives.ceo.models import ExecutiveRecommendation
from app.executives.ceo.state import CompanyState


class CEODecisionEngine:
    """
    Evaluates company conditions and ranks executive recommendations.
    """

    def rank_recommendations(
        self,
        recommendations: Iterable[ExecutiveRecommendation],
    ) -> list[ExecutiveRecommendation]:
        ranked = list(recommendations)

        ranked.sort(
            key=lambda recommendation: recommendation.calculate_final_score(),
            reverse=True,
        )

        return ranked

    def generate_state_recommendations(
        self,
        state: CompanyState,
    ) -> list[ExecutiveRecommendation]:
        recommendations: list[ExecutiveRecommendation] = []

        for department in state.available_departments():
            if department.health_score < 40:
                recommendations.append(
                    ExecutiveRecommendation(
                        title=f"Stabilize {department.department}",
                        description=(
                            f"{department.department} has a low health score "
                            f"of {department.health_score:.1f}."
                        ),
                        department=department.department,
                        action_type="stabilization",
                        priority_score=90,
                        impact_score=85,
                        urgency_score=90,
                        confidence_score=80,
                    )
                )

            for risk in department.risks:
                recommendations.append(
                    ExecutiveRecommendation(
                        title=f"Address risk in {department.department}",
                        description=risk,
                        department=department.department,
                        action_type="risk_mitigation",
                        priority_score=85,
                        impact_score=80,
                        urgency_score=85,
                        confidence_score=75,
                    )
                )

            for opportunity in department.opportunities:
                recommendations.append(
                    ExecutiveRecommendation(
                        title=f"Pursue opportunity in {department.department}",
                        description=opportunity,
                        department=department.department,
                        action_type="opportunity",
                        priority_score=75,
                        impact_score=85,
                        urgency_score=65,
                        confidence_score=70,
                    )
                )

        for risk in state.critical_risks:
            recommendations.append(
                ExecutiveRecommendation(
                    title="Resolve critical company risk",
                    description=risk,
                    department="CEO",
                    action_type="critical_risk",
                    priority_score=100,
                    impact_score=100,
                    urgency_score=100,
                    confidence_score=90,
                )
            )

        for opportunity in state.major_opportunities:
            recommendations.append(
                ExecutiveRecommendation(
                    title="Evaluate major company opportunity",
                    description=opportunity,
                    department="CEO",
                    action_type="strategic_opportunity",
                    priority_score=85,
                    impact_score=95,
                    urgency_score=70,
                    confidence_score=75,
                )
            )

        return self.rank_recommendations(recommendations)