from __future__ import annotations
from app.services.google_places import (
    search_google_places,
)

import re
from typing import Any

import httpx


OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

INVALID_BUSINESS_NAMES = {
    "",
    "unknown",
    "unknown business",
    "unnamed business",
    "not found",
}

CATEGORY_ALIASES = {
    "clinic": {
        "amenity": ["clinic", "doctors"],
        "healthcare": [
            "clinic",
            "doctor",
            "centre",
            "center",
        ],
    },
    "medical center": {
        "amenity": ["clinic", "doctors", "hospital"],
        "healthcare": [
            "clinic",
            "doctor",
            "hospital",
            "centre",
            "center",
        ],
    },
    "medical centre": {
        "amenity": ["clinic", "doctors", "hospital"],
        "healthcare": [
            "clinic",
            "doctor",
            "hospital",
            "centre",
            "center",
        ],
    },
    "dentist": {
        "amenity": ["dentist", "clinic"],
        "healthcare": ["dentist", "clinic"],
    },
    "dental clinic": {
        "amenity": ["dentist", "clinic"],
        "healthcare": ["dentist", "clinic"],
    },
    "hospital": {
        "amenity": ["hospital"],
        "healthcare": ["hospital"],
    },
    "pharmacy": {
        "amenity": ["pharmacy"],
        "healthcare": ["pharmacy"],
        "shop": ["chemist"],
    },
    "restaurant": {
        "amenity": ["restaurant", "fast_food", "cafe"],
    },
    "cafe": {
        "amenity": ["cafe"],
    },
    "gym": {
        "leisure": ["fitness_centre", "sports_centre"],
        "sport": ["fitness"],
    },
    "salon": {
        "shop": ["hairdresser", "beauty"],
    },
}

# Temporary verified fallback records for important Qatar businesses that
# may be missing or inconsistently tagged in OpenStreetMap.
VERIFIED_QATAR_BUSINESSES = [
    {
        "businessName": "Reem Medical Center",
        "aliases": [
            "Reem Medical Centre",
            "Reem Medical Center Doha",
        ],
        "category": "medical_center",
        "location": (
            "Gold Souq, near Karwa Bus Station, "
            "Old Al Ghanem, Doha, Qatar"
        ),
        "phone": "+974 3331 8112",
        "email": "inquiry@reemmedicalcenter.com",
        "website": "https://reemmedicalcenter.com",
        "latitude": None,
        "longitude": None,
        "source": "verified_qatar_directory",
    },
]


def normalize_business_name(name: Any) -> str:
    return " ".join(
        str(name or "")
        .strip()
        .lower()
        .replace("&", "and")
        .split()
    )


def is_valid_business(name: Any) -> bool:
    normalized_name = normalize_business_name(name)

    return normalized_name not in INVALID_BUSINESS_NAMES


def has_value(value: str | None) -> bool:
    if value is None:
        return False

    cleaned_value = value.strip()

    return bool(
        cleaned_value
        and cleaned_value.lower() != "not found"
    )


def _escape_overpass_regex(value: str) -> str:
    escaped = re.escape(value.strip())
    escaped = escaped.replace(r"\ ", r"\s+")

    return escaped.replace('"', r"\"")


def _build_name_variants(search_text: str) -> list[str]:
    cleaned = " ".join(search_text.strip().split())

    if not cleaned:
        return []

    variants = {cleaned}

    lower_value = cleaned.lower()

    if "centre" in lower_value:
        variants.add(
            re.sub(
                "centre",
                "center",
                cleaned,
                flags=re.IGNORECASE,
            )
        )

    if "center" in lower_value:
        variants.add(
            re.sub(
                "center",
                "centre",
                cleaned,
                flags=re.IGNORECASE,
            )
        )

    return sorted(variants)


def _build_name_filters(search_text: str) -> str:
    variants = _build_name_variants(search_text)

    if not variants:
        return ""

    pattern = "|".join(
        _escape_overpass_regex(variant)
        for variant in variants
    )

    tag_names = [
        "name",
        "official_name",
        "alt_name",
        "short_name",
        "brand",
        "operator",
    ]

    lines = []

    for tag_name in tag_names:
        lines.append(
            f'nwr["{tag_name}"~"{pattern}",i]'
            "(area.searchArea);"
        )

    return "\n  ".join(lines)


def _get_category_filters(
    business_type: str,
) -> dict[str, list[str]]:
    normalized = normalize_business_name(
        business_type
    )

    if normalized in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[normalized]

    return {
        "amenity": [normalized],
        "shop": [normalized],
        "healthcare": [normalized],
        "office": [normalized],
        "leisure": [normalized],
    }


def _build_category_filters(
    business_type: str,
) -> str:
    category_filters = _get_category_filters(
        business_type
    )

    lines = []

    for tag_name, values in category_filters.items():
        for value in values:
            if not value:
                continue

            safe_value = _escape_overpass_regex(
                value
            )

            lines.append(
                f'nwr["{tag_name}"="{safe_value}"]'
                "(area.searchArea);"
            )

    return "\n  ".join(lines)


def build_overpass_query(
    business_type: str,
    location: str,
    limit: int = 20,
) -> str:
    del location

    name_filters = _build_name_filters(
        business_type
    )

    category_filters = _build_category_filters(
        business_type
    )

    return f"""
[out:json][timeout:35];
area["ISO3166-1"="QA"][admin_level=2]->.searchArea;
(
  {name_filters}
  {category_filters}
);
out center tags {limit};
"""


def calculate_contact_quality(tags: dict) -> int:
    score = 0

    if tags.get("phone") or tags.get("contact:phone"):
        score += 35

    if (
        tags.get("website")
        or tags.get("contact:website")
    ):
        score += 35

    if tags.get("email") or tags.get("contact:email"):
        score += 20

    if tags.get("opening_hours"):
        score += 10

    return min(score, 100)


def calculate_opportunity_score(tags: dict) -> int:
    score = 35

    if tags.get("name"):
        score += 15

    if tags.get("phone") or tags.get("contact:phone"):
        score += 15

    if (
        tags.get("website")
        or tags.get("contact:website")
    ):
        score += 15

    if tags.get("email") or tags.get("contact:email"):
        score += 10

    if tags.get("opening_hours"):
        score += 5

    if tags.get("addr:street") or tags.get("addr:full"):
        score += 5

    return min(score, 100)


def get_priority(
    score: int,
    contact_quality: int,
) -> str:
    if score >= 80 and contact_quality >= 60:
        return "High"

    if score >= 60:
        return "Medium"

    return "Low"


def get_recommendation(
    score: int,
    contact_quality: int,
    has_website: bool,
    has_phone: bool,
) -> str:
    if score >= 80 and has_phone:
        return (
            "High-priority lead. Contact today and offer "
            "a starter business package."
        )

    if has_website and not has_phone:
        return (
            "Good digital presence, but phone is missing. "
            "Research contact details before outreach."
        )

    if has_phone and not has_website:
        return (
            "Good outreach target. Offer website or "
            "Google Business optimization."
        )

    if contact_quality >= 60:
        return (
            "Good lead. Review business fit and save to CRM."
        )

    return (
        "Low-information lead. Needs enrichment before outreach."
    )


def get_phone(tags: dict) -> str:
    return (
        tags.get("phone")
        or tags.get("contact:phone")
        or "Not found"
    )


def get_email(tags: dict) -> str:
    return (
        tags.get("email")
        or tags.get("contact:email")
        or "Not found"
    )


def get_website(tags: dict) -> str:
    return (
        tags.get("website")
        or tags.get("contact:website")
        or "Not found"
    )


def get_address(
    tags: dict,
    fallback_location: str,
) -> str:
    full_address = tags.get("addr:full")

    if full_address:
        return str(full_address).strip()

    address_parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
    ]

    cleaned_parts = [
        str(part).strip()
        for part in address_parts
        if part and str(part).strip()
    ]

    if cleaned_parts:
        return ", ".join(cleaned_parts)

    return fallback_location


def get_category(
    tags: dict,
    fallback: str,
) -> str:
    return str(
        tags.get("healthcare")
        or tags.get("amenity")
        or tags.get("shop")
        or tags.get("office")
        or tags.get("leisure")
        or fallback
    )


def get_coordinates(
    item: dict,
) -> tuple[float | None, float | None]:
    latitude = item.get("lat")
    longitude = item.get("lon")

    center = item.get("center") or {}

    if latitude is None:
        latitude = center.get("lat")

    if longitude is None:
        longitude = center.get("lon")

    return latitude, longitude


def calculate_name_match_score(
    business_name: str,
    search_text: str,
) -> int:
    normalized_name = normalize_business_name(
        business_name
    )

    normalized_search = normalize_business_name(
        search_text
    )

    if not normalized_name or not normalized_search:
        return 0

    if normalized_name == normalized_search:
        return 100

    search_variants = {
        normalized_search,
        normalized_search.replace(
            "centre",
            "center",
        ),
        normalized_search.replace(
            "center",
            "centre",
        ),
    }

    name_variants = {
        normalized_name,
        normalized_name.replace(
            "centre",
            "center",
        ),
        normalized_name.replace(
            "center",
            "centre",
        ),
    }

    if search_variants & name_variants:
        return 98

    if any(
        variant in normalized_name
        for variant in search_variants
    ):
        return 85

    search_tokens = set(
        normalized_search.split()
    )

    name_tokens = set(
        normalized_name.split()
    )

    if not search_tokens:
        return 0

    overlap = len(
        search_tokens & name_tokens
    )

    return round(
        (overlap / len(search_tokens)) * 70
    )


def _create_result(
    *,
    business_name: str,
    category: str,
    location: str,
    phone: str,
    email: str,
    website: str,
    latitude: float | None,
    longitude: float | None,
    source: str,
    search_text: str,
    tags: dict | None = None,
) -> dict:
    safe_tags = tags or {}

    opportunity_score = (
        calculate_opportunity_score(
            safe_tags
        )
        if safe_tags
        else 90
    )

    contact_quality = (
        calculate_contact_quality(
            safe_tags
        )
        if safe_tags
        else 90
    )

    website_available = has_value(website)
    phone_available = has_value(phone)

    name_match_score = calculate_name_match_score(
        business_name,
        search_text,
    )

    ranking_score = min(
        100,
        round(
            (
                name_match_score * 0.65
                + opportunity_score * 0.2
                + contact_quality * 0.15
            )
        ),
    )

    return {
        "id": 0,
        "businessName": business_name.strip(),
        "category": category,
        "location": location,
        "phone": phone,
        "email": email,
        "website": website,
        "latitude": latitude,
        "longitude": longitude,
        "source": source,
        "status": "New",
        "opportunityScore": opportunity_score,
        "contactQuality": contact_quality,
        "nameMatchScore": name_match_score,
        "rankingScore": ranking_score,
        "websiteAvailable": website_available,
        "phoneAvailable": phone_available,
        "priority": get_priority(
            opportunity_score,
            contact_quality,
        ),
        "aiRecommendation": get_recommendation(
            opportunity_score,
            contact_quality,
            website_available,
            phone_available,
        ),
    }


def _parse_overpass_results(
    data: dict,
    *,
    business_type: str,
    location: str,
) -> list[dict]:
    results = []

    for item in data.get("elements", []):
        tags = item.get("tags", {})

        business_name = (
            tags.get("name")
            or tags.get("official_name")
            or tags.get("brand")
            or tags.get("operator")
        )

        if not is_valid_business(
            business_name
        ):
            continue

        latitude, longitude = get_coordinates(
            item
        )

        results.append(
            _create_result(
                business_name=str(
                    business_name
                ).strip(),
                category=get_category(
                    tags,
                    business_type,
                ),
                location=get_address(
                    tags,
                    location,
                ),
                phone=get_phone(tags),
                email=get_email(tags),
                website=get_website(tags),
                latitude=latitude,
                longitude=longitude,
                source="OpenStreetMap",
                search_text=business_type,
                tags=tags,
            )
        )

    return results


async def _search_nominatim(
    client: httpx.AsyncClient,
    *,
    search_text: str,
    location: str,
    limit: int,
) -> list[dict]:
    query_text = " ".join(
        part
        for part in [
            search_text.strip(),
            location.strip(),
        ]
        if part
    )

    response = await client.get(
        NOMINATIM_URL,
        params={
            "q": query_text,
            "format": "jsonv2",
            "addressdetails": 1,
            "namedetails": 1,
            "limit": min(limit, 20),
        },
    )

    response.raise_for_status()

    payload = response.json()

    results = []

    for item in payload:
        namedetails = (
            item.get("namedetails")
            or {}
        )

        business_name = (
            namedetails.get("name")
            or item.get("name")
            or str(
                item.get("display_name")
                or ""
            ).split(",")[0]
        )

        if not is_valid_business(
            business_name
        ):
            continue

        category = (
            item.get("type")
            or item.get("category")
            or "business"
        )

        results.append(
            _create_result(
                business_name=str(
                    business_name
                ).strip(),
                category=str(category),
                location=str(
                    item.get("display_name")
                    or location
                ),
                phone="Not found",
                email="Not found",
                website="Not found",
                latitude=_safe_float(
                    item.get("lat")
                ),
                longitude=_safe_float(
                    item.get("lon")
                ),
                source="OpenStreetMap Nominatim",
                search_text=search_text,
            )
        )

    return results


def _safe_float(
    value: Any,
) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_qatar_location(location: str) -> bool:
    normalized_location = normalize_business_name(
        location
    )

    qatar_terms = {
        "qatar",
        "doha",
        "al rayyan",
        "al wakrah",
        "lusail",
    }

    return any(
        term in normalized_location
        for term in qatar_terms
    )


def _get_verified_matches(
    search_text: str,
    location: str,
) -> list[dict]:
    if not _is_qatar_location(location):
        return []

    normalized_search = normalize_business_name(
        search_text
    )

    matches = []

    for business in VERIFIED_QATAR_BUSINESSES:
        searchable_names = [
            business["businessName"],
            *business.get("aliases", []),
        ]

        best_match = max(
            calculate_name_match_score(
                candidate,
                normalized_search,
            )
            for candidate in searchable_names
        )

        if best_match < 55:
            continue

        result = _create_result(
            business_name=business[
                "businessName"
            ],
            category=business["category"],
            location=business["location"],
            phone=business["phone"],
            email=business["email"],
            website=business["website"],
            latitude=business.get("latitude"),
            longitude=business.get("longitude"),
            source=business["source"],
            search_text=search_text,
        )

        result["nameMatchScore"] = best_match
        result["rankingScore"] = max(
            result["rankingScore"],
            best_match,
        )

        matches.append(result)

    return matches


def _deduplicate_and_rank(
    results: list[dict],
    *,
    limit: int,
) -> list[dict]:
    deduplicated: dict[str, dict] = {}

    for result in results:
        normalized_name = normalize_business_name(
            result.get("businessName")
        )

        phone = normalize_business_name(
            result.get("phone")
        )

        dedupe_key = (
            f"{normalized_name}|{phone}"
            if has_value(
                result.get("phone")
            )
            else normalized_name
        )

        existing = deduplicated.get(
            dedupe_key
        )

        if (
            existing is None
            or result.get(
                "rankingScore",
                0,
            )
            > existing.get(
                "rankingScore",
                0,
            )
        ):
            deduplicated[dedupe_key] = result

    ranked_results = sorted(
        deduplicated.values(),
        key=lambda result: (
            result.get("rankingScore", 0),
            result.get("contactQuality", 0),
            result.get(
                "opportunityScore",
                0,
            ),
        ),
        reverse=True,
    )

    final_results = ranked_results[:limit]

    for index, result in enumerate(
        final_results,
        start=1,
    ):
        result["id"] = index

    return final_results


async def search_businesses(
    business_type: str,
    location: str,
    limit: int = 20,
) -> list[dict]:
    search_text = " ".join(
        str(business_type or "")
        .strip()
        .split()
    )

    if not search_text:
        return []

    safe_limit = max(
        1,
        min(int(limit), 100),
    )

    query = build_overpass_query(
        business_type=search_text,
        location=location,
        limit=min(
            safe_limit * 8,
            800,
        ),
    )

    headers = {
        "User-Agent": (
            "NestoraAI/0.7 "
            "(business-search; local development)"
        )
    }

    all_results = _get_verified_matches(
        search_text,
        location,
    )

    try:
        google_results = await search_google_places(
            business_type=search_text,
            location=location,
            limit=safe_limit,
        )

        all_results.extend(
            google_results
        )

        if len(all_results) >= safe_limit:
            return _deduplicate_and_rank(
                all_results,
                limit=safe_limit,
            )

    except Exception as error:
        print(
            "Google Places search failed: "
            f"{error}"
        )

    overpass_data = None
    last_error = None

    async with httpx.AsyncClient(
        timeout=40,
        headers=headers,
        follow_redirects=True,
    ) as client:
        for overpass_url in OVERPASS_URLS:
            try:
                response = await client.post(
                    overpass_url,
                    data={"data": query},
                )

                response.raise_for_status()
                overpass_data = response.json()
                break

            except (
                httpx.HTTPError,
                ValueError,
            ) as error:
                last_error = error

                print(
                    "Overpass server failed: "
                    f"{overpass_url} | {error}"
                )

        if overpass_data is not None:
            all_results.extend(
                _parse_overpass_results(
                    overpass_data,
                    business_type=search_text,
                    location=location,
                )
            )

        try:
            all_results.extend(
                await _search_nominatim(
                    client,
                    search_text=search_text,
                    location=location,
                    limit=safe_limit,
                )
            )

        except (
            httpx.HTTPError,
            ValueError,
        ) as error:
            print(
                "Nominatim search failed: "
                f"{error}"
            )

    if (
        not all_results
        and overpass_data is None
        and last_error is not None
    ):
        raise RuntimeError(
            "All business search providers failed. "
            f"Last error: {last_error}"
        )

    return _deduplicate_and_rank(
        all_results,
        limit=safe_limit,
    )