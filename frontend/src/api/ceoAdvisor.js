import { request } from "./client";

export function getCEOBrief() {
  return request("/ceo-advisor/brief");
}