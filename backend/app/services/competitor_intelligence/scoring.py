from __future__ import annotations

from typing import Any

from app.services.competitor_intelligence.models import (
    CompetitorScoreBreakdown,
    CompetitorStrengthScore,
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


def _count_social_profiles(
    competitor: dict[str, Any],
) -> int:
    social_fields = (
        "facebook",
        "instagram",
        "linkedin",
        "tiktok",
        "x",
        "youtube",
    )

    return sum(
        1
        for field in social_fields
        if _has_value(
            competitor.get(field)
        )
    )


def _score_label(score: int) -> str:
    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Strong"

    if score >= 50:
        return "Moderate"

    if score >= 30:
        return "Weak"

    return "Very Weak"


def calculate_competitor_strength(
    competitor: dict[str, Any],
) -> CompetitorStrengthScore:
    """
    Calculate competitor strength from available,
    verifiable business signals.

    The maximum score is 100.
    """

    breakdown = CompetitorScoreBreakdown()

    if _has_value(
        competitor.get("website")
    ):
        breakdown.website = 15

    if _has_value(
        competitor.get("phone")
    ):
        breakdown.phone = 10

    if _has_value(
        competitor.get("email")
    ):
        breakdown.email = 10

    social_count = _count_social_profiles(
        competitor
    )

    if social_count >= 5:
        breakdown.social_presence = 15
    elif social_count >= 3:
        breakdown.social_presence = 12
    elif social_count >= 1:
        breakdown.social_presence = 6

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

    if website_status == "completed":
        if website_confidence >= 80:
            breakdown.website_quality = 15
        elif website_confidence >= 50:
            breakdown.website_quality = 10
        else:
            breakdown.website_quality = 5

    rating = competitor.get("rating")
    review_count = competitor.get(
        "review_count"
    )

    try:
        rating_value = float(rating)
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

    if rating_value > 0:
        if (
            rating_value >= 4.5
            and review_count_value >= 100
        ):
            breakdown.reputation = 15

        elif (
            rating_value >= 4.0
            and review_count_value >= 25
        ):
            breakdown.reputation = 10

        else:
            breakdown.reputation = 5

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
        breakdown.seo = 10
    elif seo_value >= 60:
        breakdown.seo = 7
    elif seo_value > 0:
        breakdown.seo = 4

    completeness_signals = [
        competitor.get("location"),
        competitor.get("category"),
        competitor.get("website"),
        competitor.get("phone"),
        competitor.get("email"),
    ]

    completed_signals = sum(
        1
        for value in completeness_signals
        if _has_value(value)
    )

    if completed_signals == 5:
        breakdown.completeness = 10
    elif completed_signals >= 4:
        breakdown.completeness = 8
    elif completed_signals >= 3:
        breakdown.completeness = 5
    elif completed_signals >= 2:
        breakdown.completeness = 3

    score = min(
        100,
        (
            breakdown.website
            + breakdown.phone
            + breakdown.email
            + breakdown.social_presence
            + breakdown.website_quality
            + breakdown.reputation
            + breakdown.seo
            + breakdown.completeness
        ),
    )

    evidence_groups = [
        breakdown.website,
        breakdown.phone,
        breakdown.email,
        breakdown.social_presence,
        breakdown.website_quality,
        breakdown.reputation,
        breakdown.seo,
        breakdown.completeness,
    ]

    evidence_count = sum(
        1
        for value in evidence_groups
        if value > 0
    )

    confidence = min(
        100,
        25 + evidence_count * 10,
    )

    return CompetitorStrengthScore(
        score=score,
        label=_score_label(score),
        breakdown=breakdown,
        confidence=confidence,
    )