import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def build_overpass_query(business_type: str, location: str, limit: int = 20):
    return f"""
[out:json][timeout:15];
(
  node["amenity"="{business_type}"](25.15,51.35,25.45,51.65);
  way["amenity"="{business_type}"](25.15,51.35,25.45,51.65);
  node["shop"="{business_type}"](25.15,51.35,25.45,51.65);
  way["shop"="{business_type}"](25.15,51.35,25.45,51.65);
);
out center {limit};
"""


def has_value(value: str | None) -> bool:
    return bool(value and value.strip() and value != "Not found")


def calculate_contact_quality(tags: dict) -> int:
    score = 0

    if tags.get("phone"):
        score += 35
    if tags.get("website"):
        score += 35
    if tags.get("email"):
        score += 20
    if tags.get("opening_hours"):
        score += 10

    return min(score, 100)


def calculate_opportunity_score(tags: dict) -> int:
    score = 35

    if tags.get("name"):
        score += 15
    if tags.get("phone"):
        score += 15
    if tags.get("website"):
        score += 15
    if tags.get("email"):
        score += 10
    if tags.get("opening_hours"):
        score += 5
    if tags.get("addr:street") or tags.get("addr:full"):
        score += 5

    return min(score, 100)


def get_priority(score: int, contact_quality: int) -> str:
    if score >= 80 and contact_quality >= 60:
        return "High"
    if score >= 60:
        return "Medium"
    return "Low"


def get_recommendation(score: int, contact_quality: int, has_website: bool, has_phone: bool) -> str:
    if score >= 80 and has_phone:
        return "High-priority lead. Contact today and offer a starter business package."

    if has_website and not has_phone:
        return "Good digital presence, but phone is missing. Research contact details before outreach."

    if has_phone and not has_website:
        return "Good outreach target. Offer website or Google Business optimization."

    if contact_quality >= 60:
        return "Good lead. Review business fit and save to CRM."

    return "Low-information lead. Needs enrichment before outreach."


async def search_businesses(business_type: str, location: str, limit: int = 20):
    query = build_overpass_query(business_type, location, limit)

    headers = {"User-Agent": "NestoraAI/0.1 (local development)"}

    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        response = await client.post(OVERPASS_URL, data={"data": query})
        response.raise_for_status()
        data = response.json()

    results = []

    for index, item in enumerate(data.get("elements", []), start=1):
        tags = item.get("tags", {})

        phone = tags.get("phone", "Not found")
        email = tags.get("email", "Not found")
        website = tags.get("website", "Not found")

        opportunity_score = calculate_opportunity_score(tags)
        contact_quality = calculate_contact_quality(tags)
        website_available = has_value(website)
        phone_available = has_value(phone)
        priority = get_priority(opportunity_score, contact_quality)

        results.append(
            {
                "id": index,
                "businessName": tags.get("name", "Unknown Business"),
                "category": tags.get("amenity") or tags.get("shop") or business_type,
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

    return results