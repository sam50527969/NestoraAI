import {
  describe,
  expect,
  it,
} from "vitest";

import {
  getLeadCategory,
  matchesLeadSearch,
  normalizeLeadsResponse,
} from "../crm";

describe("normalizeLeadsResponse", () => {
  const leads = [
    {
      id: 1,
      name: "Test Clinic",
    },
  ];

  it("accepts a direct array", () => {
    expect(
      normalizeLeadsResponse(leads),
    ).toEqual(leads);
  });

  it("accepts supported wrapped responses", () => {
    expect(
      normalizeLeadsResponse({
        data: leads,
      }),
    ).toEqual(leads);

    expect(
      normalizeLeadsResponse({
        leads,
      }),
    ).toEqual(leads);

    expect(
      normalizeLeadsResponse({
        data: {
          leads,
        },
      }),
    ).toEqual(leads);
  });

  it("returns an empty array for invalid data", () => {
    expect(
      normalizeLeadsResponse(null),
    ).toEqual([]);

    expect(
      normalizeLeadsResponse({}),
    ).toEqual([]);

    expect(
      normalizeLeadsResponse({
        leads: "invalid",
      }),
    ).toEqual([]);
  });
});

describe("getLeadCategory", () => {
  it("uses supported category fields", () => {
    expect(
      getLeadCategory({
        category: "clinic",
      }),
    ).toBe("clinic");

    expect(
      getLeadCategory({
        type: "restaurant",
      }),
    ).toBe("restaurant");

    expect(
      getLeadCategory({
        business_type: "garage",
      }),
    ).toBe("garage");
  });

  it("uses Unknown when category data is missing", () => {
    expect(
      getLeadCategory({}),
    ).toBe("Unknown");
  });
});

describe("matchesLeadSearch", () => {
  const lead = {
    name: "Gulf Neon Advertising",
    category: "signage",
    address: "Doha Industrial Area",
    phone: "+974 5555 1000",
    website: "https://gulfneon.example",
    source: "Google Places",
    status: "Contacted",
    priority: "High",
    tags: "advertising, outdoor",
    assigned_to: "CEO",
  };

  it("matches searchable lead fields without case sensitivity", () => {
    expect(
      matchesLeadSearch(
        lead,
        "gulf neon",
      ),
    ).toBe(true);

    expect(
      matchesLeadSearch(
        lead,
        "DOHA INDUSTRIAL",
      ),
    ).toBe(true);

    expect(
      matchesLeadSearch(
        lead,
        "contacted",
      ),
    ).toBe(true);

    expect(
      matchesLeadSearch(
        lead,
        "outdoor",
      ),
    ).toBe(true);
  });

  it("returns false when no field matches", () => {
    expect(
      matchesLeadSearch(
        lead,
        "dental surgery",
      ),
    ).toBe(false);
  });

  it("matches an empty search term", () => {
    expect(
      matchesLeadSearch(
        lead,
        "   ",
      ),
    ).toBe(true);
  });
});