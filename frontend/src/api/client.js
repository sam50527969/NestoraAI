export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


export async function request(
  endpoint,
  options = {},
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        "Content-Type":
          "application/json",
        ...(options.headers || {}),
      },
      ...options,
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