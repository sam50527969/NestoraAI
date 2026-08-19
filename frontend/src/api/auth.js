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

export function getCurrentAccount() {
  return request("/auth/me");
}