from __future__ import annotations

from app.schemas.marketing import (
    MarketingBudgetPlan,
    MarketingCampaignPlan,
    MarketingGoal,
    MarketingPrediction,
    MarketingStrategy,
)


class MarketingPredictionEngineError(RuntimeError):
    """Raised when marketing results cannot be estimated."""


class MarketingPredictionEngine:
    """
    Produces conservative marketing performance estimates.

    These predictions are planning estimates, not guaranteed results.
    The engine uses the available budget, selected channels, campaign
    duration, and strategy expectations to calculate:

    - Estimated reach
    - Estimated engagements
    - Estimated leads
    - Estimated conversions
    - Estimated revenue
    - Estimated ROI
    - Confidence score
    """

    DEFAULT_COST_PER_LEAD = 125.0
    DEFAULT_LEAD_CONVERSION_RATE = 0.20
    DEFAULT_ENGAGEMENT_RATE = 0.025
    DEFAULT_REACH_PER_CURRENCY_UNIT = 18.0
    DEFAULT_AVERAGE_CONVERSION_VALUE = 350.0

    CHANNEL_REACH_MULTIPLIERS: dict[str, float] = {
        "instagram": 1.25,
        "facebook": 1.15,
        "linkedin": 0.65,
        "tiktok": 1.45,
        "x": 0.80,
        "email": 0.55,
        "whatsapp": 0.45,
        "google_business": 0.75,
        "google_ads": 1.10,
    }

    CHANNEL_LEAD_MULTIPLIERS: dict[str, float] = {
        "instagram": 0.85,
        "facebook": 0.90,
        "linkedin": 0.75,
        "tiktok": 0.65,
        "x": 0.55,
        "email": 1.05,
        "whatsapp": 1.30,
        "google_business": 1.20,
        "google_ads": 1.35,
    }

    def create_prediction(
        self,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
        budget: MarketingBudgetPlan,
        campaign: MarketingCampaignPlan,
        average_conversion_value: float | None = None,
    ) -> MarketingPrediction:
        """
        Create conservative marketing performance estimates.
        """

        self._validate_inputs(
            goal=goal,
            strategy=strategy,
            budget=budget,
            campaign=campaign,
        )

        conversion_value = (
            average_conversion_value
            if average_conversion_value is not None
            else self.DEFAULT_AVERAGE_CONVERSION_VALUE
        )

        if conversion_value < 0:
            raise MarketingPredictionEngineError(
                "Average conversion value cannot be negative."
            )

        campaign_months = max(
            campaign.duration_days / 30,
            1 / 30,
        )

        effective_budget = round(
            budget.total_budget * campaign_months,
            2,
        )

        estimated_reach = self._estimate_reach(
            strategy=strategy,
            budget=budget,
            campaign_months=campaign_months,
        )

        estimated_engagements = self._estimate_engagements(
            estimated_reach=estimated_reach,
            strategy=strategy,
        )

        estimated_leads = self._estimate_leads(
            strategy=strategy,
            effective_budget=effective_budget,
            campaign_months=campaign_months,
        )

        estimated_conversions = self._estimate_conversions(
            estimated_leads=estimated_leads,
            strategy=strategy,
        )

        estimated_revenue = round(
            estimated_conversions * conversion_value,
            2,
        )

        estimated_roi_percentage = self._calculate_roi(
            estimated_revenue=estimated_revenue,
            effective_budget=effective_budget,
        )

        confidence = self._calculate_confidence(
            strategy=strategy,
            budget=budget,
            campaign=campaign,
        )

        assumptions = self._build_assumptions(
            goal=goal,
            campaign=campaign,
            effective_budget=effective_budget,
            conversion_value=conversion_value,
        )

        return MarketingPrediction(
            estimated_reach=estimated_reach,
            estimated_engagements=estimated_engagements,
            estimated_leads=estimated_leads,
            estimated_conversions=estimated_conversions,
            estimated_revenue=estimated_revenue,
            estimated_roi_percentage=estimated_roi_percentage,
            confidence=confidence,
            assumptions=assumptions,
        )

    @staticmethod
    def _validate_inputs(
        goal: MarketingGoal,
        strategy: MarketingStrategy,
        budget: MarketingBudgetPlan,
        campaign: MarketingCampaignPlan,
    ) -> None:
        if not strategy.channels:
            raise MarketingPredictionEngineError(
                "A marketing strategy with at least one channel is required."
            )

        if not campaign.weeks:
            raise MarketingPredictionEngineError(
                "A campaign plan with at least one week is required."
            )

        if campaign.duration_days != goal.timeline_days:
            raise MarketingPredictionEngineError(
                "Campaign duration must match the marketing goal timeline."
            )

        if budget.total_budget < 0:
            raise MarketingPredictionEngineError(
                "Marketing budget cannot be negative."
            )

    def _estimate_reach(
        self,
        strategy: MarketingStrategy,
        budget: MarketingBudgetPlan,
        campaign_months: float,
    ) -> int:
        if budget.total_budget <= 0:
            organic_reach = (
                len(strategy.channels)
                * max(250, round(500 * campaign_months))
            )

            return max(
                int(organic_reach),
                250,
            )

        total_reach = 0.0

        allocation_lookup = {
            allocation.channel: allocation.amount
            for allocation in budget.allocations
        }

        for channel_strategy in strategy.channels:
            channel_budget = allocation_lookup.get(
                channel_strategy.channel,
                0,
            )

            multiplier = self.CHANNEL_REACH_MULTIPLIERS.get(
                channel_strategy.channel,
                1.0,
            )

            total_reach += (
                channel_budget
                * campaign_months
                * self.DEFAULT_REACH_PER_CURRENCY_UNIT
                * multiplier
            )

        return max(
            round(total_reach),
            len(strategy.channels) * 100,
        )

    def _estimate_engagements(
        self,
        estimated_reach: int,
        strategy: MarketingStrategy,
    ) -> int:
        engagement_rate = self.DEFAULT_ENGAGEMENT_RATE

        high_engagement_channels = {
            "instagram",
            "facebook",
            "tiktok",
            "whatsapp",
        }

        high_engagement_count = sum(
            1
            for channel in strategy.channels
            if channel.channel in high_engagement_channels
        )

        engagement_rate += min(
            high_engagement_count * 0.004,
            0.016,
        )

        return max(
            round(estimated_reach * engagement_rate),
            len(strategy.channels),
        )

    def _estimate_leads(
        self,
        strategy: MarketingStrategy,
        effective_budget: float,
        campaign_months: float,
    ) -> int:
        strategy_expected_leads = sum(
            channel.expected_leads
            for channel in strategy.channels
        )

        adjusted_strategy_leads = round(
            strategy_expected_leads * campaign_months
        )

        if effective_budget <= 0:
            return max(
                adjusted_strategy_leads,
                len(strategy.channels) * 2,
            )

        weighted_multiplier = self._weighted_lead_multiplier(
            strategy
        )

        budget_based_leads = round(
            effective_budget
            / self.DEFAULT_COST_PER_LEAD
            * weighted_multiplier
        )

        if adjusted_strategy_leads <= 0:
            return max(
                budget_based_leads,
                len(strategy.channels),
            )

        blended_estimate = round(
            budget_based_leads * 0.65
            + adjusted_strategy_leads * 0.35
        )

        return max(
            blended_estimate,
            len(strategy.channels),
        )

    def _weighted_lead_multiplier(
        self,
        strategy: MarketingStrategy,
    ) -> float:
        weighted_total = 0.0

        for channel in strategy.channels:
            multiplier = self.CHANNEL_LEAD_MULTIPLIERS.get(
                channel.channel,
                1.0,
            )

            weight = channel.budget_percentage / 100

            weighted_total += multiplier * weight

        return max(
            weighted_total,
            0.5,
        )

    def _estimate_conversions(
        self,
        estimated_leads: int,
        strategy: MarketingStrategy,
    ) -> int:
        conversion_rate = self.DEFAULT_LEAD_CONVERSION_RATE

        direct_response_channels = {
            "whatsapp",
            "email",
            "google_business",
            "google_ads",
        }

        direct_channel_count = sum(
            1
            for channel in strategy.channels
            if channel.channel in direct_response_channels
        )

        conversion_rate += min(
            direct_channel_count * 0.02,
            0.08,
        )

        return max(
            round(estimated_leads * conversion_rate),
            0,
        )

    @staticmethod
    def _calculate_roi(
        estimated_revenue: float,
        effective_budget: float,
    ) -> float:
        if effective_budget <= 0:
            return 0.0

        roi = (
            estimated_revenue - effective_budget
        ) / effective_budget * 100

        return round(
            roi,
            2,
        )

    @staticmethod
    def _calculate_confidence(
        strategy: MarketingStrategy,
        budget: MarketingBudgetPlan,
        campaign: MarketingCampaignPlan,
    ) -> float:
        confidence = strategy.confidence * 0.70

        if budget.total_budget > 0:
            confidence += 0.08

        if len(strategy.channels) in {
            2,
            3,
            4,
        }:
            confidence += 0.05

        if len(campaign.weeks) >= 4:
            confidence += 0.05

        if campaign.approval_required:
            confidence += 0.02

        return round(
            min(
                max(confidence, 0.35),
                0.90,
            ),
            2,
        )

    @staticmethod
    def _build_assumptions(
        goal: MarketingGoal,
        campaign: MarketingCampaignPlan,
        effective_budget: float,
        conversion_value: float,
    ) -> list[str]:
        assumptions = [
            (
                "Predictions are planning estimates and are not "
                "guaranteed business results."
            ),
            (
                "The campaign is executed consistently throughout "
                f"the full {campaign.duration_days}-day timeline."
            ),
            (
                "New enquiries receive timely and professional follow-up."
            ),
            (
                "Lead quality and conversion performance remain reasonably "
                "consistent during the campaign."
            ),
            (
                f"The estimated value of each conversion is "
                f"{conversion_value:.2f} {goal.currency.upper()}."
            ),
        ]

        if effective_budget <= 0:
            assumptions.append(
                "The campaign relies mainly on organic marketing activity."
            )
        else:
            assumptions.append(
                f"The effective campaign budget is approximately "
                f"{effective_budget:.2f} {goal.currency.upper()}."
            )

        if goal.approval_required:
            assumptions.append(
                "Required approvals are completed without major campaign delays."
            )

        return assumptions


_marketing_prediction_engine = MarketingPredictionEngine()


def get_marketing_prediction_engine() -> MarketingPredictionEngine:
    """
    Return the shared Marketing Prediction Engine instance.
    """

    return _marketing_prediction_engine