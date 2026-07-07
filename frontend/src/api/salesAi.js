import { request } from "./client";

export function analyzeLead(lead) {
  return request("/sales-ai/analyze", {
    method: "POST",
    body: JSON.stringify({ lead }),
  });
}