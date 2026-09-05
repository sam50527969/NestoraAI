import {
  getAccessToken,
} from "../auth/session";
import {
  getActiveBusinessUid,
} from "../workspace/session";

import {
  API_BASE_URL,
} from "../config/api";

export {
  API_BASE_URL,
};

export async function request(
  endpoint,
  options = {},
) {
  const accessToken =
    getAccessToken();

  const activeBusinessUid =
    getActiveBusinessUid();

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
        ...(activeBusinessUid
          ? {
              "X-Business-Uid":
                activeBusinessUid,
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
