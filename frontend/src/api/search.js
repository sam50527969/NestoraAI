import { request } from "./client";

export function searchBusinesses({ businessType, location, quantity }) {
  const params = new URLSearchParams({
    business_type: businessType,
    location,
    limit: quantity,
  });

  return request(`/search/businesses?${params.toString()}`);
}