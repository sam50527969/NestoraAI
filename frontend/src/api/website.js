import { request } from "./client";

export function analyzeWebsite(url) {
  return request("/website/analyze", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}