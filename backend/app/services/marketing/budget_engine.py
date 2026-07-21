from __future__ import annotations

from app.schemas.marketing import (
    MarketingBudgetItem,
    MarketingBudgetPlan,
    MarketingGoal,
    MarketingStrategy,
)


class MarketingBudgetEngineError(RuntimeError):
    """Raised when a valid marketing budget plan cannot be produced."""


class MarketingBudgetEngine:
    """
    Converts a marketing strategy into a structured budget plan.

    The engine:

    - Uses the monthly budget from the marketing goal.
    - Reserves part of the budget for testing and optimization.
    - Allocates the remaining budget according to channel percentages.
    - Corrects rounding differences automatically.
    """

    DEFAULT_RESERVE_PERCENTAGE = 10.0

    def create_budget_plan(
        self,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
    ) -> MarketingBudgetPlan:
        """
        Create a channel-by-channel marketing budget plan.
        """

        self._validate_strategy(strategy)

        total_budget = round(
            goal.monthly_budget,
            2,
        )

        if total_budget <= 0:
            return self._create_zero_budget_plan(
                goal=goal,
                strategy=strategy,
            )

        reserve_percentage = self._determine_reserve_percentage(
            total_budget
        )

        reserve_amount = round(
            total_budget * reserve_percentage / 100,
            2,
        )

        distributable_budget = round(
            total_budget - reserve_amount,
            2,
        )

        allocations = self._build_allocations(
            strategy=strategy,
            distributable_budget=distributable_budget,
        )

        self._correct_rounding_difference(
            allocations=allocations,
            expected_total=distributable_budget,
        )

        notes = self._build_notes(
            total_budget=total_budget,
            reserve_percentage=reserve_percentage,
            reserve_amount=reserve_amount,
        )

        budget_plan = MarketingBudgetPlan(
            total_budget=total_budget,
            currency=goal.currency.upper(),
            allocations=allocations,
            reserve_amount=reserve_amount,
            notes=notes,
        )

        self._validate_budget_plan(
            budget_plan
        )

        return budget_plan

    @staticmethod
    def _validate_strategy(
        strategy: MarketingStrategy,
    ) -> None:
        if not strategy.channels:
            raise MarketingBudgetEngineError(
                "The marketing strategy must contain at least "
                "one channel before a budget can be created."
            )

        total_percentage = sum(
            channel.budget_percentage
            for channel in strategy.channels
        )

        if abs(total_percentage - 100) > 0.1:
            raise MarketingBudgetEngineError(
                "Marketing channel percentages must equal 100."
            )

    def _create_zero_budget_plan(
        self,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
    ) -> MarketingBudgetPlan:
        allocations = [
            MarketingBudgetItem(
                channel=channel.channel,
                amount=0,
                percentage=channel.budget_percentage,
                rationale=(
                    f"No paid budget is currently available. "
                    f"Use this channel organically because "
                    f"{channel.rationale}"
                ),
            )
            for channel in strategy.channels
        ]

        return MarketingBudgetPlan(
            total_budget=0,
            currency=goal.currency.upper(),
            allocations=allocations,
            reserve_amount=0,
            notes=[
                (
                    "No paid marketing budget was supplied. "
                    "The campaign should begin with organic execution."
                ),
                (
                    "Channel percentages represent effort priority, "
                    "not cash expenditure."
                ),
                (
                    "Introduce a paid test budget after baseline "
                    "performance has been measured."
                ),
            ],
        )

    def _determine_reserve_percentage(
        self,
        total_budget: float,
    ) -> float:
        """
        Use a larger reserve for very small budgets because testing
        and optimization risk is proportionally higher.
        """

        if total_budget < 1000:
            return 5.0

        if total_budget < 3000:
            return 8.0

        return self.DEFAULT_RESERVE_PERCENTAGE

    def _build_allocations(
        self,
        strategy: MarketingStrategy,
        distributable_budget: float,
    ) -> list[MarketingBudgetItem]:
        allocations: list[MarketingBudgetItem] = []

        for channel_strategy in strategy.channels:
            amount = round(
                distributable_budget
                * channel_strategy.budget_percentage
                / 100,
                2,
            )

            allocations.append(
                MarketingBudgetItem(
                    channel=channel_strategy.channel,
                    amount=amount,
                    percentage=channel_strategy.budget_percentage,
                    rationale=self._build_rationale(
                        channel_objective=channel_strategy.objective,
                        channel_rationale=channel_strategy.rationale,
                    ),
                )
            )

        return allocations

    @staticmethod
    def _build_rationale(
        channel_objective: str,
        channel_rationale: str,
    ) -> str:
        return (
            f"Objective: {channel_objective} "
            f"Allocation rationale: {channel_rationale}"
        )

    @staticmethod
    def _correct_rounding_difference(
        allocations: list[MarketingBudgetItem],
        expected_total: float,
    ) -> None:
        if not allocations:
            return

        allocated_total = round(
            sum(
                item.amount
                for item in allocations
            ),
            2,
        )

        difference = round(
            expected_total - allocated_total,
            2,
        )

        if difference == 0:
            return

        largest_allocation = max(
            allocations,
            key=lambda item: item.amount,
        )

        largest_allocation.amount = round(
            largest_allocation.amount + difference,
            2,
        )

    @staticmethod
    def _build_notes(
        total_budget: float,
        reserve_percentage: float,
        reserve_amount: float,
    ) -> list[str]:
        notes = [
            (
                f"{reserve_percentage:.0f}% of the monthly budget "
                f"({reserve_amount:.2f}) is reserved for testing, "
                "optimization, and unexpected opportunities."
            ),
            (
                "Channel allocations should be reviewed weekly "
                "against lead quality and conversion performance."
            ),
            (
                "Move budget away from channels producing weak "
                "qualified-lead results."
            ),
        ]

        if total_budget < 3000:
            notes.append(
                "Because the available budget is limited, execution "
                "should remain focused on the highest-priority channels."
            )

        return notes

    @staticmethod
    def _validate_budget_plan(
        budget_plan: MarketingBudgetPlan,
    ) -> None:
        allocated_total = round(
            sum(
                item.amount
                for item in budget_plan.allocations
            ),
            2,
        )

        combined_total = round(
            allocated_total + budget_plan.reserve_amount,
            2,
        )

        if abs(
            combined_total - budget_plan.total_budget
        ) > 0.01:
            raise MarketingBudgetEngineError(
                "Budget allocations and reserve do not equal "
                "the total marketing budget."
            )

        percentage_total = sum(
            item.percentage
            for item in budget_plan.allocations
        )

        if abs(percentage_total - 100) > 0.1:
            raise MarketingBudgetEngineError(
                "Budget allocation percentages must equal 100."
            )


_marketing_budget_engine = MarketingBudgetEngine()


def get_marketing_budget_engine() -> MarketingBudgetEngine:
    """
    Return the shared Marketing Budget Engine instance.
    """

    return _marketing_budget_engine