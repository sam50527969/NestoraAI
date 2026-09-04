from __future__ import annotations

from app.services.strategy_generator.models import (
    StrategyRoiForecast,
)


def build_roi_forecast(
    *,
    monthly_budget: float,
    average_sale_value: float,
    lead_conversion_rate: float = 0.25,
    estimated_cost_per_lead: float = 75.0,
    currency: str,
) -> StrategyRoiForecast:
    """
    Generate a simple ROI forecast.

    Future versions will use historical CRM data,
    campaign performance, seasonality, and AI
    predictions instead of fixed assumptions.
    """

    budget = max(
        0.0,
        float(monthly_budget or 0),
    )

    sale_value = max(
        0.0,
        float(average_sale_value or 0),
    )

    conversion_rate = max(
        0.0,
        min(
            1.0,
            float(lead_conversion_rate),
        ),
    )

    cost_per_lead = max(
        1.0,
        float(estimated_cost_per_lead),
    )

    estimated_leads = int(
        budget / cost_per_lead
    )

    estimated_customers = int(
        estimated_leads
        * conversion_rate
    )

    estimated_revenue = round(
        estimated_customers
        * sale_value,
        2,
    )

    if budget > 0:
        roi_percent = round(
            (
                (
                    estimated_revenue
                    - budget
                )
                / budget
            )
            * 100,
            1,
        )
    else:
        roi_percent = 0.0

    return StrategyRoiForecast(
        monthly_investment=budget,
        currency=currency,
        estimated_leads=estimated_leads,
        estimated_customers=estimated_customers,
        estimated_revenue=estimated_revenue,
        estimated_roi_percent=roi_percent,
        assumptions=[
            (
                "Lead generation cost is estimated at "
                f"{cost_per_lead:.2f} {currency}."
            ),
            (
                "Lead conversion rate is estimated at "
                f"{conversion_rate * 100:.0f}%."
            ),
            (
                "Average customer value is estimated at "
                f"{sale_value:.2f} {currency}."
            ),
            (
                "Forecast values are planning estimates "
                "and should be refined using actual CRM "
                "and campaign performance."
            ),
        ],
    )