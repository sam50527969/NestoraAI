import {
  describe,
  expect,
  it,
} from "vitest";

import {
  formToWorkspace,
  workspaceToForm,
} from "../workspacePayload";

describe("workspace payload", () => {
  it("builds a universal create payload", () => {
    const payload = formToWorkspace({
      name: "  Global Studio  ",
      industry: "professional_services",
      country: "  Canada ",
      city: "Toronto",
      region: "Ontario",
      timezone: "America/Toronto",
      locale: "en-CA",
      size: "micro",
      currency: "cad",
      description: " Advisory ",
      employee_count: "4",
      locations_count: "1",
      business_type: "Consultancy",
      products_services:
        "Strategy, Research",
      preferred_languages:
        "English, French",
    });

    expect(payload.name).toBe(
      "Global Studio",
    );
    expect(
      payload.finances.currency,
    ).toBe("CAD");
    expect(
      payload.metadata
        .products_services,
    ).toEqual([
      "Strategy",
      "Research",
    ]);
    expect(
      payload.metadata
        .preferred_languages,
    ).toEqual([
      "English",
      "French",
    ]);
  });

  it("preserves full profile data during edits", () => {
    const current = {
      name: "Existing",
      industry: "retail",
      country: "Australia",
      size: "small",
      team: {
        employee_count: 3,
        departments: ["Sales"],
        roles: {
          manager: 1,
        },
      },
      customers: {
        total_customers: 40,
      },
      finances: {
        currency: "AUD",
        monthly_revenue: 9000,
      },
      operations: {
        locations_count: 2,
        working_hours: [
          {
            day: "Monday",
          },
        ],
      },
      goals: ["Grow"],
      metadata: {
        source: "owner",
      },
    };

    const form =
      workspaceToForm(current);

    form.name = "Updated";

    const payload =
      formToWorkspace(
        form,
        current,
      );

    expect(
      payload.team.departments,
    ).toEqual(["Sales"]);
    expect(
      payload.finances
        .monthly_revenue,
    ).toBe(9000);
    expect(payload.goals).toEqual(
      ["Grow"],
    );
    expect(
      payload.metadata.source,
    ).toBe("owner");
  });
});
