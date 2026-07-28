import { request } from "./client";

/**
 * Existing CEO chat endpoint
 */
export function askCEO(question) {
  return request("/ceo/ask", {
    method: "POST",
    body: JSON.stringify({
      question,
    }),
  });
}

/**
 * Analyze a business objective and generate a mission.
 */
export function createObjectiveMission({
  businessId,
  objective,
}) {
  return request("/ceo/objective", {
    method: "POST",
    body: JSON.stringify({
      business_id: businessId,
      objective,
    }),
  });
}