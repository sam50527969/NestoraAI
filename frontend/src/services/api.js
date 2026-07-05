const API_BASE_URL = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "API request failed");
  }

  return response.json();
}

export async function getSampleLeads() {
  return request("/leads");
}

export async function searchBusinesses({ businessType, location, quantity }) {
  const params = new URLSearchParams({
    business_type: businessType,
    location,
    limit: quantity,
  });

  return request(`/search/businesses?${params.toString()}`);
}

export async function saveLead(lead) {
  return request("/crm/leads", {
    method: "POST",
    body: JSON.stringify(lead),
  });
}

export async function getSavedLeads() {
  return request("/crm/leads");
}