from __future__ import annotations

from app.services.strategy_generator.models import (
    StrategyBudget,
    StrategyBudgetAllocation,
)


def build_budget_plan(
    *,
    monthly_budget: float,
    currency: str,
) -> StrategyBudget:
    """
    Create a balanced default marketing budget.

    The allocation is intentionally deterministic.
    Later we can make it adaptive based on business
    type, competitor gaps, campaign performance,
    and AI recommendations.
    """

    safe_budget = max(
        0.0,
        float(monthly_budget or 0),
    )

    if safe_budget <= 0:
        return StrategyBudget(
            monthly_budget=0.0,
            currency=currency,
            allocations=[],
            reserve_amount=0.0,
        )

    allocation_rules = [
        {
            "channel": "Google Ads",
            "percentage": 35,
            "purpose": (
                "Capture high-intent customers who are "
                "actively searching for relevant services."
            ),
        },
        {
            "channel": "SEO",
            "percentage": 25,
            "purpose": (
                "Improve organic visibility, local search "
                "presence, and long-term lead generation."
            ),
        },
        {
            "channel": "Social Media",
            "percentage": 15,
            "purpose": (
                "Build awareness, trust, engagement, and "
                "remarketing audiences."
            ),
        },
        {
            "channel": "Content",
            "percentage": 10,
            "purpose": (
                "Create educational and conversion-focused "
                "content for organic and paid campaigns."
            ),
        },
        {
            "channel": "CRM & Follow-up",
            "percentage": 5,
            "purpose": (
                "Improve lead nurturing, reminders, and "
                "customer follow-up."
            ),
        },
    ]

    reserve_percentage = 10

    allocations = []

    for rule in allocation_rules:
        amount = round(
            safe_budget
            * (
                rule["percentage"]
                / 100
            ),
            2,
        )

        allocations.append(
            StrategyBudgetAllocation(
                channel=rule["channel"],
                amount=amount,
                percentage=float(
                    rule["percentage"]
                ),
                purpose=rule["purpose"],
            )
        )

    reserve_amount = round(
        safe_budget
        * (
            reserve_percentage
            / 100
        ),
        2,
    )

    return StrategyBudget(
        monthly_budget=round(
            safe_budget,
            2,
        ),
        currency=currency,
        allocations=allocations,
        reserve_amount=reserve_amount,
    )