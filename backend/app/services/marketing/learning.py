from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.marketing import (
    MarketingBudgetPlan,
    MarketingBusinessAnalysis,
    MarketingBusinessProfile,
    MarketingCampaignPlan,
    MarketingGoal,
    MarketingPrediction,
    MarketingStrategy,
)
from app.services.memory import (
    MemoryManager,
    get_memory_manager,
)
from app.services.memory.memory_models import (
    BusinessKnowledge,
    Observation,
    Pattern,
    Recommendation,
)


class MarketingLearningEngineError(RuntimeError):
    """Raised when marketing learning cannot be stored."""


@dataclass
class MarketingLearningResult:
    """
    Summary of memory entries created by the Marketing Director.
    """

    business_id: str

    entries_created: int = 0

    observations_created: int = 0

    recommendations_created: int = 0

    patterns_created: int = 0

    knowledge_created: int = 0

    created_titles: list[str] = field(
        default_factory=list,
    )

    warnings: list[str] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "business_id": self.business_id,
            "entries_created": self.entries_created,
            "observations_created": (
                self.observations_created
            ),
            "recommendations_created": (
                self.recommendations_created
            ),
            "patterns_created": self.patterns_created,
            "knowledge_created": self.knowledge_created,
            "created_titles": self.created_titles,
            "warnings": self.warnings,
        }


class MarketingLearningEngine:
    """
    Stores useful Marketing Director insights in Business Memory.

    The engine records:

    - Business positioning knowledge
    - Audience observations
    - Strategic recommendations
    - Budget recommendations
    - Campaign observations
    - Performance predictions
    - Recurring patterns when similar memory already exists

    Memory is stored through Nestora's shared MemoryManager.
    """

    SOURCE = "Marketing Director"

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
    ):
        self.memory_manager = (
            memory_manager
            or get_memory_manager()
        )

    def record_marketing_run(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        analysis: MarketingBusinessAnalysis,
        strategy: MarketingStrategy,
        budget: MarketingBudgetPlan,
        campaign: MarketingCampaignPlan,
        prediction: MarketingPrediction,
    ) -> MarketingLearningResult:
        """
        Store useful knowledge from a completed marketing run.
        """

        self._validate_inputs(
            business=business,
            strategy=strategy,
            campaign=campaign,
        )

        result = MarketingLearningResult(
            business_id=business.business_id,
        )

        memory_operations = [
            lambda: self._store_positioning_knowledge(
                business=business,
                analysis=analysis,
            ),
            lambda: self._store_audience_observation(
                business=business,
                analysis=analysis,
            ),
            lambda: self._store_strategy_recommendation(
                business=business,
                goal=goal,
                strategy=strategy,
            ),
            lambda: self._store_budget_recommendation(
                business=business,
                budget=budget,
            ),
            lambda: self._store_campaign_observation(
                business=business,
                campaign=campaign,
            ),
            lambda: self._store_prediction_observation(
                business=business,
                prediction=prediction,
                goal=goal,
            ),
        ]

        for operation in memory_operations:
            try:
                entry = operation()

                self._register_created_entry(
                    result=result,
                    entry=entry,
                )

            except Exception as exc:
                result.warnings.append(
                    str(exc)
                )

        self._detect_and_store_patterns(
            business=business,
            strategy=strategy,
            result=result,
        )

        return result

    @staticmethod
    def _validate_inputs(
        business: MarketingBusinessProfile,
        strategy: MarketingStrategy,
        campaign: MarketingCampaignPlan,
    ) -> None:
        if not business.business_id.strip():
            raise MarketingLearningEngineError(
                "A business ID is required for learning."
            )

        if not strategy.channels:
            raise MarketingLearningEngineError(
                "A marketing strategy with at least one "
                "channel is required for learning."
            )

        if not campaign.weeks:
            raise MarketingLearningEngineError(
                "A campaign plan with at least one week "
                "is required for learning."
            )

    def _store_positioning_knowledge(
        self,
        business: MarketingBusinessProfile,
        analysis: MarketingBusinessAnalysis,
    ) -> BusinessKnowledge:
        entry = BusinessKnowledge(
            title="Marketing Positioning",
            content=analysis.recommended_positioning,
            confidence=analysis.confidence,
            source=self.SOURCE,
            tags=[
                "marketing",
                "positioning",
                "brand",
                self._tag_value(business.industry),
            ],
            metadata={
                "business_name": business.business_name,
                "industry": business.industry,
                "location": business.location,
            },
            importance=8,
        )

        return self.memory_manager.remember(
            business.business_id,
            entry,
        )

    def _store_audience_observation(
        self,
        business: MarketingBusinessProfile,
        analysis: MarketingBusinessAnalysis,
    ) -> Observation:
        evidence = [
            item
            for item in business.target_audience
            if item.strip()
        ]

        entry = Observation(
            title="Marketing Audience Insight",
            content=analysis.audience_summary,
            confidence=analysis.confidence,
            source=self.SOURCE,
            tags=[
                "marketing",
                "audience",
                "customer",
                self._tag_value(business.industry),
            ],
            metadata={
                "target_audience": (
                    business.target_audience
                ),
                "preferred_languages": (
                    business.preferred_languages
                ),
            },
            evidence=evidence,
        )

        return self.memory_manager.remember(
            business.business_id,
            entry,
        )

    def _store_strategy_recommendation(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
    ) -> Recommendation:
        channel_names = [
            channel.channel
            for channel in strategy.channels
        ]

        content = (
            f"Use the '{strategy.strategy_name}' strategy "
            f"to achieve the objective: {goal.objective}. "
            f"Priority channels: "
            f"{', '.join(channel_names)}. "
            f"{strategy.executive_summary}"
        )

        priority = self._calculate_strategy_priority(
            goal=goal,
            strategy=strategy,
        )

        entry = Recommendation(
            title="Marketing Strategy Recommendation",
            content=content,
            confidence=strategy.confidence,
            source=self.SOURCE,
            tags=[
                "marketing",
                "strategy",
                "growth",
                *channel_names,
            ],
            metadata={
                "strategy_name": strategy.strategy_name,
                "objective": goal.objective,
                "timeline_days": goal.timeline_days,
                "channels": channel_names,
                "success_metrics": (
                    strategy.success_metrics
                ),
            },
            priority=priority,
        )

        return self.memory_manager.remember(
            business.business_id,
            entry,
        )

    def _store_budget_recommendation(
        self,
        business: MarketingBusinessProfile,
        budget: MarketingBudgetPlan,
    ) -> Recommendation:
        allocation_summary = ", ".join(
            (
                f"{item.channel}: "
                f"{item.amount:.2f} "
                f"{budget.currency}"
            )
            for item in budget.allocations
        )

        if not allocation_summary:
            allocation_summary = (
                "No paid channel allocations"
            )

        content = (
            f"Recommended monthly marketing budget: "
            f"{budget.total_budget:.2f} "
            f"{budget.currency}. "
            f"Channel allocations: "
            f"{allocation_summary}. "
            f"Reserve: {budget.reserve_amount:.2f} "
            f"{budget.currency}."
        )

        entry = Recommendation(
            title="Marketing Budget Recommendation",
            content=content,
            confidence=0.80,
            source=self.SOURCE,
            tags=[
                "marketing",
                "budget",
                "allocation",
            ],
            metadata={
                "total_budget": budget.total_budget,
                "currency": budget.currency,
                "reserve_amount": budget.reserve_amount,
                "allocations": [
                    {
                        "channel": item.channel,
                        "amount": item.amount,
                        "percentage": item.percentage,
                    }
                    for item in budget.allocations
                ],
            },
            priority=7,
        )

        return self.memory_manager.remember(
            business.business_id,
            entry,
        )

    def _store_campaign_observation(
        self,
        business: MarketingBusinessProfile,
        campaign: MarketingCampaignPlan,
    ) -> Observation:
        weekly_themes = [
            week.theme
            for week in campaign.weeks
        ]

        content = (
            f"Campaign '{campaign.campaign_name}' "
            f"was prepared for {campaign.duration_days} days "
            f"with {len(campaign.weeks)} campaign weeks. "
            f"Campaign objective: "
            f"{campaign.campaign_objective}"
        )

        entry = Observation(
            title="Marketing Campaign Plan",
            content=content,
            confidence=0.80,
            source=self.SOURCE,
            tags=[
                "marketing",
                "campaign",
                "content",
                "planning",
            ],
            metadata={
                "campaign_name": campaign.campaign_name,
                "duration_days": campaign.duration_days,
                "status": campaign.status,
                "approval_required": (
                    campaign.approval_required
                ),
                "weekly_themes": weekly_themes,
            },
            evidence=weekly_themes,
        )

        return self.memory_manager.remember(
            business.business_id,
            entry,
        )

    def _store_prediction_observation(
        self,
        business: MarketingBusinessProfile,
        prediction: MarketingPrediction,
        goal: MarketingGoal,
    ) -> Observation:
        content = (
            f"Predicted marketing results include "
            f"{prediction.estimated_reach} reach, "
            f"{prediction.estimated_engagements} engagements, "
            f"{prediction.estimated_leads} leads, "
            f"{prediction.estimated_conversions} conversions, "
            f"and estimated revenue of "
            f"{prediction.estimated_revenue:.2f} "
            f"{goal.currency.upper()}. "
            f"Estimated ROI: "
            f"{prediction.estimated_roi_percentage:.2f}%."
        )

        entry = Observation(
            title="Marketing Performance Prediction",
            content=content,
            confidence=prediction.confidence,
            source=self.SOURCE,
            tags=[
                "marketing",
                "prediction",
                "performance",
                "roi",
                "leads",
            ],
            metadata={
                "estimated_reach": (
                    prediction.estimated_reach
                ),
                "estimated_engagements": (
                    prediction.estimated_engagements
                ),
                "estimated_leads": (
                    prediction.estimated_leads
                ),
                "estimated_conversions": (
                    prediction.estimated_conversions
                ),
                "estimated_revenue": (
                    prediction.estimated_revenue
                ),
                "estimated_roi_percentage": (
                    prediction.estimated_roi_percentage
                ),
                "currency": goal.currency.upper(),
                "assumptions": prediction.assumptions,
            },
            evidence=prediction.assumptions,
        )

        return self.memory_manager.remember(
            business.business_id,
            entry,
        )

    def _detect_and_store_patterns(
        self,
        business: MarketingBusinessProfile,
        strategy: MarketingStrategy,
        result: MarketingLearningResult,
    ) -> None:
        """
        Detect repeated channel recommendations.

        A pattern is stored only when a channel has appeared in
        at least two previous Marketing Director strategy memories.
        """

        previous_entries = self.memory_manager.search(
            business.business_id,
            category="recommendation",
            tags=["strategy"],
        )

        for channel in strategy.channels:
            previous_occurrences = sum(
                1
                for search_result in previous_entries
                if channel.channel
                in search_result.entry.metadata.get(
                    "channels",
                    [],
                )
            )

            if previous_occurrences < 2:
                continue

            pattern_title = (
                f"Recurring Marketing Channel: "
                f"{channel.channel}"
            )

            if self._active_memory_exists(
                business_id=business.business_id,
                title=pattern_title,
            ):
                continue

            pattern = Pattern(
                title=pattern_title,
                content=(
                    f"The channel '{channel.channel}' has "
                    f"been repeatedly recommended for "
                    f"{business.business_name}. This may "
                    f"indicate that it is a consistently "
                    f"relevant acquisition or engagement channel."
                ),
                confidence=min(
                    0.60
                    + previous_occurrences * 0.08,
                    0.90,
                ),
                source=self.SOURCE,
                tags=[
                    "marketing",
                    "pattern",
                    channel.channel,
                ],
                metadata={
                    "channel": channel.channel,
                    "previous_occurrences": (
                        previous_occurrences
                    ),
                },
                occurrences=(
                    previous_occurrences + 1
                ),
            )

            try:
                stored_pattern = (
                    self.memory_manager.remember(
                        business.business_id,
                        pattern,
                    )
                )

                self._register_created_entry(
                    result=result,
                    entry=stored_pattern,
                )

            except Exception as exc:
                result.warnings.append(
                    f"Could not store marketing pattern "
                    f"for {channel.channel}: {exc}"
                )

    def _active_memory_exists(
        self,
        business_id: str,
        title: str,
    ) -> bool:
        return any(
            entry.title == title
            for entry in self.memory_manager.recall(
                business_id
            )
        )

    @staticmethod
    def _calculate_strategy_priority(
        goal: MarketingGoal,
        strategy: MarketingStrategy,
    ) -> int:
        priority = 5

        if goal.timeline_days <= 30:
            priority += 1

        if goal.monthly_budget > 0:
            priority += 1

        if strategy.confidence >= 0.80:
            priority += 1

        return min(priority, 10)

    @staticmethod
    def _register_created_entry(
        result: MarketingLearningResult,
        entry: Any,
    ) -> None:
        result.entries_created += 1
        result.created_titles.append(entry.title)

        if isinstance(entry, Observation):
            result.observations_created += 1

        elif isinstance(entry, Recommendation):
            result.recommendations_created += 1

        elif isinstance(entry, Pattern):
            result.patterns_created += 1

        elif isinstance(entry, BusinessKnowledge):
            result.knowledge_created += 1

    @staticmethod
    def _tag_value(value: str) -> str:
        cleaned = value.strip().lower()

        return "_".join(
            cleaned.split()
        )


_marketing_learning_engine = MarketingLearningEngine()


def get_marketing_learning_engine() -> MarketingLearningEngine:
    """
    Return the shared Marketing Learning Engine instance.
    """

    return _marketing_learning_engine