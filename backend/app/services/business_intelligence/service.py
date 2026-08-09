from __future__ import annotations

from typing import Any

from app.services.business_intelligence.google_provider import (
    GoogleBusinessProvider,
)
from app.services.business_intelligence.models import (
    BusinessIntelligenceProfile,
)


class BusinessIntelligenceService:
    """
    Unified business intelligence service.

    It queries available providers and returns the
    strongest normalized business profile.
    """

    def __init__(
        self,
        google_provider: GoogleBusinessProvider | None = None,
    ) -> None:
        self.google_provider = (
            google_provider
            or GoogleBusinessProvider()
        )

    async def get_business_profile(
        self,
        *,
        business_name: str,
        location: str,
    ) -> BusinessIntelligenceProfile | None:
        """
        Retrieve the best available intelligence profile
        for one business.
        """

        profiles: list[
            BusinessIntelligenceProfile
        ] = []

        google_profile = (
            await self.google_provider.search_business(
                business_name=business_name,
                location=location,
            )
        )

        if google_profile is not None:
            profiles.append(
                google_profile
            )

        if not profiles:
            return None

        return max(
            profiles,
            key=lambda profile:
                profile.source_confidence,
        )

    async def enrich_record(
        self,
        business: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge provider intelligence into an existing
        competitor or CRM business record.
        """

        business_name = str(
            business.get("businessName")
            or business.get("business_name")
            or business.get("name")
            or ""
        ).strip()

        location = str(
            business.get("location")
            or business.get("address")
            or "Doha, Qatar"
        ).strip()

        if not business_name:
            return {
                **business,
                "business_intelligence_status":
                    "skipped",
            }

        profile = await self.get_business_profile(
            business_name=business_name,
            location=location,
        )

        if profile is None:
            return {
                **business,
                "business_intelligence_status":
                    "not_found",
            }

        profile_data = profile.to_dict()

        contact = profile_data.get(
            "contact"
        ) or {}

        reputation = profile_data.get(
            "reputation"
        ) or {}

        opening_hours = profile_data.get(
            "opening_hours"
        ) or {}

        enriched = {
            **business,

            "phone": (
                contact.get("phone")
                or business.get("phone")
                or "Not found"
            ),

            "email": (
                contact.get("email")
                or business.get("email")
                or "Not found"
            ),

            "website": (
                contact.get("website")
                or business.get("website")
                or "Not found"
            ),

            "rating": reputation.get(
                "rating"
            ),

            "review_count": reputation.get(
                "review_count"
            ),

            "opening_hours": opening_hours.get(
                "weekday_text"
            ),

            "open_now": opening_hours.get(
                "open_now"
            ),

            "business_status": profile_data.get(
                "business_status"
            ),

            "provider_id": profile_data.get(
                "provider_id"
            ),

            "business_intelligence_provider":
                profile_data.get("provider"),

            "business_intelligence_confidence":
                profile_data.get(
                    "source_confidence",
                    0,
                ),

            "business_intelligence_status":
                "completed",
        }

        return enriched