from __future__ import annotations

from typing import Any

from app.services.competitor_intelligence.models import (
    CompetitorOpportunity,
)


INVALID_VALUES = {
    "",
    "not found",
    "missing",
    "website missing",
    "phone missing",
    "email missing",
    "none",
    "null",
    "undefined",
    "n/a",
}


def _has_value(value: Any) -> bool:
    cleaned = str(value or "").strip().lower()

    return bool(
        cleaned
        and cleaned not in INVALID_VALUES
    )


def identify_competitor_opportunities(
    competitor: dict[str, Any],
) -> list[CompetitorOpportunity]:
    opportunities: list[
        CompetitorOpportunity
    ] = []

    has_website = _has_value(
        competitor.get("website")
    )

    has_phone = _has_value(
        competitor.get("phone")
    )

    has_email = _has_value(
        competitor.get("email")
    )

    social_fields = (
        "facebook",
        "instagram",
        "linkedin",
        "tiktok",
        "x",
        "youtube",
    )

    social_count = sum(
        1
        for field in social_fields
        if _has_value(
            competitor.get(field)
        )
    )

    if not has_website:
        opportunities.append(
            CompetitorOpportunity(
                title="Website Advantage",
                description=(
                    "This competitor has no verified "
                    "website. A strong website with local "
                    "SEO and clear conversion paths could "
                    "create a significant advantage."
                ),
                priority="High",
                impact_score=90,
                category="Website",
            )
        )

    if not has_phone:
        opportunities.append(
            CompetitorOpportunity(
                title="Customer Accessibility",
                description=(
                    "Direct phone contact is missing from "
                    "the available profile. Better contact "
                    "accessibility may improve enquiry "
                    "conversion."
                ),
                priority="Medium",
                impact_score=65,
                category="Conversion",
            )
        )

    if not has_email:
        opportunities.append(
            CompetitorOpportunity(
                title="Email Lead Capture",
                description=(
                    "No public email address was found. "
                    "A clear enquiry channel and automated "
                    "email follow-up could improve lead "
                    "capture."
                ),
                priority="Medium",
                impact_score=60,
                category="Lead Capture",
            )
        )

    if social_count == 0:
        opportunities.append(
            CompetitorOpportunity(
                title="Social Media Gap",
                description=(
                    "No verified social profiles were "
                    "detected. Consistent social media "
                    "content and local campaigns could "
                    "create stronger visibility."
                ),
                priority="High",
                impact_score=80,
                category="Social Media",
            )
        )

    elif social_count <= 2:
        opportunities.append(
            CompetitorOpportunity(
                title="Social Channel Expansion",
                description=(
                    "The competitor has limited social "
                    "coverage. Stronger multi-channel "
                    "presence may create an engagement "
                    "advantage."
                ),
                priority="Medium",
                impact_score=60,
                category="Social Media",
            )
        )

    booking_page = competitor.get(
        "booking_page"
    )

    if not _has_value(
        booking_page
    ):
        opportunities.append(
            CompetitorOpportunity(
                title="Online Booking",
                description=(
                    "No verified online booking page was "
                    "detected. A fast appointment or lead "
                    "booking journey could improve "
                    "conversion."
                ),
                priority="High",
                impact_score=85,
                category="Conversion",
            )
        )

    seo_score = competitor.get(
        "seo_score"
    )

    try:
        seo_value = int(
            seo_score or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        seo_value = 0

    if (
        seo_value > 0
        and seo_value < 60
    ):
        opportunities.append(
            CompetitorOpportunity(
                title="SEO Opportunity",
                description=(
                    "SEO performance appears relatively "
                    "weak. Local search optimization and "
                    "high-intent service content could "
                    "help outrank this competitor."
                ),
                priority="High",
                impact_score=88,
                category="SEO",
            )
        )

    rating = competitor.get(
        "rating"
    )

    review_count = competitor.get(
        "review_count"
    )

    try:
        rating_value = float(
            rating or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        rating_value = 0.0

    try:
        review_count_value = int(
            review_count or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        review_count_value = 0

    if (
        rating_value > 0
        and (
            rating_value < 4.2
            or review_count_value < 50
        )
    ):
        opportunities.append(
            CompetitorOpportunity(
                title="Reputation Advantage",
                description=(
                    "The competitor's reputation signals "
                    "leave room for differentiation. A "
                    "strong customer review strategy may "
                    "improve local trust and visibility."
                ),
                priority="High",
                impact_score=82,
                category="Reputation",
            )
        )

    if not opportunities:
        opportunities.append(
            CompetitorOpportunity(
                title="Differentiation Opportunity",
                description=(
                    "No major digital weakness was found. "
                    "Differentiate through faster follow-up, "
                    "better customer experience, stronger "
                    "offers, and more focused campaigns."
                ),
                priority="Medium",
                impact_score=55,
                category="Strategy",
            )
        )

    opportunities.sort(
        key=lambda opportunity:
            opportunity.impact_score,
        reverse=True,
    )

    return opportunities[:6]