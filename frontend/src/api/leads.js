import { request } from "./client";

export function getSampleLeads() {
  return request("/leads");
}