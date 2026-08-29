import {
  request,
} from "./client";

export async function getWorkspaces({
  offset = 0,
  limit = 100,
} = {}) {
  const query = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  });

  const response = await request(
    `/businesses?${query.toString()}`,
  );

  return {
    businesses: Array.isArray(
      response?.businesses,
    )
      ? response.businesses
      : [],
    offset: response?.offset ?? offset,
    limit: response?.limit ?? limit,
    count: response?.count ?? 0,
  };
}
