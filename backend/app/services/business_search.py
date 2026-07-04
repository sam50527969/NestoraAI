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


async def search_businesses(business_type: str, location: str, limit: int = 20):
    query = build_overpass_query(business_type, location, limit)

    headers = {
        "User-Agent": "NestoraAI/0.1 (local development)"
    }

    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        response = await client.post(OVERPASS_URL, data={"data": query})
        response.raise_for_status()
        data = response.json()

    results = []

    for index, item in enumerate(data.get("elements", []), start=1):
        tags = item.get("tags", {})

        results.append(
            {
                "id": index,
                "businessName": tags.get("name", "Unknown Business"),
                "category": tags.get("amenity") or tags.get("shop") or business_type,
                "location": location,
                "phone": tags.get("phone", "Not found"),
                "email": tags.get("email", "Not found"),
                "website": tags.get("website", "Not found"),
                "status": "New",
            }
        )

    return results