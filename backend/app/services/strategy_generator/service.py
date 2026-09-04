from __future__ import annotations

from typing import Any

from app.services.strategy_generator.ads import (
    build_ad_campaigns,
)
from app.services.strategy_generator.budget import (
    build_budget_plan,
)
from app.services.strategy_generator.content import (
    build_content_calendar,
)
from app.services.strategy_generator.email import (
    build_email_sequence,
)
from app.services.strategy_generator.models import (
    GrowthStrategyReport,
)
from app.services.strategy_generator.roi import (
    build_roi_forecast,
)
from app.services.strategy_generator.seo import (
    build_seo_plan,
)
from app.services.strategy_generator.timeline import (
    build_strategy_timeline,
)


class StrategyGeneratorService:
    """
    Build a complete growth strategy from business
    context and competitor intelligence.
    """

    def generate(
        self,
        *,
        business_name: str,
        industry: str,
        location: str,
        objective: str,
        timeline_days: int = 90,
        monthly_budget: float = 0.0,
        currency: str,
        average_sale_value: float = 500.0,
        competitor_context: list[
            dict[str, Any]
        ] | None = None,
        additional_context: dict[
            str,
            Any,
        ] | None = None,
    ) -> GrowthStrategyReport:
        safe_business_name = str(
            business_name or "Business"
        ).strip()

        safe_industry = str(
            industry or "business"
        ).strip()

        safe_location = str(location).strip()

        safe_objective = str(
            objective
            or "Increase qualified leads and revenue"
        ).strip()

        safe_timeline = max(
            30,
            min(
                int(timeline_days or 90),
                365,
            ),
        )

        safe_budget = max(
            0.0,
            float(monthly_budget or 0),
        )

        safe_sale_value = max(
            0.0,
            float(average_sale_value or 0),
        )

        competitors = (
            competitor_context
            or []
        )

        budget = build_budget_plan(
            monthly_budget=safe_budget,
            currency=currency,
        )

        seo_plan = build_seo_plan(
            business_name=safe_business_name,
            industry=safe_industry,
            location=safe_location,
            competitor_context=competitors,
        )

        ad_campaigns = build_ad_campaigns(
            business_name=safe_business_name,
            industry=safe_industry,
            location=safe_location,
            monthly_budget=safe_budget,
            competitor_context=competitors,
        )

        content_calendar = (
            build_content_calendar(
                business_name=safe_business_name,
                industry=safe_industry,
                location=safe_location,
                timeline_days=min(
                    safe_timeline,
                    90,
                ),
            )
        )

        email_sequence = (
            build_email_sequence(
                business_name=safe_business_name,
                industry=safe_industry,
            )
        )

        timeline = build_strategy_timeline(
            business_name=safe_business_name,
            timeline_days=safe_timeline,
        )

        roi_forecast = build_roi_forecast(
            monthly_budget=safe_budget,
            average_sale_value=safe_sale_value,
            currency=currency,
        )

        priorities = self._build_priorities(
            competitors
        )

        confidence = self._calculate_confidence(
            business_name=safe_business_name,
            industry=safe_industry,
            location=safe_location,
            monthly_budget=safe_budget,
            competitors=competitors,
        )

        executive_summary = (
            self._build_executive_summary(
                business_name=safe_business_name,
                objective=safe_objective,
                timeline_days=safe_timeline,
                monthly_budget=safe_budget,
                currency=currency,
                competitors=competitors,
                priorities=priorities,
            )
        )

        assumptions = [
            (
                "The strategy is based on currently "
                "available business and competitor data."
            ),
            (
                "Budget allocation should be adjusted "
                "after real campaign performance becomes "
                "available."
            ),
            (
                "ROI is a planning estimate, not a "
                "guaranteed financial result."
            ),
            (
                "Competitor intelligence quality depends "
                "on the amount of verified public data "
                "available."
            ),
        ]

        return GrowthStrategyReport(
            business_name=safe_business_name,
            objective=safe_objective,
            timeline_days=safe_timeline,
            budget=budget,
            seo_plan=seo_plan,
            ad_campaigns=ad_campaigns,
            content_calendar=content_calendar,
            email_sequence=email_sequence,
            timeline=timeline,
            roi_forecast=roi_forecast,
            executive_summary=executive_summary,
            priorities=priorities,
            assumptions=assumptions,
            confidence=confidence,
            raw_context={
                "industry": safe_industry,
                "location": safe_location,
                "competitors": competitors,
                "additional_context": (
                    additional_context
                    or {}
                ),
            },
        )

    @staticmethod
    def _build_priorities(
        competitors: list[
            dict[str, Any]
        ],
    ) -> list[str]:
        priorities = [
            "Improve conversion paths and lead follow-up.",
            "Strengthen local SEO and high-intent search visibility.",
            "Build a consistent reputation and review strategy.",
            "Launch measurable paid acquisition campaigns.",
        ]

        strong_competitors = [
            competitor
            for competitor in competitors
            if int(
                competitor.get(
                    "profileStrength",
                    0,
                )
                or 0
            ) >= 70
        ]

        weak_competitors = [
            competitor
            for competitor in competitors
            if int(
                competitor.get(
                    "profileStrength",
                    0,
                )
                or 0
            ) < 50
        ]

        if strong_competitors:
            priorities.insert(
                0,
                (
                    "Differentiate clearly from strong "
                    "local competitors."
                ),
            )

        if weak_competitors:
            priorities.append(
                (
                    "Exploit digital gaps among weaker "
                    "competitors before they improve."
                )
            )

        return priorities[:6]

    @staticmethod
    def _calculate_confidence(
        *,
        business_name: str,
        industry: str,
        location: str,
        monthly_budget: float,
        competitors: list[
            dict[str, Any]
        ],
    ) -> int:
        score = 35

        if business_name:
            score += 10

        if industry:
            score += 10

        if location:
            score += 10

        if monthly_budget > 0:
            score += 10

        if competitors:
            score += 15

        enriched_competitors = [
            competitor
            for competitor in competitors
            if int(
                competitor.get(
                    "intelligenceConfidence",
                    0,
                )
                or 0
            ) >= 60
        ]

        if enriched_competitors:
            score += 10

        return min(
            score,
            100,
        )

    @staticmethod
    def _build_executive_summary(
        *,
        business_name: str,
        objective: str,
        timeline_days: int,
        monthly_budget: float,
        currency: str,
        competitors: list[
            dict[str, Any]
        ],
        priorities: list[str],
    ) -> str:
        competitor_count = len(
            competitors
        )

        priority_text = (
            priorities[0]
            if priorities
            else (
                "Improve digital visibility and "
                "customer acquisition."
            )
        )

        if monthly_budget > 0:
            budget_text = (
                f"with a monthly marketing budget of "
                f"{monthly_budget:,.0f} {currency}"
            )
        else:
            budget_text = (
                "with the marketing budget to be "
                "confirmed"
            )

        return (
            f"This {timeline_days}-day growth strategy "
            f"for {business_name} is designed to "
            f"{objective.lower()} {budget_text}. "
            f"Nestora analyzed {competitor_count} "
            f"competitor records and recommends "
            f"prioritizing: {priority_text}"
        )