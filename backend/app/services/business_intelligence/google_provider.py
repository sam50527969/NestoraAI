from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.services.business_intelligence.models import (
    BusinessContact,
    BusinessIntelligenceProfile,
    BusinessLocation,
    BusinessOpeningHours,
    BusinessReputation,
)


GOOGLE_PLACES_TEXT_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)


class GoogleBusinessProvider:
    """
    Google Places provider for business intelligence.

    This provider uses the official Google Places API
    and returns Nestora's normalized business profile.
    """

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        self.api_key = (
            api_key
            or getattr(
                settings,
                "google_places_api_key",
                None,
            )
        )

    @property
    def is_configured(self) -> bool:
        return bool(
            self.api_key
            and str(self.api_key).strip()
        )

    async def search_business(
        self,
        *,
        business_name: str,
        location: str,
    ) -> BusinessIntelligenceProfile | None:
        """
        Search Google Places for one business and
        return the strongest matching result.
        """

        if not self.is_configured:
            return None

        query = " ".join(
            part.strip()
            for part in [
                business_name,
                location,
            ]
            if part and part.strip()
        )

        headers = {
            "X-Goog-Api-Key": str(
                self.api_key
            ),
            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress,"
                "places.location,"
                "places.nationalPhoneNumber,"
                "places.internationalPhoneNumber,"
                "places.websiteUri,"
                "places.rating,"
                "places.userRatingCount,"
                "places.businessStatus,"
                "places.types,"
                "places.regularOpeningHours"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "textQuery": query,
            "languageCode": "en",
            "regionCode": "QA",
            "maxResultCount": 5,
        }

        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    GOOGLE_PLACES_TEXT_SEARCH_URL,
                    headers=headers,
                    json=payload,
                )

                response.raise_for_status()
                data = response.json()

        except (
            httpx.HTTPError,
            ValueError,
        ) as exc:
            print(
                "Google Places search failed: "
                f"{business_name} | {exc}"
            )

            return None

        places = data.get("places") or []

        if not places:
            return None

        best_match = self._select_best_match(
            business_name=business_name,
            places=places,
        )

        if best_match is None:
            return None

        return self._normalize_place(
            best_match
        )

    @staticmethod
    def _normalize_name(
        value: Any,
    ) -> str:
        return " ".join(
            str(value or "")
            .strip()
            .lower()
            .replace("&", "and")
            .split()
        )

    def _select_best_match(
        self,
        *,
        business_name: str,
        places: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        target_name = self._normalize_name(
            business_name
        )

        best_place = None
        best_score = -1

        for place in places:
            display_name = (
                place.get("displayName")
                or {}
            ).get("text")

            candidate_name = self._normalize_name(
                display_name
            )

            score = 0

            if candidate_name == target_name:
                score = 100

            elif (
                target_name
                and target_name in candidate_name
            ):
                score = 85

            elif (
                candidate_name
                and candidate_name in target_name
            ):
                score = 80

            else:
                target_tokens = set(
                    target_name.split()
                )

                candidate_tokens = set(
                    candidate_name.split()
                )

                if target_tokens:
                    overlap = len(
                        target_tokens
                        & candidate_tokens
                    )

                    score = round(
                        (
                            overlap
                            / len(target_tokens)
                        )
                        * 70
                    )

            if score > best_score:
                best_score = score
                best_place = place

        if best_score < 40:
            return None

        return best_place

    @staticmethod
    def _normalize_place(
        place: dict[str, Any],
    ) -> BusinessIntelligenceProfile:
        display_name = (
            place.get("displayName")
            or {}
        ).get("text") or "Unknown business"

        location_data = place.get(
            "location"
        ) or {}

        opening_hours_data = (
            place.get(
                "regularOpeningHours"
            )
            or {}
        )

        phone = (
            place.get(
                "internationalPhoneNumber"
            )
            or place.get(
                "nationalPhoneNumber"
            )
        )

        types = [
            str(value)
            for value in (
                place.get("types")
                or []
            )
        ]

        return BusinessIntelligenceProfile(
            name=str(display_name),
            provider="google_places",
            provider_id=place.get("id"),
            category=(
                types[0]
                if types
                else None
            ),
            contact=BusinessContact(
                phone=phone,
                website=place.get(
                    "websiteUri"
                ),
            ),
            location=BusinessLocation(
                address=place.get(
                    "formattedAddress"
                ),
                city="Doha",
                country="Qatar",
                latitude=location_data.get(
                    "latitude"
                ),
                longitude=location_data.get(
                    "longitude"
                ),
            ),
            reputation=BusinessReputation(
                rating=place.get("rating"),
                review_count=place.get(
                    "userRatingCount"
                ),
            ),
            opening_hours=BusinessOpeningHours(
                open_now=opening_hours_data.get(
                    "openNow"
                ),
                weekday_text=list(
                    opening_hours_data.get(
                        "weekdayDescriptions"
                    )
                    or []
                ),
            ),
            business_status=place.get(
                "businessStatus"
            ),
            categories=types,
            source_confidence=95,
            raw_data=place,
        )