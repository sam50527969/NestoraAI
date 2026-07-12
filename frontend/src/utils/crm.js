export function normalizeLeadsResponse(response) {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response?.data)) return response.data;
  if (Array.isArray(response?.leads)) return response.leads;
  if (Array.isArray(response?.data?.leads)) return response.data.leads;

  return [];
}

export function getLeadCategory(lead) {
  return lead.category || lead.type || lead.business_type || "Unknown";
}

export function matchesLeadSearch(lead, searchTerm) {
  const value = searchTerm.trim().toLowerCase();

  if (!value) return true;

  const searchableText = [
    lead.name,
    getLeadCategory(lead),
    lead.address,
    lead.phone,
    lead.website,
    lead.source,
    lead.status,
    lead.priority,
    lead.tags,
    lead.assigned_to,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return searchableText.includes(value);
}