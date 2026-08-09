from __future__ import annotations

from typing import Any

from app.services.competitor_intelligence.models import (
    CompetitorSwot,
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


def _has_social_presence(
    competitor: dict[str, Any],
) -> bool:
    social_fields = (
        "facebook",
        "instagram",
        "linkedin",
        "tiktok",
        "x",
        "youtube",
    )

    return any(
        _has_value(
            competitor.get(field)
        )
        for field in social_fields
    )


def generate_competitor_swot(
    competitor: dict[str, Any],
) -> CompetitorSwot:
    strengths: list[str] = []
    weaknesses: list[str] = []
    opportunities: list[str] = []
    threats: list[str] = []

    has_website = _has_value(
        competitor.get("website")
    )

    has_phone = _has_value(
        competitor.get("phone")
    )

    has_email = _has_value(
        competitor.get("email")
    )

    has_social = _has_social_presence(
        competitor
    )

    website_status = str(
        competitor.get("website_status")
        or ""
    ).lower()

    website_confidence = int(
        competitor.get(
            "website_intelligence_confidence",
            0,
        )
        or 0
    )

    if has_website:
        strengths.append(
            "Verified business website is available."
        )
    else:
        weaknesses.append(
            "No verified official website was found."
        )

        opportunities.append(
            "A stronger website and local SEO presence could create a competitive advantage."
        )

    if has_phone:
        strengths.append(
            "Direct customer phone contact is available."
        )
    else:
        weaknesses.append(
            "Direct phone contact is missing from the available public profile."
        )

    if has_email:
        strengths.append(
            "A public business email address is available."
        )
    else:
        weaknesses.append(
            "No public business email address was found."
        )

        opportunities.append(
            "Better email accessibility could improve customer enquiries and lead capture."
        )

    if has_social:
        strengths.append(
            "The competitor has an established social media presence."
        )
    else:
        weaknesses.append(
            "Limited or no verified social media presence was detected."
        )

        opportunities.append(
            "Consistent social media activity could outperform this competitor in digital engagement."
        )

    if (
        website_status == "completed"
        and website_confidence >= 70
    ):
        strengths.append(
            "Website intelligence indicates a reasonably complete digital presence."
        )

    rating = competitor.get("rating")

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
        rating_value >= 4.5
        and review_count_value >= 100
    ):
        strengths.append(
            "Strong public reputation with high ratings and substantial review volume."
        )

        threats.append(
            "Strong customer reputation may make this competitor difficult to displace."
        )

    elif (
        rating_value > 0
        and rating_value < 4.0
    ):
        weaknesses.append(
            "Public rating suggests customer satisfaction may be below top competitors."
        )

        opportunities.append(
            "A stronger customer experience and review strategy could create an advantage."
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

    if seo_value >= 80:
        strengths.append(
            "Strong SEO signals indicate good search visibility."
        )

        threats.append(
            "Strong organic visibility may increase competition for local search traffic."
        )

    elif (
        seo_value > 0
        and seo_value < 60
    ):
        weaknesses.append(
            "SEO performance appears below a strong competitive benchmark."
        )

        opportunities.append(
            "Local SEO and high-intent service keywords may provide an opportunity to outrank this competitor."
        )

    if not opportunities:
        opportunities.append(
            "Differentiate through stronger customer follow-up, digital reputation, and conversion-focused campaigns."
        )

    if not threats:
        threats.append(
            "The competitor may strengthen its digital presence and marketing execution over time."
        )

    return CompetitorSwot(
        strengths=strengths[:6],
        weaknesses=weaknesses[:6],
        opportunities=opportunities[:6],
        threats=threats[:6],
    )