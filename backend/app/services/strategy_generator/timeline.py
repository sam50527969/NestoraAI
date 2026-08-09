from __future__ import annotations

from app.services.strategy_generator.models import (
    StrategyTimelineAction,
)


def build_strategy_timeline(
    *,
    business_name: str,
    timeline_days: int = 90,
) -> list[StrategyTimelineAction]:
    """
    Build a phased execution roadmap.

    The current version is deterministic and divides
    implementation into practical growth phases.
    """

    safe_business_name = str(
        business_name or "Business"
    ).strip()

    safe_days = max(
        30,
        int(timeline_days or 90),
    )

    actions = [
        StrategyTimelineAction(
            period="Days 1-7",
            title="Business Intelligence Setup",
            description=(
                f"Validate {safe_business_name}'s business "
                "profile, website, competitors, contact "
                "information, analytics, and baseline KPIs."
            ),
            owner="Marketing Director",
            priority="High",
        ),

        StrategyTimelineAction(
            period="Days 1-14",
            title="Fix Conversion Foundations",
            description=(
                "Improve website calls-to-action, phone and "
                "WhatsApp visibility, enquiry forms, booking "
                "journeys, and lead tracking."
            ),
            owner="Marketing Director",
            priority="High",
        ),

        StrategyTimelineAction(
            period="Days 8-21",
            title="Local SEO Launch",
            description=(
                "Improve local search signals, service pages, "
                "metadata, business listings, reputation "
                "signals, and high-intent local keywords."
            ),
            owner="Marketing Director",
            priority="High",
        ),

        StrategyTimelineAction(
            period="Days 15-30",
            title="Content Engine Launch",
            description=(
                "Begin educational, trust-building, service, "
                "testimonial, and conversion-focused content "
                "across priority channels."
            ),
            owner="Marketing Director",
            priority="Medium",
        ),

        StrategyTimelineAction(
            period="Days 21-45",
            title="Paid Acquisition Launch",
            description=(
                "Launch high-intent Google Ads and local "
                "social campaigns with conversion tracking "
                "and controlled daily budgets."
            ),
            owner="Marketing Director",
            priority="High",
        ),

        StrategyTimelineAction(
            period="Days 30-60",
            title="CRM Follow-up Automation",
            description=(
                "Implement structured follow-up for new "
                "enquiries, inactive prospects, appointment "
                "reminders, and lead nurturing."
            ),
            owner="Sales Director",
            priority="High",
        ),

        StrategyTimelineAction(
            period="Days 45-75",
            title="Reputation Growth",
            description=(
                "Launch a systematic review-generation "
                "programme and strengthen social proof "
                "across customer touchpoints."
            ),
            owner="Marketing Director",
            priority="Medium",
        ),

        StrategyTimelineAction(
            period="Days 60-90",
            title="Competitive Optimization",
            description=(
                "Compare campaign performance against "
                "competitor gaps, reallocate budget, improve "
                "weak channels, and scale winning campaigns."
            ),
            owner="CEO Agent",
            priority="High",
        ),
    ]

    if safe_days <= 30:
        return actions[:4]

    if safe_days <= 60:
        return actions[:6]

    return actions