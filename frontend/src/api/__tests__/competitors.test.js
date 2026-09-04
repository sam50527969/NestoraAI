import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearAccessToken,
} from "../../auth/session";

import {
  getCompetitors,
} from "../competitors";

afterEach(() => {
  clearAccessToken();
  vi.unstubAllGlobals();
});

describe("competitor workspace location", () => {
  it("preserves the supplied workspace location", async () => {
    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        headers: {
          get: () =>
            "application/json",
        },
        json: async () => ([
          {
            businessName:
              "Sydney Auto Service",
            category: "car_repair",
            location:
              "Sydney, New South Wales, Australia",
          },
        ]),
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await getCompetitors(
      "Auto Repair Workshop",
      "Sydney, New South Wales, Australia",
      8,
    );

    const requestUrl =
      fetchMock.mock.calls[0][0];

    expect(requestUrl).toContain(
      "/marketing/competitors?",
    );

    const url = new URL(requestUrl);

    expect(
      url.searchParams.get("location"),
    ).toBe(
      "Sydney, New South Wales, Australia",
    );

    expect(requestUrl).not.toContain(
      "Doha",
    );
    expect(requestUrl).not.toContain(
      "Qatar",
    );
  });

  it("does not replace an empty location with Doha", async () => {
    const fetchMock = vi.fn(
      async () => ({
        ok: true,
        headers: {
          get: () =>
            "application/json",
        },
        json: async () => ([
          {
            businessName:
              "Generic Auto Service",
            category: "car_repair",
            location:
              "Location unavailable",
          },
        ]),
      }),
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    await getCompetitors(
      "Auto Repair Workshop",
      "",
      8,
    );

    const requestUrl =
      fetchMock.mock.calls[0][0];

    const url = new URL(requestUrl);

    expect(
      url.searchParams.get("location"),
    ).toBe("");

    expect(requestUrl).not.toContain(
      "Doha",
    );
    expect(requestUrl).not.toContain(
      "Qatar",
    );
  });

  it("does not invent a regional location for CRM fallback", async () => {
    const fetchMock = vi.fn(
      async (url) => {
        if (
          String(url).includes(
            "/marketing/competitors?",
          )
        ) {
          return {
            ok: false,
            text: async () =>
              "Competitor search unavailable",
          };
        }

        if (
          String(url).includes(
            "/crm/leads",
          )
        ) {
          return {
            ok: true,
            headers: {
              get: () =>
                "application/json",
            },
            json: async () => ([
              {
                id: 10,
                business_name:
                  "Local Auto Workshop",
                category:
                  "Auto Repair Workshop",
              },
            ]),
          };
        }

        throw new Error(
          `Unexpected request: ${url}`,
        );
      },
    );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    const competitors =
      await getCompetitors(
        "Auto Repair Workshop",
        "Dubai, United Arab Emirates",
        8,
      );

    expect(competitors).toHaveLength(1);

    expect(
      competitors[0].location,
    ).toBe(
      "Location unavailable",
    );

    expect(
      competitors[0].location,
    ).not.toContain("Doha");

    expect(
      competitors[0].location,
    ).not.toContain("Qatar");
  });
});
