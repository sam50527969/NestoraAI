const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export function getLeadDetails(leadId) {
  return request(`/crm/leads/${leadId}`);
}

export function updateLead(leadId, payload) {
  return request(`/crm/leads/${leadId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
