import { request } from "./client";

export function generateOutreach(lead) {
  return request("/outreach/generate", {
    method: "POST",
    body: JSON.stringify({
      lead,
      offer: "99 QAR starter business package",
    }),
  });
}