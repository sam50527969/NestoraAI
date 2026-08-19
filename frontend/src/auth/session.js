const ACCESS_TOKEN_KEY =
  "nestora.access_token";

export function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return (
    window.sessionStorage.getItem(
      ACCESS_TOKEN_KEY,
    ) || null
  );
}

export function setAccessToken(
  token,
) {
  if (typeof window === "undefined") {
    return;
  }

  window.sessionStorage.setItem(
    ACCESS_TOKEN_KEY,
    token,
  );
}

export function clearAccessToken() {
  if (typeof window === "undefined") {
    return;
  }

  window.sessionStorage.removeItem(
    ACCESS_TOKEN_KEY,
  );
}