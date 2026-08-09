from __future__ import annotations

from typing import Any

from app.services.competitor_intelligence.models import (
    CompetitorIntelligenceReport,
)
from app.services.competitor_intelligence.opportunities import (
    identify_competitor_opportunities,
)
from app.services.competitor_intelligence.recommendations import (
    generate_competitor_recommendations,
)
from app.services.competitor_intelligence.scoring import (
    calculate_competitor_strength,
)
from app.services.competitor_intelligence.swot import (
    generate_competitor_swot,
)


class CompetitorIntelligenceService:
    """
    Convert one enriched competitor record into a
    complete executive intelligence report.
    """

    def analyze(
        self,
        competitor: dict[str, Any],
    ) -> CompetitorIntelligenceReport:
        competitor_name = str(
            competitor.get("businessName")
            or competitor.get("business_name")
            or competitor.get("name")
            or "Unknown competitor"
        ).strip()

        strength = calculate_competitor_strength(
            competitor
        )

        swot = generate_competitor_swot(
            competitor
        )

        opportunities = (
            identify_competitor_opportunities(
                competitor
            )
        )

        recommendations = (
            generate_competitor_recommendations(
                competitor,
                opportunities,
            )
        )

        market_position = (
            self._get_market_position(
                strength.score
            )
        )

        digital_maturity = (
            self._get_digital_maturity(
                strength.score
            )
        )

        confidence = self._calculate_report_confidence(
            strength_confidence=strength.confidence,
            enrichment_confidence=int(
                competitor.get(
                    "enrichment_confidence",
                    0,
                )
                or 0
            ),
            website_confidence=int(
                competitor.get(
                    "website_intelligence_confidence",
                    0,
                )
                or 0
            ),
        )

        summary = self._build_summary(
            competitor_name=competitor_name,
            score=strength.score,
            market_position=market_position,
            opportunities=opportunities,
        )

        return CompetitorIntelligenceReport(
            competitor_name=competitor_name,
            strength=strength,
            swot=swot,
            opportunities=opportunities,
            recommendations=recommendations,
            market_position=market_position,
            digital_maturity=digital_maturity,
            summary=summary,
            confidence=confidence,
            raw_signals={
                "website": competitor.get(
                    "website"
                ),
                "phone": competitor.get(
                    "phone"
                ),
                "email": competitor.get(
                    "email"
                ),
                "facebook": competitor.get(
                    "facebook"
                ),
                "instagram": competitor.get(
                    "instagram"
                ),
                "linkedin": competitor.get(
                    "linkedin"
                ),
                "rating": competitor.get(
                    "rating"
                ),
                "review_count": competitor.get(
                    "review_count"
                ),
                "seo_score": competitor.get(
                    "seo_score"
                ),
                "website_status": competitor.get(
                    "website_status"
                ),
                "website_intelligence_confidence":
                    competitor.get(
                        "website_intelligence_confidence"
                    ),
            },
        )

    @staticmethod
    def _get_market_position(
        score: int,
    ) -> str:
        if score >= 85:
            return "Market Leader"

        if score >= 70:
            return "Strong Competitor"

        if score >= 50:
            return "Established Competitor"

        if score >= 30:
            return "Developing Competitor"

        return "Low Digital Presence"

    @staticmethod
    def _get_digital_maturity(
        score: int,
    ) -> str:
        if score >= 85:
            return "Advanced"

        if score >= 70:
            return "Strong"

        if score >= 50:
            return "Moderate"

        if score >= 30:
            return "Basic"

        return "Limited"

    @staticmethod
    def _calculate_report_confidence(
        *,
        strength_confidence: int,
        enrichment_confidence: int,
        website_confidence: int,
    ) -> int:
        values = [
            strength_confidence,
            enrichment_confidence,
            website_confidence,
        ]

        valid_values = [
            value
            for value in values
            if value > 0
        ]

        if not valid_values:
            return 0

        return min(
            100,
            round(
                sum(valid_values)
                / len(valid_values)
            ),
        )

    @staticmethod
    def _build_summary(
        *,
        competitor_name: str,
        score: int,
        market_position: str,
        opportunities: list,
    ) -> str:
        if opportunities:
            top_opportunity = (
                opportunities[0].title
            )

            return (
                f"{competitor_name} is currently assessed "
                f"as a {market_position.lower()} with a "
                f"digital strength score of {score}%. "
                f"The strongest identified opportunity "
                f"is {top_opportunity.lower()}."
            )

        return (
            f"{competitor_name} has a digital strength "
            f"score of {score}% and is assessed as a "
            f"{market_position.lower()}."
        )