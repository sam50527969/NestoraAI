from __future__ import annotations

from app.objective.exceptions import (
    StrategyGenerationError,
)
from app.objective.models import (
    ObjectiveAnalysisResult,
    StrategyRecommendation,
)


class ObjectiveStrategist:
    """
    Converts business opportunities into an executable strategy.

    This class does not execute work.

    It determines HOW the business should
    achieve its objective.
    """

    def create_strategy(
        self,
        analysis: ObjectiveAnalysisResult,
    ) -> StrategyRecommendation:

        try:

            analysis.validate()

            opportunities = analysis.opportunities

            estimated_roi = (
                sum(
                    opportunity.estimated_value
                    for opportunity in opportunities
                )
                / 10000
            )

            missions = [
                opportunity.title
                for opportunity in opportunities
            ]

            risks = []

            if analysis.has_missing_information:
                risks.append(
                    "Business information is incomplete."
                )

            if analysis.has_risks:
                risks.extend(analysis.risks)

            summary = (
                "Execute the identified opportunities "
                "in priority order."
            )

            strategy = StrategyRecommendation(
                title="Business Growth Strategy",
                summary=summary,
                estimated_roi=estimated_roi,
                confidence=analysis.confidence,
                missions=missions,
                executives=analysis.recommended_executives,
                risks=risks,
                success_metrics=analysis.relevant_metrics,
            )

            strategy.validate()

            return strategy

        except Exception as exc:

            raise StrategyGenerationError(
                str(exc)
            ) from exc