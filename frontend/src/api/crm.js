import { request } from "./client";

export function saveLead(lead) {
  return request("/crm/leads", {
    method: "POST",
    body: JSON.stringify(lead),
  });
}

export function getSavedLeads() {
  return request("/crm/leads");
}

export function updateLead(leadId, leadData) {
  return request(`/crm/leads/${leadId}`, {
    method: "PUT",
    body: JSON.stringify(leadData),
  });
}