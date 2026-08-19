import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "../session";

afterEach(() => {
  window.sessionStorage.clear();
});

describe("authentication session", () => {
  it("returns null when no token exists", () => {
    expect(
      getAccessToken(),
    ).toBeNull();
  });

  it("stores and retrieves an access token", () => {
    setAccessToken(
      "stored-access-token",
    );

    expect(
      getAccessToken(),
    ).toBe(
      "stored-access-token",
    );
  });

  it("replaces an existing token", () => {
    setAccessToken(
      "old-token",
    );

    setAccessToken(
      "new-token",
    );

    expect(
      getAccessToken(),
    ).toBe(
      "new-token",
    );
  });

  it("clears the stored token", () => {
    setAccessToken(
      "temporary-token",
    );

    clearAccessToken();

    expect(
      getAccessToken(),
    ).toBeNull();
  });
});