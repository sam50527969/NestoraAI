from __future__ import annotations

from app.services.strategy_generator.models import (
    StrategyContentItem,
)


def build_content_calendar(
    *,
    business_name: str,
    industry: str,
    location: str,
    timeline_days: int = 30,
) -> list[StrategyContentItem]:
    """
    Build a practical multi-channel content calendar.

    This first version is deterministic and designed
    to create a balanced mix of educational,
    promotional, trust-building, and conversion content.
    """

    safe_business_name = str(
        business_name or "Business"
    ).strip()

    safe_industry = str(
        industry or "business"
    ).strip().replace("_", " ")

    safe_location = str(
        location or "Doha"
    ).strip()

    safe_days = max(
        7,
        int(timeline_days or 30),
    )

    topics = [
        (
            "Instagram",
            "Educational",
            f"Common questions about {safe_industry}",
            "Build trust and educate potential customers.",
        ),
        (
            "Facebook",
            "Customer Proof",
            "Customer testimonial or success story",
            "Strengthen credibility and social proof.",
        ),
        (
            "Instagram",
            "Service Highlight",
            f"Highlight one key {safe_industry} service",
            "Increase awareness of profitable services.",
        ),
        (
            "Google Business",
            "Local Update",
            f"Why choose {safe_business_name} in {safe_location}",
            "Improve local visibility and conversion.",
        ),
        (
            "Instagram",
            "Behind the Scenes",
            "Meet the team or show the customer experience",
            "Humanize the brand and increase trust.",
        ),
        (
            "Facebook",
            "FAQ",
            f"Answer a frequent customer question about {safe_industry}",
            "Reduce objections and educate prospects.",
        ),
        (
            "Instagram",
            "Promotion",
            "Create a limited-time service offer",
            "Generate enquiries and short-term demand.",
        ),
        (
            "Google Business",
            "Reputation",
            "Share a recent customer review",
            "Reinforce trust and local reputation.",
        ),
        (
            "Instagram",
            "Educational",
            f"Top mistakes customers make when choosing a {safe_industry}",
            "Position the business as an expert.",
        ),
        (
            "Facebook",
            "Conversion",
            "Book now or contact us campaign",
            "Drive direct enquiries.",
        ),
        (
            "Instagram",
            "Comparison",
            f"What makes {safe_business_name} different",
            "Communicate differentiators clearly.",
        ),
        (
            "Google Business",
            "Service Highlight",
            f"Featured service in {safe_location}",
            "Capture high-intent local customers.",
        ),
    ]

    calendar: list[
        StrategyContentItem
    ] = []

    day = 1
    topic_index = 0

    while day <= safe_days:
        (
            channel,
            content_type,
            topic,
            objective,
        ) = topics[
            topic_index
            % len(topics)
        ]

        calendar.append(
            StrategyContentItem(
                day=day,
                channel=channel,
                content_type=content_type,
                topic=topic,
                objective=objective,
            )
        )

        topic_index += 1
        day += 3

    return calendar