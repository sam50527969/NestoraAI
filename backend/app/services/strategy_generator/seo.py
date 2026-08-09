from __future__ import annotations

from typing import Any

from app.services.strategy_generator.models import (
    StrategySeoAction,
    StrategySeoPlan,
)


def build_seo_plan(
    *,
    business_name: str,
    industry: str,
    location: str,
    competitor_context: list[dict[str, Any]] | None = None,
) -> StrategySeoPlan:
    """
    Build a deterministic local SEO plan.

    Later this can be enhanced with real keyword
    volumes, ranking data, search-console data,
    and AI-generated content briefs.
    """

    safe_business_name = (
        str(business_name or "Business").strip()
    )

    safe_industry = (
        str(industry or "business")
        .strip()
        .replace("_", " ")
    )

    safe_location = (
        str(location or "Doha").strip()
    )

    keyword_base = safe_industry.lower()

    target_keywords = [
        f"{keyword_base} {safe_location}",
        f"best {keyword_base} {safe_location}",
        f"{keyword_base} near me",
        f"{keyword_base} Qatar",
        f"{safe_business_name} {safe_location}",
    ]

    actions = [
        StrategySeoAction(
            title="Optimize Local Search Presence",
            description=(
                "Improve business information consistency, "
                "local relevance, service descriptions, "
                "location signals, and trust signals."
            ),
            priority="High",
            target_keywords=target_keywords[:3],
        ),

        StrategySeoAction(
            title="Create High-Intent Service Pages",
            description=(
                "Build dedicated pages for the most valuable "
                "services instead of relying on one general "
                "services page."
            ),
            priority="High",
            target_keywords=target_keywords,
        ),

        StrategySeoAction(
            title="Improve On-Page SEO",
            description=(
                "Optimize page titles, meta descriptions, "
                "headings, internal links, image alt text, "
                "and conversion calls-to-action."
            ),
            priority="High",
            target_keywords=target_keywords[:4],
        ),

        StrategySeoAction(
            title="Build Local Authority",
            description=(
                "Strengthen local business citations, "
                "relevant directory listings, partnerships, "
                "and locally relevant backlinks."
            ),
            priority="Medium",
            target_keywords=[
                f"{keyword_base} Qatar",
                f"{keyword_base} {safe_location}",
            ],
        ),

        StrategySeoAction(
            title="Publish Educational Content",
            description=(
                "Create useful articles answering common "
                "customer questions and targeting long-tail "
                "search queries with commercial relevance."
            ),
            priority="Medium",
            target_keywords=[
                f"how to choose {keyword_base}",
                f"{keyword_base} cost Qatar",
                f"best {keyword_base} in {safe_location}",
            ],
        ),

        StrategySeoAction(
            title="Strengthen Reputation Signals",
            description=(
                "Encourage authentic customer reviews and "
                "respond consistently to strengthen trust "
                "and local search visibility."
            ),
            priority="High",
            target_keywords=[
                f"best {keyword_base} {safe_location}",
            ],
        ),
    ]

    if competitor_context:
        weak_competitors = [
            competitor
            for competitor in competitor_context
            if int(
                competitor.get(
                    "profileStrength",
                    0,
                )
                or 0
            ) < 60
        ]

        if weak_competitors:
            actions.append(
                StrategySeoAction(
                    title="Exploit Competitor Search Gaps",
                    description=(
                        "Several identified competitors have "
                        "weak digital profiles. Prioritize "
                        "local service keywords, richer "
                        "content, and stronger conversion "
                        "pages to capture this gap."
                    ),
                    priority="High",
                    target_keywords=target_keywords,
                )
            )

    return StrategySeoPlan(
        objective=(
            f"Increase organic and local-search visibility "
            f"for {safe_business_name} in {safe_location}."
        ),
        actions=actions[:7],
    )