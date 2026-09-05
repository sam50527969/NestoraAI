import {
  act,
  renderHook,
  waitFor,
} from "@testing-library/react";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import useDashboardData from "../useDashboardData";

const {
  getDashboardSummaryMock,
  getSavedLeadsMock,
  searchBusinessesMock,
} = vi.hoisted(() => ({
  getDashboardSummaryMock: vi.fn(),
  getSavedLeadsMock: vi.fn(),
  searchBusinessesMock: vi.fn(),
}));

vi.mock("../../../../api", () => ({
  getDashboardSummary:
    getDashboardSummaryMock,
  getSavedLeads:
    getSavedLeadsMock,
  searchBusinesses:
    searchBusinessesMock,
}));

function summary({
  totalLeads,
  pipelineValue,
}) {
  return {
    kpis: {
      total_leads: totalLeads,
      high_priority_leads: 1,
      qualified_leads: 1,
      won_leads: 0,
      pipeline_value: pipelineValue,
      ai_score: 80,
    },
    pipeline: [],
    activity: [],
    priorities: [],
    recommendations: [],
  };
}

describe("useDashboardData workspace behavior", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    getDashboardSummaryMock
      .mockResolvedValueOnce(
        summary({
          totalLeads: 2,
          pipelineValue: 5000,
        }),
      )
      .mockResolvedValueOnce(
        summary({
          totalLeads: 3,
          pipelineValue: 9000,
        }),
      );

    getSavedLeadsMock
      .mockResolvedValueOnce([
        {
          id: 1,
          name: "Atlas Opportunity",
          ai_score: 80,
        },
      ])
      .mockResolvedValueOnce([
        {
          id: 2,
          name: "Dental Opportunity",
          ai_score: 90,
        },
      ]);
  });

  it(
    "reloads dashboard data and currency when workspace changes",
    async () => {
      const {
        result,
        rerender,
      } = renderHook(
        ({
          businessUid,
          currency,
        }) =>
          useDashboardData({
            businessUid,
            currency,
          }),
        {
          initialProps: {
            businessUid: "biz_atlas",
            currency: "AED",
          },
        },
      );

      await waitFor(() => {
        expect(
          result.current.isDashboardLoading,
        ).toBe(false);
      });

      expect(
        getDashboardSummaryMock,
      ).toHaveBeenCalledTimes(1);

      expect(
        getSavedLeadsMock,
      ).toHaveBeenCalledTimes(1);

      expect(
        result.current.dashboardSummary
          .kpis.total_leads,
      ).toBe(2);

      expect(
        result.current.topOpportunity.name,
      ).toBe("Atlas Opportunity");

      expect(
        result.current.metrics.find(
          (metric) =>
            metric.title === "Pipeline Value",
        ).value,
      ).toBe("AED 5,000");

      await act(async () => {
        rerender({
          businessUid: "biz_dental",
          currency: "QAR",
        });
      });

      await waitFor(() => {
        expect(
          getDashboardSummaryMock,
        ).toHaveBeenCalledTimes(2);
      });

      await waitFor(() => {
        expect(
          result.current.dashboardSummary
            .kpis.total_leads,
        ).toBe(3);
      });

      expect(
        getSavedLeadsMock,
      ).toHaveBeenCalledTimes(2);

      expect(
        result.current.topOpportunity.name,
      ).toBe("Dental Opportunity");

      expect(
        result.current.metrics.find(
          (metric) =>
            metric.title === "Pipeline Value",
        ).value,
      ).toBe("QAR 9,000");
    },
  );

  it("ignores an older workspace response after switching workspaces", async () => {
    getDashboardSummaryMock.mockReset();
    getSavedLeadsMock.mockReset();

    let resolveAtlasSummary;
    let resolveAtlasLeads;

    const atlasSummaryPromise = new Promise(
      (resolve) => {
        resolveAtlasSummary = resolve;
      }
    );

    const atlasLeadsPromise = new Promise(
      (resolve) => {
        resolveAtlasLeads = resolve;
      }
    );

    const dentalSummary = {
      kpis: {
        total_leads: 1,
        high_priority_leads: 1,
        qualified_leads: 1,
        won_leads: 0,
        pipeline_value: 9000,
        ai_score: 90,
      },
      activity: [],
    };

    const dentalLeads = [
      {
        name: "Dental Opportunity",
        ai_score: 90,
      },
    ];

    getDashboardSummaryMock
      .mockImplementationOnce(
        () => atlasSummaryPromise
      )
      .mockResolvedValueOnce(
        dentalSummary
      );

    getSavedLeadsMock
      .mockImplementationOnce(
        () => atlasLeadsPromise
      )
      .mockResolvedValueOnce(
        dentalLeads
      );

    const { result, rerender } = renderHook(
      ({ businessUid, currency }) =>
        useDashboardData({
          businessUid,
          currency,
        }),
      {
        initialProps: {
          businessUid: "biz_atlas",
          currency: "AED",
        },
      }
    );

    rerender({
      businessUid: "biz_dental",
      currency: "QAR",
    });

    await waitFor(() => {
      expect(
        result.current.isDashboardLoading
      ).toBe(false);
    });

    expect(
      result.current.dashboardSummary
        ?.kpis?.pipeline_value
    ).toBe(9000);

    expect(
      result.current.metrics.find(
        (metric) =>
          metric.title === "Pipeline Value"
      )?.value
    ).toBe("QAR 9,000");

    expect(
      result.current.topOpportunity?.name
    ).toBe("Dental Opportunity");

    await act(async () => {
      resolveAtlasSummary({
        kpis: {
          total_leads: 1,
          high_priority_leads: 1,
          qualified_leads: 1,
          won_leads: 0,
          pipeline_value: 5000,
          ai_score: 80,
        },
        activity: [],
      });

      resolveAtlasLeads([
        {
          name: "Atlas Stale Opportunity",
          ai_score: 99,
        },
      ]);

      await atlasSummaryPromise;
      await atlasLeadsPromise;
    });

    expect(
      result.current.dashboardSummary
        ?.kpis?.pipeline_value
    ).toBe(9000);

    expect(
      result.current.metrics.find(
        (metric) =>
          metric.title === "Pipeline Value"
      )?.value
    ).toBe("QAR 9,000");

    expect(
      result.current.topOpportunity?.name
    ).toBe("Dental Opportunity");
  });

});
