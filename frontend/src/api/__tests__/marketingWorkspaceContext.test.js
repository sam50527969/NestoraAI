import {
  describe,
  expect,
  it,
} from "vitest";

import {
  createDefaultMarketingRequest,
  createMarketingBusinessView,
  createMarketingRequestFromWorkspace,
  mergeMarketingRequestWithWorkspace,
} from "../marketingApi";

const workspace = {
  business_uid: "biz_global",
  name: "Global Neon",
  industry: "professional_services",
  country: "Australia",
  city: "Sydney",
  region: "New South Wales",
  timezone: "Australia/Sydney",
  locale: "en-AU",
  description: "Custom signage studio",
  finances: {
    currency: "AUD",
  },
  metadata: {
    business_type: "Advertising agency",
    products_services: [
      "Neon signs",
      "Retail displays",
    ],
    preferred_languages: [
      "English",
    ],
    target_audience: [
      "Retail brands",
    ],
    website:
      "https://global.example",
  },
};

describe("marketing workspace context", () => {
  it("has no regional or industry defaults", () => {
    const request =
      createDefaultMarketingRequest();

    expect(
      request.business.location,
    ).toBe("");
    expect(
      request.goal.currency,
    ).toBe("");
    expect(
      request.business
        .preferred_languages,
    ).toEqual([]);
  });

  it("maps the authoritative workspace", () => {
    const request =
      createMarketingRequestFromWorkspace(
        workspace,
      );

    expect(
      request.business.business_id,
    ).toBe("biz_global");
    expect(
      request.business.industry,
    ).toBe(
      "Professional Services / Advertising agency",
    );
    expect(
      request.business.location,
    ).toBe(
      "Sydney, New South Wales, Australia",
    );
    expect(
      request.business
        .products_or_services,
    ).toEqual([
      "Neon signs",
      "Retail displays",
    ]);
    expect(
      request.goal.currency,
    ).toBe("AUD");
  });

  it("prevents campaign edits from replacing workspace identity", () => {
    const current =
      createMarketingRequestFromWorkspace(
        workspace,
      );

    current.business.industry =
      "Store";
    current.business.location =
      "Doha, Qatar";
    current.goal.currency = "QAR";
    current.goal.objective =
      "Grow qualified leads";
    current.business.target_audience = [
      "New customers",
    ];

    const merged =
      mergeMarketingRequestWithWorkspace(
        current,
        workspace,
      );

    expect(
      merged.business.industry,
    ).toBe(
      "Professional Services / Advertising agency",
    );
    expect(
      merged.business.location,
    ).toBe(
      "Sydney, New South Wales, Australia",
    );
    expect(
      merged.goal.currency,
    ).toBe("AUD");
    expect(
      merged.goal.objective,
    ).toBe("Grow qualified leads");
    expect(
      merged.business
        .target_audience,
    ).toEqual(["New customers"]);
  });

  it("builds competitor context from workspace fields", () => {
    const view =
      createMarketingBusinessView(
        workspace,
      );

    expect(view.id).toBe(
      "biz_global",
    );
    expect(view.category).toBe(
      "Professional Services",
    );
    expect(view.address).toContain(
      "Australia",
    );
    expect(view.source).toBe(
      "Workspace",
    );
  });
});
