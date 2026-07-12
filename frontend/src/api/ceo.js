import { request } from "./client";

export function askCEO(question) {
  return request("/ceo/ask", {
    method: "POST",
    body: JSON.stringify({
      question,
    }),
  });
}