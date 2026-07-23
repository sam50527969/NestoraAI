from __future__ import annotations

from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
    ExecutiveRecommendation,
)


class CEOPlanner:
    """
    Converts ranked recommendations into an executable CEO plan.
    """

    def create_plan(
        self,
        objective: str,
        recommendations: list[ExecutiveRecommendation],
        max_actions: int = 5,
    ) -> ExecutivePlan:
        selected = recommendations[:max_actions]

        actions = [
            self._recommendation_to_action(recommendation)
            for recommendation in selected
        ]

        summary = self._build_summary(
            objective=objective,
            recommendations=selected,
        )

        return ExecutivePlan(
            objective=objective,
            summary=summary,
            actions=actions,
            recommendations=selected,
            metadata={
                "total_recommendations_received": len(recommendations),
                "actions_created": len(actions),
            },
        )

    def _recommendation_to_action(
        self,
        recommendation: ExecutiveRecommendation,
    ) -> ExecutiveAction:
        return ExecutiveAction(
            title=recommendation.title,
            department=recommendation.department,
            instruction=recommendation.description,
            recommendation_score=recommendation.calculate_final_score(),
            requires_approval=True,
            metadata={
                "action_type": recommendation.action_type,
                "priority_level": recommendation.priority_level.value,
                "estimated_value": recommendation.estimated_value,
                "currency": recommendation.currency,
            },
        )

    def _build_summary(
        self,
        objective: str,
        recommendations: list[ExecutiveRecommendation],
    ) -> str:
        if not recommendations:
            return (
                f"No immediate executive actions were identified "
                f"for the objective: {objective}."
            )

        highest_score = recommendations[0].calculate_final_score()

        return (
            f"Created {len(recommendations)} executive action(s) "
            f"for the objective '{objective}'. "
            f"Highest recommendation score: {highest_score:.2f}."
        )