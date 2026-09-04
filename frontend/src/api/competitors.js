import { request } from "./client";


function normalizeCategory(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replaceAll("_", " ")
    .replaceAll("-", " ");
}


function extractList(response) {
  if (Array.isArray(response)) {
    return response;
  }

  const possibleLists = [
    response?.leads,
    response?.businesses,
    response?.results,
    response?.items,
    response?.data,
  ];

  return (
    possibleLists.find(Array.isArray)
    || []
  );
}


function getRelatedCategories(category) {
  const normalized = normalizeCategory(category);

  const groups = {
    "medical center": [
      "medical center",
      "medical centre",
      "clinic",
      "hospital",
      "doctor",
      "doctors",
      "dentist",
      "healthcare",
    ],

    clinic: [
      "medical center",
      "medical centre",
      "clinic",
      "hospital",
      "doctor",
      "doctors",
      "dentist",
      "healthcare",
    ],

    dentist: [
      "dentist",
      "dental clinic",
      "clinic",
      "medical center",
    ],

    restaurant: [
      "restaurant",
      "cafe",
      "fast food",
      "food court",
    ],

    cafe: [
      "cafe",
      "coffee shop",
      "restaurant",
    ],
  };

  return groups[normalized] || [normalized];
}


function matchesCategory(
  business,
  categories,
) {
  const businessCategory = normalizeCategory(
    business?.category
    || business?.industry,
  );

  return categories.some(
    (category) =>
      businessCategory.includes(category)
      || category.includes(businessCategory),
  );
}


function normalizeFallbackBusiness(
  business,
  index,
) {
  return {
    id:
      business?.id
      ?? business?.lead_id
      ?? `crm-competitor-${index}`,

    businessName:
      business?.businessName
      ?? business?.business_name
      ?? business?.name
      ?? "Unnamed business",

    category:
      business?.category
      ?? business?.industry
      ?? "Business",

    location:
      business?.location
      ?? business?.address
      ?? "Location unavailable",

    phone:
      business?.phone
      ?? "Not found",

    email:
      business?.email
      ?? "Not found",

    website:
      business?.website
      ?? "Not found",

    priority:
      business?.priority
      ?? "Medium",

    opportunityScore:
      Number(
        business?.opportunityScore
        ?? business?.opportunity_score
        ?? business?.ai_score
        ?? 60,
      ),

    contactQuality:
      Number(
        business?.contactQuality
        ?? business?.contact_quality
        ?? 50,
      ),

    source: "Nestora CRM",
  };
}


async function getCRMCompetitors(
  category,
  limit,
) {
  const response = await request(
    "/crm/leads",
  );

  const relatedCategories =
    getRelatedCategories(category);

  return extractList(response)
    .filter((business) =>
      matchesCategory(
        business,
        relatedCategories,
      ),
    )
    .map(normalizeFallbackBusiness)
    .slice(0, limit);
}


export async function getCompetitors(
  category,
  location = "",
  limit = 8,
) {
  const normalizedCategory =
    normalizeCategory(category)
    || "business";

  const normalizedLocation =
    String(location || "").trim();

  const query = new URLSearchParams({
    category: normalizedCategory,
    location: normalizedLocation,
    limit: String(limit),
  });

  try {
    const liveResults = await request(
      `/marketing/competitors?${query.toString()}`,
    );

    if (
      Array.isArray(liveResults)
      && liveResults.length > 0
    ) {
      return liveResults;
    }
  } catch (error) {
    console.warn(
      "Live competitor search unavailable. "
      + "Using CRM fallback.",
      error,
    );
  }

  return getCRMCompetitors(
    normalizedCategory,
    limit,
  );
}


export default {
  getCompetitors,
};