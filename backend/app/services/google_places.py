from __future__ import annotations

import os
from typing import Any

import httpx


PLACES_TEXT_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)


def _get_api_key() -> str:
    api_key = str(
        os.getenv("GOOGLE_API_KEY")
        or ""
    ).strip()

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured."
        )

    return api_key


def _safe_text(
    value: Any,
    default: str = "Not found",
) -> str:
    cleaned = str(
        value or ""
    ).strip()

    return cleaned or default


def _extract_display_name(
    place: dict[str, Any],
) -> str:
    display_name = (
        place.get("displayName")
        or {}
    )

    return _safe_text(
        display_name.get("text"),
        "Unknown business",
    )


def _extract_location(
    place: dict[str, Any],
) -> tuple[
    float | None,
    float | None,
]:
    location = (
        place.get("location")
        or {}
    )

    return (
        location.get("latitude"),
        location.get("longitude"),
    )


def _extract_category(
    place: dict[str, Any],
    fallback: str,
) -> str:
    primary_type = str(
        place.get("primaryType")
        or ""
    ).strip()

    if primary_type:
        return primary_type.replace(
            "_",
            " ",
        )

    types = (
        place.get("types")
        or []
    )

    if types:
        return str(
            types[0]
        ).replace(
            "_",
            " ",
        )

    return fallback


def _build_result(
    *,
    place: dict[str, Any],
    business_type: str,
    index: int,
) -> dict[str, Any]:
    latitude, longitude = (
        _extract_location(place)
    )

    phone = _safe_text(
        place.get("nationalPhoneNumber")
        or place.get(
            "internationalPhoneNumber"
        )
    )

    website = _safe_text(
        place.get("websiteUri")
    )

    rating = place.get("rating")

    review_count = (
        place.get("userRatingCount")
        or 0
    )

    business_status = _safe_text(
        place.get("businessStatus"),
        "UNKNOWN",
    )

    website_available = (
        website.lower() != "not found"
    )

    phone_available = (
        phone.lower() != "not found"
    )

    contact_quality = 0

    if phone_available:
        contact_quality += 35

    if website_available:
        contact_quality += 35

    if rating is not None:
        contact_quality += 15

    if review_count:
        contact_quality += 15

    contact_quality = min(
        contact_quality,
        100,
    )

    opportunity_score = 50

    if website_available:
        opportunity_score += 15

    if phone_available:
        opportunity_score += 15

    if rating is not None:
        opportunity_score += 10

    if review_count:
        opportunity_score += 10

    opportunity_score = min(
        opportunity_score,
        100,
    )

    return {
        "id": index,
        "businessName": (
            _extract_display_name(place)
        ),
        "category": (
            _extract_category(
                place,
                business_type,
            )
        ),
        "location": _safe_text(
            place.get(
                "formattedAddress"
            ),
            "Not found",
        ),
        "phone": phone,
        "email": "Not found",
        "website": website,
        "latitude": latitude,
        "longitude": longitude,
        "source": "Google Places",
        "source_id": place.get("id"),
        "status": "New",
        "opportunityScore": (
            opportunity_score
        ),
        "contactQuality": (
            contact_quality
        ),
        "nameMatchScore": 90,
        "rankingScore": 90,
        "websiteAvailable": (
            website_available
        ),
        "phoneAvailable": (
            phone_available
        ),
        "priority": (
            "High"
            if opportunity_score >= 80
            else "Medium"
        ),
        "aiRecommendation": (
            "High-quality Google Places result. "
            "Review competitor fit and enrich further."
        ),
        "googleRating": rating,
        "googleReviewCount": (
            review_count
        ),
        "businessStatus": (
            business_status
        ),
        "googleMapsUri": place.get(
            "googleMapsUri"
        ),
        "types": (
            place.get("types")
            or []
        ),
    }


async def search_google_places(
    *,
    business_type: str,
    location: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Search Google Places API (New) using Text Search.

    Raises a readable RuntimeError containing Google's
    HTTP status and response body when the request fails.
    """

    api_key = _get_api_key()

    safe_limit = max(
        1,
        min(
            int(limit or 20),
            20,
        ),
    )

    text_query = (
        f"{business_type} in {location}"
    ).strip()

    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.primaryType,"
            "places.types,"
            "places.nationalPhoneNumber,"
            "places.internationalPhoneNumber,"
            "places.websiteUri,"
            "places.rating,"
            "places.userRatingCount,"
            "places.businessStatus,"
            "places.googleMapsUri"
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "textQuery": text_query,
        "pageSize": safe_limit,
        "languageCode": "en",
    }

    try:
        async with httpx.AsyncClient(
            timeout=25,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                PLACES_TEXT_SEARCH_URL,
                headers=headers,
                json=payload,
            )

            if response.is_error:
                response_text = (
                    response.text[:3000]
                    if response.text
                    else "<empty response body>"
                )

                raise RuntimeError(
                    "Google Places request failed. "
                    f"HTTP {response.status_code}. "
                    f"Response: {response_text}"
                )

            data = response.json()

    except httpx.TimeoutException as exc:
        raise RuntimeError(
            "Google Places request timed out."
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Google Places network request failed: "
            f"{repr(exc)}"
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Google Places returned invalid JSON."
        ) from exc

    places = (
        data.get("places")
        or []
    )

    results: list[
        dict[str, Any]
    ] = []

    for index, place in enumerate(
        places,
        start=1,
    ):
        results.append(
            _build_result(
                place=place,
                business_type=business_type,
                index=index,
            )
        )

    print(
        "[GooglePlaces] "
        f"query={text_query!r} "
        f"results={len(results)}"
    )

    return results