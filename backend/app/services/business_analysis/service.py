from __future__ import annotations

import asyncio
from collections import Counter
from typing import Any

from app.services.business_analysis.models import (
    BusinessAnalysisCompetitorSummary,
    BusinessAnalysisMarketSummary,
    BusinessAnalysisReport,
)
from app.services.business_search import search_businesses
from app.services.competitor_enrichment import (
    CompetitorEnrichmentService,
)
from app.services.competitor_intelligence import (
    CompetitorIntelligenceService,
)
from app.services.strategy_generator import (
    StrategyGeneratorService,
)
from app.services.competitor_filter import (
    CompetitorFilterService,
)


class BusinessAnalysisService:
    """
    Autonomous business-analysis orchestrator.

    This service coordinates:
    - competitor search
    - competitor enrichment
    - competitor intelligence
    - market summary
    - growth strategy generation
    """

    async def analyze(
        self,
        *,
        business_name: str,
        industry: str,
        location: str,
        objective: str,
        timeline_days: int = 90,
        monthly_budget: float = 0.0,
        currency: str = "QAR",
        average_sale_value: float = 500.0,
        competitor_limit: int = 5,
        additional_context: dict[str, Any] | None = None,
    ) -> BusinessAnalysisReport:
        errors: list[str] = []

        competitors = await self._discover_competitors(
            industry=industry,
            location=location,
            limit=competitor_limit,
            errors=errors,
        )

        enriched_competitors = await self._enrich_competitors(
            competitors,
            errors=errors,
        )

        analyzed_competitors = self._analyze_competitors(
            enriched_competitors,
            errors=errors,
        )

        competitor_summaries = (
            self._build_competitor_summaries(
                analyzed_competitors
            )
        )

        market_summary = self._build_market_summary(
            competitor_summaries
        )

        strategy_service = StrategyGeneratorService()

        strategy_report = strategy_service.generate(
            business_name=business_name,
            industry=industry,
            location=location,
            objective=objective,
            timeline_days=timeline_days,
            monthly_budget=monthly_budget,
            currency=currency,
            average_sale_value=average_sale_value,
            competitor_context=analyzed_competitors,
            additional_context=additional_context or {},
        )

        confidence = self._calculate_confidence(
            competitor_summaries
        )

        executive_summary = self._build_executive_summary(
            business_name=business_name,
            industry=industry,
            location=location,
            market_summary=market_summary,
            strategy_summary=(
                strategy_report.executive_summary
            ),
        )

        return BusinessAnalysisReport(
            business_name=business_name,
            industry=industry,
            location=location,
            objective=objective,
            timeline_days=timeline_days,
            status=(
                "completed"
                if not errors
                else "completed_with_warnings"
            ),
            competitors=competitor_summaries,
            market_summary=market_summary,
            growth_strategy=strategy_report.to_dict(),
            executive_summary=executive_summary,
            confidence=confidence,
            errors=errors,
            raw_context={
                "monthly_budget": monthly_budget,
                "currency": currency,
                "average_sale_value": average_sale_value,
                "competitor_limit": competitor_limit,
                "additional_context": (
                    additional_context or {}
                ),
            },
        )

    async def _discover_competitors(
        self,
        *,
        industry: str,
        location: str,
        limit: int,
        errors: list[str],
    ) -> list[dict[str, Any]]:
        normalized_industry = (
            str(industry or "")
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        category_mapping = {
            "medical center": "clinic",
            "medical centre": "clinic",
            "healthcare": "clinic",
            "dental clinic": "dentist",
            "coffee shop": "cafe",
            "fast food": "restaurant",
        }

        search_category = category_mapping.get(
            normalized_industry,
            normalized_industry,
        )

        safe_limit = max(
            1,
            min(
                int(limit or 5),
                10,
            ),
        )

        raw_limit = min(
            max(
                safe_limit * 3,
                10,
            ),
            30,
        )

        try:
            results = await search_businesses(
                business_type=search_category,
                location=location,
                limit=raw_limit,
            )

            print("=" * 60)
            print("SEARCH_BUSINESSES RETURNED:", len(results))
            for competitor in results[:5]:
                print(competitor.get("businessName"))
            print("=" * 60)

            filter_service = CompetitorFilterService()

            filtered_results = (
                filter_service.filter_competitors(
                    competitors=results,
                    target_industry=industry,
                    target_location=location,
                    limit=safe_limit,
                )
            )

            print("=" * 60)
            print("FILTERED RESULTS:", len(filtered_results))
            for competitor in filtered_results[:5]:
                print(competitor.get("businessName"))
            print("=" * 60)

            return filtered_results

        except Exception as exc:
            errors.append(
                f"Competitor search failed: {exc}"
            )

            return []

    async def _enrich_competitors(
        self,
        competitors: list[dict[str, Any]],
        *,
        errors: list[str],
    ) -> list[dict[str, Any]]:
        if not competitors:
            return []

        service = CompetitorEnrichmentService()

        async def enrich_one(
            competitor: dict[str, Any],
        ) -> dict[str, Any]:
            try:
                return await asyncio.wait_for(
                    service.enrich(competitor),
                    timeout=25,
                )

            except Exception as exc:
                errors.append(
                    "Competitor enrichment failed for "
                    f"{competitor.get('businessName')}: "
                    f"{exc}"
                )

                return {
                    **competitor,
                    "enrichment_status": "failed",
                    "enrichment_confidence": 0,
                }

        results = await asyncio.gather(
            *[
                enrich_one(competitor)
                for competitor in competitors
            ]
        )

        return list(results)

    def _analyze_competitors(
        self,
        competitors: list[dict[str, Any]],
        *,
        errors: list[str],
    ) -> list[dict[str, Any]]:
        if not competitors:
            return []

        service = CompetitorIntelligenceService()

        analyzed: list[dict[str, Any]] = []

        for competitor in competitors:
            enriched = dict(
                competitor
            )

            try:
                report = service.analyze(
                    enriched
                )

                enriched[
                    "competitor_intelligence"
                ] = report.to_dict()

                enriched[
                    "profileStrength"
                ] = report.strength.score

                enriched[
                    "profileStrengthLabel"
                ] = report.strength.label

                enriched[
                    "marketPosition"
                ] = report.market_position

                enriched[
                    "digitalMaturity"
                ] = report.digital_maturity

                enriched[
                    "intelligenceConfidence"
                ] = report.confidence

            except Exception as exc:
                errors.append(
                    "Competitor intelligence failed for "
                    f"{competitor.get('businessName')}: "
                    f"{exc}"
                )

            analyzed.append(
                enriched
            )

        return analyzed

    @staticmethod
    def _build_competitor_summaries(
        competitors: list[
            dict[str, Any]
        ],
    ) -> list[
        BusinessAnalysisCompetitorSummary
    ]:
        summaries = []

        for competitor in competitors:
            summaries.append(
                BusinessAnalysisCompetitorSummary(
                    name=str(
                        competitor.get(
                            "businessName"
                        )
                        or competitor.get(
                            "name"
                        )
                        or "Unknown competitor"
                    ),
                    category=competitor.get(
                        "category"
                    ),
                    location=competitor.get(
                        "location"
                    ),
                    website=competitor.get(
                        "website"
                    ),
                    phone=competitor.get(
                        "phone"
                    ),
                    email=competitor.get(
                        "email"
                    ),
                    profile_strength=int(
                        competitor.get(
                            "profileStrength",
                            0,
                        )
                        or 0
                    ),
                    profile_strength_label=(
                        competitor.get(
                            "profileStrengthLabel"
                        )
                    ),
                    market_position=(
                        competitor.get(
                            "marketPosition"
                        )
                    ),
                    digital_maturity=(
                        competitor.get(
                            "digitalMaturity"
                        )
                    ),
                    intelligence_confidence=int(
                        competitor.get(
                            "intelligenceConfidence",
                            0,
                        )
                        or 0
                    ),
                    competitor_intelligence=(
                        competitor.get(
                            "competitor_intelligence"
                        )
                        or {}
                    ),
                )
            )

        return summaries

    @staticmethod
    def _build_market_summary(
        competitors: list[
            BusinessAnalysisCompetitorSummary
        ],
    ) -> BusinessAnalysisMarketSummary:
        if not competitors:
            return BusinessAnalysisMarketSummary()

        strengths = [
            competitor.profile_strength
            for competitor in competitors
        ]

        strongest = max(
            competitors,
            key=lambda competitor:
                competitor.profile_strength,
        )

        weakest = min(
            competitors,
            key=lambda competitor:
                competitor.profile_strength,
        )

        opportunity_counter: Counter[str] = Counter()

        for competitor in competitors:
            intelligence = (
                competitor.competitor_intelligence
                or {}
            )

            for opportunity in (
                intelligence.get(
                    "opportunities"
                )
                or []
            ):
                title = str(
                    opportunity.get(
                        "title"
                    )
                    or ""
                ).strip()

                if title:
                    opportunity_counter[
                        title
                    ] += 1

        common_opportunities = [
            title
            for title, _count
            in opportunity_counter.most_common(
                5
            )
        ]

        strong_count = sum(
            1
            for score in strengths
            if score >= 70
        )

        moderate_count = sum(
            1
            for score in strengths
            if 50 <= score < 70
        )

        weak_count = sum(
            1
            for score in strengths
            if score < 50
        )

        return BusinessAnalysisMarketSummary(
            competitor_count=len(
                competitors
            ),
            average_profile_strength=round(
                sum(strengths)
                / len(strengths),
                1,
            ),
            strongest_competitor=(
                strongest.name
            ),
            weakest_competitor=(
                weakest.name
            ),
            strong_competitors=strong_count,
            moderate_competitors=(
                moderate_count
            ),
            weak_competitors=weak_count,
            common_opportunities=(
                common_opportunities
            ),
        )

    @staticmethod
    def _calculate_confidence(
        competitors: list[
            BusinessAnalysisCompetitorSummary
        ],
    ) -> int:
        if not competitors:
            return 35

        confidence_values = [
            competitor.intelligence_confidence
            for competitor in competitors
            if competitor.intelligence_confidence > 0
        ]

        if not confidence_values:
            return 45

        average = (
            sum(confidence_values)
            / len(confidence_values)
        )

        return min(
            100,
            round(
                average * 0.8 + 20
            ),
        )

    @staticmethod
    def _build_executive_summary(
        *,
        business_name: str,
        industry: str,
        location: str,
        market_summary: BusinessAnalysisMarketSummary,
        strategy_summary: str | None,
    ) -> str:
        if market_summary.competitor_count:
            market_text = (
                f"Nestora analyzed "
                f"{market_summary.competitor_count} "
                f"competitors in {location}. "
                f"The average digital strength is "
                f"{market_summary.average_profile_strength}%. "
                f"The strongest detected competitor is "
                f"{market_summary.strongest_competitor}."
            )

        else:
            market_text = (
                "Nestora could not obtain enough "
                "competitor data for a reliable "
                "market comparison."
            )

        strategy_text = (
            strategy_summary
            or (
                "A growth strategy has been generated "
                "from the available business context."
            )
        )

        return (
            f"{business_name} operates in the "
            f"{industry} market. "
            f"{market_text} "
            f"{strategy_text}"
        )