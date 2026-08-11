import { request } from "./client";


function addDateFilters(
  searchParams,
  {
    startDate,
    endDate,
  } = {},
) {
  if (startDate) {
    searchParams.set(
      "start_date",
      startDate,
    );
  }

  if (endDate) {
    searchParams.set(
      "end_date",
      endDate,
    );
  }
}


export function saveLead(lead) {
  return request("/crm/leads", {
    method: "POST",
    body: JSON.stringify(lead),
  });
}


export function getSavedLeads() {
  return request("/crm/leads");
}


export function getDueFollowUps({
  limit = 100,
} = {}) {
  const searchParams =
    new URLSearchParams();

  searchParams.set(
    "limit",
    String(limit),
  );

  return request(
    `/crm/follow-ups/due?${searchParams.toString()}`,
  );
}


export function updateLead(
  leadId,
  leadData,
) {
  return request(
    `/crm/leads/${leadId}`,
    {
      method: "PUT",
      body: JSON.stringify(
        leadData,
      ),
    },
  );
}


export function getFollowUpActivities({
  leadId,
  startDate,
  endDate,
  limit = 100,
} = {}) {
  const searchParams =
    new URLSearchParams();

  if (leadId != null) {
    searchParams.set(
      "lead_id",
      String(leadId),
    );
  }

  addDateFilters(
    searchParams,
    {
      startDate,
      endDate,
    },
  );

  searchParams.set(
    "limit",
    String(limit),
  );

  return request(
    `/follow-up-activities?${searchParams.toString()}`,
  );
}


export function recordFollowUpOutcome(
  leadId,
  data,
) {
  return request(
    `/follow-up-activities/leads/${leadId}/outcome`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}


export function getFollowUpMetrics({
  startDate,
  endDate,
} = {}) {
  const searchParams =
    new URLSearchParams();

  addDateFilters(
    searchParams,
    {
      startDate,
      endDate,
    },
  );

  const query =
    searchParams.toString();

  return request(
    query
      ? `/follow-up-activities/metrics?${query}`
      : "/follow-up-activities/metrics",
  );
}