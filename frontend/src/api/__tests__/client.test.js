import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearAccessToken,
  setAccessToken,
} from "../../auth/session";

import {
  request,
} from "../client";

afterEach(() => {
  clearAccessToken();
  vi.unstubAllGlobals();
});

describe("request", () => {
  it("returns parsed JSON for a successful response", async () => {
    const payload = {
      id: 12,
      name: "API Test Lead",
    };

    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        json: async () =>
          payload,
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    const result = await request(
      "/crm/leads/12",
    );

    expect(result).toEqual(
      payload,
    );

    expect(
      fetchMock,
    ).toHaveBeenCalledWith(
      expect.stringContaining(
        "/crm/leads/12",
      ),
      expect.objectContaining({
        headers: {
          "Content-Type":
            "application/json",
        },
      }),
    );
  });

  it("adds the stored authentication token", async () => {
    setAccessToken(
      "stored-token",
    );

    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        json: async () => ({
          success: true,
        }),
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await request("/auth/me");

    expect(
      fetchMock,
    ).toHaveBeenCalledWith(
      expect.stringContaining(
        "/auth/me",
      ),
      expect.objectContaining({
        headers: {
          "Content-Type":
            "application/json",
          Authorization:
            "Bearer stored-token",
        },
      }),
    );
  });

  it("allows custom headers to override defaults", async () => {
    setAccessToken(
      "stored-token",
    );

    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        json: async () => ({
          success: true,
        }),
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await request(
      "/test",
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/custom+json",
          Authorization:
            "Bearer custom-token",
          "X-Request-ID":
            "request-123",
        },
        body: JSON.stringify({
          value: 1,
        }),
      },
    );

    expect(
      fetchMock,
    ).toHaveBeenCalledWith(
      expect.stringContaining(
        "/test",
      ),
      expect.objectContaining({
        method: "POST",
        headers: {
          "Content-Type":
            "application/custom+json",
          Authorization:
            "Bearer custom-token",
          "X-Request-ID":
            "request-123",
        },
      }),
    );
  });

  it("does not add authorization without a token", async () => {
    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        json: async () => ({
          success: true,
        }),
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await request("/test");

    const requestOptions =
      fetchMock.mock.calls[0][1];

    expect(
      requestOptions.headers,
    ).not.toHaveProperty(
      "Authorization",
    );
  });

  it("throws the backend error response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () => ({
          ok: false,
          text: async () =>
            "Lead was not found.",
        }),
      ),
    );

    await expect(
      request(
        "/crm/leads/999999",
      ),
    ).rejects.toThrow(
      "Lead was not found.",
    );
  });

  it("uses a fallback error message", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () => ({
          ok: false,
          text: async () => "",
        }),
      ),
    );

    await expect(
      request("/failure"),
    ).rejects.toThrow(
      "API request failed",
    );
  });
});