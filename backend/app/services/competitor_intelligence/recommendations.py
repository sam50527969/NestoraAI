from __future__ import annotations

from typing import Any

from app.services.competitor_intelligence.models import (
    CompetitorOpportunity,
    CompetitorRecommendation,
)


def _priority_rank(
    priority: str,
) -> int:
    mapping = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    return mapping.get(
        priority,
        0,
    )


def _recommendation_from_opportunity(
    opportunity: CompetitorOpportunity,
) -> CompetitorRecommendation:
    category = (
        opportunity.category
        or "Strategy"
    )

    title = opportunity.title

    if category == "Website":
        return CompetitorRecommendation(
            title="Build a Stronger Website Experience",
            action=(
                "Create or improve a conversion-focused "
                "website with clear services, trust signals, "
                "local SEO pages, contact options, and "
                "online enquiry paths."
            ),
            priority=opportunity.priority,
            estimated_impact="High",
            suggested_channel="Website",
            reasoning=opportunity.description,
        )

    if category == "Conversion":
        return CompetitorRecommendation(
            title="Improve Lead Conversion",
            action=(
                "Make phone, WhatsApp, enquiry forms, and "
                "appointment booking easy to access across "
                "the customer journey."
            ),
            priority=opportunity.priority,
            estimated_impact="High",
            suggested_channel="Website / WhatsApp",
            reasoning=opportunity.description,
        )

    if category == "Lead Capture":
        return CompetitorRecommendation(
            title="Strengthen Lead Capture",
            action=(
                "Add structured enquiry forms, email "
                "capture, automated acknowledgements, "
                "and follow-up workflows."
            ),
            priority=opportunity.priority,
            estimated_impact="Medium",
            suggested_channel="Email / CRM",
            reasoning=opportunity.description,
        )

    if category == "Social Media":
        return CompetitorRecommendation(
            title="Expand Social Visibility",
            action=(
                "Publish consistent educational, proof-based, "
                "and promotional content across the most "
                "relevant social channels."
            ),
            priority=opportunity.priority,
            estimated_impact="Medium to High",
            suggested_channel="Social Media",
            reasoning=opportunity.description,
        )

    if category == "SEO":
        return CompetitorRecommendation(
            title="Attack Local Search Gaps",
            action=(
                "Create optimized service pages, improve "
                "local SEO signals, strengthen internal "
                "linking, and target high-intent local "
                "search terms."
            ),
            priority=opportunity.priority,
            estimated_impact="High",
            suggested_channel="SEO",
            reasoning=opportunity.description,
        )

    if category == "Reputation":
        return CompetitorRecommendation(
            title="Build a Reputation Advantage",
            action=(
                "Launch a structured customer review "
                "programme and actively improve review "
                "volume, quality, and response consistency."
            ),
            priority=opportunity.priority,
            estimated_impact="High",
            suggested_channel="Google Business / CRM",
            reasoning=opportunity.description,
        )

    return CompetitorRecommendation(
        title=title,
        action=(
            "Differentiate through faster follow-up, "
            "stronger customer experience, better offers, "
            "and focused marketing execution."
        ),
        priority=opportunity.priority,
        estimated_impact="Medium",
        suggested_channel="Multi-channel",
        reasoning=opportunity.description,
    )


def generate_competitor_recommendations(
    competitor: dict[str, Any],
    opportunities: list[
        CompetitorOpportunity
    ],
) -> list[CompetitorRecommendation]:
    del competitor

    recommendations = [
        _recommendation_from_opportunity(
            opportunity
        )
        for opportunity in opportunities
    ]

    recommendations.sort(
        key=lambda recommendation:
            _priority_rank(
                recommendation.priority
            ),
        reverse=True,
    )

    return recommendations[:6]