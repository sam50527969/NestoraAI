import httpx


OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]


INVALID_BUSINESS_NAMES = {
    "",
    "unknown",
    "unknown business",
    "unnamed business",
    "not found",
}


def normalize_business_name(name):
    return " ".join(
        str(name or "")
        .strip()
        .lower()
        .split()
    )


def is_valid_business(name):
    normalized_name = normalize_business_name(name)

    return normalized_name not in INVALID_BUSINESS_NAMES


def build_overpass_query(
    business_type: str,
    location: str,
    limit: int = 20,
):
    # Current bounding box covers Doha and nearby areas.
    # The location value is kept for the returned lead data.
    return f"""
[out:json][timeout:15];
(
  node["amenity"="{business_type}"](25.15,51.35,25.45,51.65);
  way["amenity"="{business_type}"](25.15,51.35,25.45,51.65);
  relation["amenity"="{business_type}"](25.15,51.35,25.45,51.65);

  node["shop"="{business_type}"](25.15,51.35,25.45,51.65);
  way["shop"="{business_type}"](25.15,51.35,25.45,51.65);
  relation["shop"="{business_type}"](25.15,51.35,25.45,51.65);
);
out center {limit};
"""


def has_value(value: str | None) -> bool:
    if value is None:
        return False

    cleaned_value = value.strip()

    return bool(
        cleaned_value
        and cleaned_value.lower() != "not found"
    )


def calculate_contact_quality(tags: dict) -> int:
    score = 0

    if tags.get("phone") or tags.get("contact:phone"):
        score += 35

    if tags.get("website") or tags.get("contact:website"):
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

    if tags.get("website") or tags.get("contact:website"):
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


async def search_businesses(
    business_type: str,
    location: str,
    limit: int = 20,
):
    safe_limit = max(1, min(int(limit), 100))

    query = build_overpass_query(
        business_type=business_type,
        location=location,
        limit=safe_limit * 3,
    )

    headers = {
        "User-Agent": "NestoraAI/0.1 (local development)"
    }

    data = None
    last_error = None

    async with httpx.AsyncClient(
        timeout=30,
        headers=headers,
    ) as client:
        for overpass_url in OVERPASS_URLS:
            try:
                response = await client.post(
                    overpass_url,
                    data={"data": query},
                )

                response.raise_for_status()
                data = response.json()
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

    if data is None:
        raise RuntimeError(
            "All Overpass servers failed. "
            f"Last error: {last_error}"
        )

    results = []
    seen_names = set()

    for item in data.get("elements", []):
        tags = item.get("tags", {})

        business_name = tags.get("name")

        if not is_valid_business(business_name):
            continue

        normalized_name = normalize_business_name(
            business_name
        )

        if normalized_name in seen_names:
            continue

        seen_names.add(normalized_name)

        phone = get_phone(tags)
        email = get_email(tags)
        website = get_website(tags)

        opportunity_score = calculate_opportunity_score(
            tags
        )

        contact_quality = calculate_contact_quality(
            tags
        )

        website_available = has_value(website)
        phone_available = has_value(phone)

        priority = get_priority(
            opportunity_score,
            contact_quality,
        )

        results.append(
            {
                "id": len(results) + 1,
                "businessName": str(
                    business_name
                ).strip(),
                "category": (
                    tags.get("amenity")
                    or tags.get("shop")
                    or business_type
                ),
                "location": location,
                "phone": phone,
                "email": email,
                "website": website,
                "status": "New",
                "opportunityScore": opportunity_score,
                "contactQuality": contact_quality,
                "websiteAvailable": website_available,
                "phoneAvailable": phone_available,
                "priority": priority,
                "aiRecommendation": get_recommendation(
                    opportunity_score,
                    contact_quality,
                    website_available,
                    phone_available,
                ),
            }
        )

        if len(results) >= safe_limit:
            break

    return results