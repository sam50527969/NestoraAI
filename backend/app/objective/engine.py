from __future__ import annotations

from dataclasses import dataclass

from app.business.models import BusinessProfile
from app.objective.analyzer import ObjectiveAnalyzer
from app.objective.models import (
    BusinessObjective,
    ObjectiveAnalysisResult,
    StrategyRecommendation,
)
from app.objective.strategist import ObjectiveStrategist


@dataclass(slots=True)
class ObjectiveEngineResult:
    """
    Final output returned by the Objective Engine.

    This object groups together every stage of the
    decision-making process so callers only interact
    with one result object.
    """

    analysis: ObjectiveAnalysisResult
    strategy: StrategyRecommendation


class ObjectiveEngine:
    """
    Facade for the Objective Engine.

    Coordinates the Analyzer and Strategist.
    """

    def __init__(self) -> None:

        self._analyzer = ObjectiveAnalyzer()
        self._strategist = ObjectiveStrategist()

    def process(
        self,
        business: BusinessProfile,
        objective: BusinessObjective,
    ) -> ObjectiveEngineResult:
        """
        Execute the complete objective planning pipeline.
        """

        analysis = self._analyzer.analyze(
            business,
            objective,
        )

        strategy = self._strategist.create_strategy(
            analysis,
        )

        return ObjectiveEngineResult(
            analysis=analysis,
            strategy=strategy,
        )