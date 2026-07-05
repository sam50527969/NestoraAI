import { request } from "./client";

export function getDashboardSummary() {
  return request("/dashboard/summary");
}