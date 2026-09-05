import { useEffect, useMemo, useRef, useState } from "react";

import {
  getDashboardSummary,
  getSavedLeads,
  searchBusinesses,
} from "../../../api";

export default function useDashboardData({
  businessUid,
  currency,
} = {}) {
  const [leads, setLeads] = useState([]);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [isDashboardLoading, setIsDashboardLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [dashboardError, setDashboardError] = useState("");
  const [searchError, setSearchError] = useState("");

  const activeBusinessUidRef = useRef(
    businessUid
  );

  useEffect(() => {
    activeBusinessUidRef.current =
      businessUid;

    let cancelled = false;

    async function loadDashboard() {
      setIsDashboardLoading(true);
      setDashboardSummary(null);
      setLeads([]);
      setIsSearching(false);
      setDashboardError("");
      setSearchError("");

      try {
        const [summaryData, leadsData] = await Promise.all([
          getDashboardSummary(),
          getSavedLeads(),
        ]);

        if (cancelled) {
          return;
        }

        setDashboardSummary(summaryData);
        setLeads(
          Array.isArray(leadsData)
            ? leadsData
            : []
        );
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.error(
          "Failed to load dashboard:",
          error
        );

        setDashboardError(
          "Unable to load the executive dashboard."
        );
      } finally {
        if (!cancelled) {
          setIsDashboardLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [businessUid]);

  async function searchLeads(searchData) {
    const requestBusinessUid =
      businessUid;

    try {
      setIsSearching(true);
      setSearchError("");

      const data = await searchBusinesses({
        businessType: searchData.businessType,
        location: searchData.location,
        quantity: searchData.quantity || "20",
      });

      if (
        activeBusinessUidRef.current
        !== requestBusinessUid
      ) {
        return;
      }

      setLeads(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      if (
        activeBusinessUidRef.current
        !== requestBusinessUid
      ) {
        return;
      }

      console.error(
        "Failed to search businesses:",
        error
      );

      setSearchError(
        "Unable to fetch businesses."
      );
    } finally {
      if (
        activeBusinessUidRef.current
        === requestBusinessUid
      ) {
        setIsSearching(false);
      }
    }
  }

  const topOpportunity = useMemo(() => {
    if (!leads.length) {
      return null;
    }

    return [...leads].sort((firstLead, secondLead) => {
      const firstScore =
        firstLead.ai_score ??
        firstLead.opportunityScore ??
        0;

      const secondScore =
        secondLead.ai_score ??
        secondLead.opportunityScore ??
        0;

      return secondScore - firstScore;
    })[0];
  }, [leads]);

  const metrics = useMemo(() => {
    if (!dashboardSummary?.kpis) {
      return [];
    }

    const { kpis } = dashboardSummary;

    return [
      {
        title: "Total Leads",
        value: String(kpis.total_leads ?? 0),
        subtitle: "Saved in CRM",
        color: "#22c55e",
      },
      {
        title: "High Priority",
        value: String(kpis.high_priority_leads ?? 0),
        subtitle: "Best opportunities",
        color: "#f59e0b",
      },
      {
        title: "Qualified",
        value: String(kpis.qualified_leads ?? 0),
        subtitle: "Ready for follow-up",
        color: "#38bdf8",
      },
      {
        title: "Pipeline Value",
        value: [
          currency,
          (kpis.pipeline_value ?? 0).toLocaleString(),
        ]
          .filter(Boolean)
          .join(" "),
        subtitle: `${kpis.won_leads ?? 0} won leads`,
        color: "#8b5cf6",
      },
      {
        title: "AI Score",
        value: `${kpis.ai_score ?? 0}%`,
        subtitle: "Business confidence",
        color: "#22c55e",
      },
    ];
  }, [dashboardSummary, currency]);

  return {
    leads,
    dashboardSummary,
    metrics,
    topOpportunity,
    isDashboardLoading,
    isSearching,
    dashboardError,
    searchError,
    searchLeads,
  };
}