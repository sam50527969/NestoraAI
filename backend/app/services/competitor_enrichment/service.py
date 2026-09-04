from __future__ import annotations

import asyncio
from typing import Any

from app.services.competitor_enrichment.email_discovery import (
    discover_email,
)
from app.services.competitor_enrichment.phone_discovery import (
    discover_phone,
)
from app.services.competitor_enrichment.social_discovery import (
    discover_social_profiles,
)
from app.services.competitor_enrichment.website_discovery import (
    discover_website,
)
from app.services.website_intelligence import (
    WebsiteIntelligenceService,
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


def _first_value(
    values: list[Any] | None,
) -> str | None:
    for value in values or []:
        if _has_value(value):
            return str(value).strip()

    return None


class CompetitorEnrichmentService:
    """
    Enrich competitor records with public business
    information.

    The service verifies existing websites, analyzes
    available websites once, and extracts contact,
    social, SEO, and website intelligence signals.
    """

    def __init__(
        self,
        website_intelligence_service:
            WebsiteIntelligenceService | None = None,
    ) -> None:
        self.website_intelligence_service = (
            website_intelligence_service
            or WebsiteIntelligenceService()
        )

    async def enrich(
        self,
        competitor: dict[str, Any],
    ) -> dict[str, Any]:
        enriched = dict(competitor)

        business_name = self._get_business_name(
            competitor,
        )

        location = str(
            competitor.get("location")
            or competitor.get("address")
            or ""
        ).strip()

        category = str(
            competitor.get("category")
            or competitor.get("industry")
            or "business"
        ).strip()

        website_result = await discover_website(
            business_name=business_name,
            location=location,
            current_website=competitor.get(
                "website"
            ),
        )

        website = website_result.get(
            "website"
        )

        website_profile: dict[str, Any] = {}

        if _has_value(website):
            profile = (
                await self.website_intelligence_service
                .analyze(
                    website=str(website),
                    business_name=business_name,
                )
            )

            website_profile = profile.to_dict()

        contact_data = (
            website_profile.get("contact")
            or {}
        )

        social_data = (
            website_profile.get(
                "social_profiles"
            )
            or {}
        )

        seo_data = (
            website_profile.get("seo")
            or {}
        )

        pages_data = (
            website_profile.get("pages")
            or {}
        )

        extracted_phone = _first_value(
            contact_data.get("phones")
        )

        extracted_email = _first_value(
            contact_data.get("emails")
        )

        if extracted_phone:
            phone_result = {
                "phone": extracted_phone,
                "confidence": 90,
                "source": "website_intelligence",
                "status": "discovered",
            }
        else:
            phone_result = await discover_phone(
                business_name=business_name,
                location=location,
                website=website,
                current_phone=competitor.get(
                    "phone"
                ),
            )

        if extracted_email:
            email_result = {
                "email": extracted_email,
                "confidence": 90,
                "source": "website_intelligence",
                "status": "discovered",
            }
        else:
            email_result = await discover_email(
                business_name=business_name,
                website=website,
                current_email=competitor.get(
                    "email"
                ),
            )

        if any(
            _has_value(value)
            for value in social_data.values()
        ):
            social_result = {
                "facebook": social_data.get(
                    "facebook"
                ),
                "instagram": social_data.get(
                    "instagram"
                ),
                "linkedin": social_data.get(
                    "linkedin"
                ),
                "tiktok": social_data.get(
                    "tiktok"
                ),
                "x": social_data.get("x"),
                "youtube": social_data.get(
                    "youtube"
                ),
                "confidence": 90,
                "source": "website_intelligence",
                "status": "discovered",
            }
        else:
            social_result = (
                await discover_social_profiles(
                    business_name=business_name,
                    location=location,
                    website=website,
                )
            )

        website_intelligence_confidence = int(
            website_profile.get(
                "confidence",
                0,
            )
            or 0
        )

        enriched.update(
            {
                "website": (
                    website
                    if _has_value(website)
                    else "Not found"
                ),

                "phone": (
                    phone_result.get("phone")
                    or "Not found"
                ),

                "email": (
                    email_result.get("email")
                    or "Not found"
                ),

                "facebook": social_result.get(
                    "facebook"
                ),

                "instagram": social_result.get(
                    "instagram"
                ),

                "linkedin": social_result.get(
                    "linkedin"
                ),

                "tiktok": social_result.get(
                    "tiktok"
                ),

                "x": social_result.get("x"),

                "youtube": social_result.get(
                    "youtube"
                ),

                "website_title": seo_data.get(
                    "title"
                ),

                "meta_description": seo_data.get(
                    "meta_description"
                ),

                "contact_page": pages_data.get(
                    "contact"
                ),

                "booking_page": pages_data.get(
                    "booking"
                ),

                "website_status": (
                    website_profile.get("status")
                    if website_profile
                    else "not_analyzed"
                ),

                "website_status_code": (
                    website_profile.get(
                        "status_code"
                    )
                ),

                "website_response_time_ms": (
                    website_profile.get(
                        "response_time_ms"
                    )
                ),

                "website_is_https": (
                    website_profile.get(
                        "is_https"
                    )
                ),

                "website_intelligence_confidence":
                    website_intelligence_confidence,

                "website_intelligence": (
                    website_profile
                    if website_profile
                    else None
                ),

                "enrichment_confidence": (
                    self._calculate_confidence(
                        website_result=website_result,
                        phone_result=phone_result,
                        email_result=email_result,
                        social_result=social_result,
                        website_intelligence_confidence=(
                            website_intelligence_confidence
                        ),
                    )
                ),

                "enrichment_sources": (
                    self._collect_sources(
                        website_result,
                        phone_result,
                        email_result,
                        social_result,
                    )
                ),

                "enrichment_status": "completed",
                "category": category,
            }
        )

        if (
            website_profile
            and "website_intelligence"
            not in enriched[
                "enrichment_sources"
            ]
        ):
            enriched[
                "enrichment_sources"
            ].append(
                "website_intelligence"
            )

        return enriched

    async def enrich_many(
        self,
        competitors: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Enrich competitors concurrently so one slow
        website does not force sequential processing.
        """

        if not competitors:
            return []

        results = await asyncio.gather(
            *[
                self.enrich(competitor)
                for competitor in competitors
            ],
            return_exceptions=True,
        )

        enriched_results: list[
            dict[str, Any]
        ] = []

        for competitor, result in zip(
            competitors,
            results,
        ):
            if isinstance(
                result,
                BaseException,
            ):
                enriched_results.append(
                    {
                        **competitor,
                        "enrichment_status":
                            "failed",
                        "enrichment_confidence":
                            0,
                        "enrichment_sources":
                            [],
                        "enrichment_error":
                            str(result),
                    }
                )

                continue

            enriched_results.append(result)

        return enriched_results

    @staticmethod
    def _get_business_name(
        competitor: dict[str, Any],
    ) -> str:
        return str(
            competitor.get("businessName")
            or competitor.get(
                "business_name"
            )
            or competitor.get("name")
            or "Unknown business"
        ).strip()

    @staticmethod
    def _calculate_confidence(
        *,
        website_result: dict[str, Any],
        phone_result: dict[str, Any],
        email_result: dict[str, Any],
        social_result: dict[str, Any],
        website_intelligence_confidence: int,
    ) -> int:
        scores = [
            int(
                website_result.get(
                    "confidence",
                    0,
                )
                or 0
            ),
            int(
                phone_result.get(
                    "confidence",
                    0,
                )
                or 0
            ),
            int(
                email_result.get(
                    "confidence",
                    0,
                )
                or 0
            ),
            int(
                social_result.get(
                    "confidence",
                    0,
                )
                or 0
            ),
            int(
                website_intelligence_confidence
                or 0
            ),
        ]

        valid_scores = [
            score
            for score in scores
            if score > 0
        ]

        if not valid_scores:
            return 0

        return round(
            sum(valid_scores)
            / len(valid_scores)
        )

    @staticmethod
    def _collect_sources(
        *results: dict[str, Any],
    ) -> list[str]:
        sources: list[str] = []

        for result in results:
            source = result.get(
                "source"
            )

            if (
                source
                and source not in sources
            ):
                sources.append(
                    str(source)
                )

        return sources