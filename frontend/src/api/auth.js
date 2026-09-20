import {
  request,
} from "./client";

export function registerAccount(
  account,
) {
  return request(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify(account),
    },
  );
}

export function loginAccount(
  credentials,
) {
  return request(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify(
        credentials,
      ),
    },
  );
}

export function requestPasswordReset(
  email,
) {
  return request(
    "/auth/password-reset/request",
    {
      method: "POST",
      body: JSON.stringify({
        email,
      }),
    },
  );
}

export function confirmPasswordReset({
  token,
  password,
}) {
  return request(
    "/auth/password-reset/confirm",
    {
      method: "POST",
      body: JSON.stringify({
        token,
        password,
      }),
    },
  );
}

export function getCurrentAccount() {
  return request("/auth/me");
}
