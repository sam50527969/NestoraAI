import { request } from "./client";


function normalizeBusiness(rawBusiness, index) {
  return {
    id:
      rawBusiness?.id
      ?? rawBusiness?.lead_id
      ?? rawBusiness?.source_id
      ?? `business-${index}`,

    name:
      rawBusiness?.name
      ?? rawBusiness?.businessName
      ?? rawBusiness?.business_name
      ?? "Unnamed business",

    category:
      rawBusiness?.category
      ?? rawBusiness?.industry
      ?? "Business",

    address:
      rawBusiness?.address
      ?? rawBusiness?.location
      ?? "",

    location:
      rawBusiness?.location
      ?? rawBusiness?.address
      ?? "",

    phone:
      rawBusiness?.phone
      ?? "Not found",

    email:
      rawBusiness?.email
      ?? "Not found",

    website:
      rawBusiness?.website
      ?? "Not found",

    status:
      rawBusiness?.status
      ?? "New",

    priority:
      rawBusiness?.priority
      ?? "Medium",

    notes:
      rawBusiness?.notes
      ?? "",

    tags:
      rawBusiness?.tags
      ?? "",

    aiScore:
      rawBusiness?.ai_score
      ?? rawBusiness?.aiScore
      ?? null,

    aiRecommendation:
      rawBusiness?.ai_recommendation
      ?? rawBusiness?.aiRecommendation
      ?? "",

    aiOpportunity:
      rawBusiness?.ai_opportunity
      ?? rawBusiness?.aiOpportunity
      ?? "",

    opportunityScore:
      rawBusiness?.opportunity_score
      ?? rawBusiness?.opportunityScore
      ?? null,

    source:
      rawBusiness?.source
      ?? "CRM",
  };
}


function extractBusinessList(response) {
  if (Array.isArray(response)) {
    return response;
  }

  const possibleLists = [
    response?.leads,
    response?.businesses,
    response?.items,
    response?.results,
    response?.data,
  ];

  return (
    possibleLists.find(Array.isArray)
    || []
  );
}


export async function getSavedBusinesses() {
  const response = await request("/crm/leads");

  return extractBusinessList(response)
    .map(normalizeBusiness)
    .sort((left, right) =>
      left.name.localeCompare(right.name),
    );
}


export async function getSavedBusiness(
  businessId,
) {
  const businesses = await getSavedBusinesses();

  return (
    businesses.find(
      (business) =>
        String(business.id)
        === String(businessId),
    )
    || null
  );
}
