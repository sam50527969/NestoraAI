import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearActiveBusinessUid,
  setActiveBusinessUid,
} from "../../workspace/session";

import {
  request,
} from "../client";

afterEach(() => {
  clearActiveBusinessUid();
  vi.unstubAllGlobals();
});

describe("workspace request header", () => {
  it("sends the active business UID", async () => {
    setActiveBusinessUid(
      "biz_selected",
    );

    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        json: async () => [],
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await request("/crm/leads");

    expect(
      fetchMock,
    ).toHaveBeenCalledWith(
      expect.stringContaining(
        "/crm/leads",
      ),
      expect.objectContaining({
        headers:
          expect.objectContaining({
            "X-Business-Uid":
              "biz_selected",
          }),
      }),
    );
  });

  it("allows an explicit header override", async () => {
    setActiveBusinessUid(
      "biz_selected",
    );

    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        json: async () => [],
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await request(
      "/crm/leads",
      {
        headers: {
          "X-Business-Uid":
            "biz_override",
        },
      },
    );

    expect(
      fetchMock.mock.calls[0][1]
        .headers[
          "X-Business-Uid"
        ],
    ).toBe("biz_override");
  });
});
