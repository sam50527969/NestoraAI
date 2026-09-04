from __future__ import annotations

from typing import Any

from app.services.strategy_generator.models import (
    StrategyAdCampaign,
)


def build_ad_campaigns(
    *,
    business_name: str,
    industry: str,
    location: str,
    monthly_budget: float,
    competitor_context: list[dict[str, Any]] | None = None,
) -> list[StrategyAdCampaign]:
    """
    Build a practical paid-media campaign plan.

    This version is deterministic. Later we can
    enhance it using real keyword CPC, search volume,
    conversion data, and campaign performance.
    """

    safe_business_name = str(
        business_name or "Business"
    ).strip()

    safe_industry = str(
        industry or "business"
    ).strip().replace("_", " ")

    safe_location = str(location).strip()

    safe_budget = max(
        0.0,
        float(monthly_budget or 0),
    )

    google_monthly = round(
        safe_budget * 0.35,
        2,
    )

    social_monthly = round(
        safe_budget * 0.15,
        2,
    )

    google_daily = round(
        google_monthly / 30,
        2,
    )

    social_daily = round(
        social_monthly / 30,
        2,
    )

    industry_lower = safe_industry.lower()

    campaigns = [
        StrategyAdCampaign(
            name=(
                f"{safe_business_name} "
                "High-Intent Search"
            ),
            channel="Google Ads",
            objective=(
                "Capture customers actively searching "
                "for relevant services."
            ),
            daily_budget=google_daily,
            audience=[
                f"People in {safe_location}",
                "High-intent service searchers",
                "Mobile users",
            ],
            keywords=[
                f"{industry_lower} {safe_location}",
                f"best {industry_lower} {safe_location}",
                f"{industry_lower} services {safe_location}",
                f"{industry_lower} near me",
            ],
            message=(
                f"Choose {safe_business_name} for trusted "
                f"{safe_industry.lower()} services in "
                f"{safe_location}."
            ),
        ),

        StrategyAdCampaign(
            name=(
                f"{safe_business_name} "
                "Local Awareness"
            ),
            channel="Meta Ads",
            objective=(
                "Increase local awareness and build "
                "remarketing audiences."
            ),
            daily_budget=social_daily,
            audience=[
                f"Adults in {safe_location}",
                "People interested in relevant services",
                "Website visitors",
                "Engaged social users",
            ],
            keywords=[],
            message=(
                f"Discover {safe_business_name} and learn "
                f"more about available services in "
                f"{safe_location}."
            ),
        ),
    ]

    if competitor_context:
        strong_competitors = [
            competitor
            for competitor in competitor_context
            if int(
                competitor.get(
                    "profileStrength",
                    0,
                )
                or 0
            ) >= 70
        ]

        if strong_competitors:
            campaigns.append(
                StrategyAdCampaign(
                    name="Competitor Gap Campaign",
                    channel="Google Ads",
                    objective=(
                        "Compete for high-intent searches "
                        "where strong local competitors are "
                        "already visible."
                    ),
                    daily_budget=round(
                        google_daily * 0.35,
                        2,
                    ),
                    audience=[
                        f"Customers in {safe_location}",
                        "High-intent local searchers",
                    ],
                    keywords=[
                        f"best {industry_lower} {safe_location}",
                        f"top {industry_lower} {safe_location}",
                        f"{industry_lower} reviews {safe_location}",
                    ],
                    message=(
                        f"Compare your options and choose "
                        f"{safe_business_name} for quality, "
                        "convenience, and responsive service."
                    ),
                )
            )

    return campaigns[:3]