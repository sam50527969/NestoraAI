import {
  getAccessToken,
} from "../auth/session";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

export async function request(
  endpoint,
  options = {},
) {
  const accessToken =
    getAccessToken();

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers: {
        "Content-Type":
          "application/json",
        ...(accessToken
          ? {
              Authorization:
                `Bearer ${accessToken}`,
            }
          : {}),
        ...(options.headers || {}),
      },
    },
  );

  if (!response.ok) {
    const message =
      await response.text();

    throw new Error(
      message ||
        "API request failed",
    );
  }

  return response.json();
}