import { useEffect, useMemo, useState } from "react";

import {
  getDashboardSummary,
  getSampleLeads,
  searchBusinesses,
} from "../../../api";

export default function useDashboardData() {
  const [leads, setLeads] = useState([]);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [isDashboardLoading, setIsDashboardLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        setErrorMessage("");

        const [summaryData, leadsData] = await Promise.all([
          getDashboardSummary(),
          getSampleLeads(),
        ]);

        setDashboardSummary(summaryData);
        setLeads(Array.isArray(leadsData) ? leadsData : []);
      } catch (error) {
        console.error("Failed to load dashboard:", error);
        setErrorMessage("Unable to load the executive dashboard.");
      } finally {
        setIsDashboardLoading(false);
      }
    }

    loadDashboard();
  }, []);

  async function searchLeads(searchData) {
    try {
      setIsSearching(true);
      setErrorMessage("");

      const data = await searchBusinesses({
        businessType: searchData.businessType,
        location: searchData.location,
        quantity: searchData.quantity || "20",
      });

      setLeads(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to search businesses:", error);
      setErrorMessage("Unable to fetch businesses.");
    } finally {
      setIsSearching(false);
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
        value: `QAR ${(kpis.pipeline_value ?? 0).toLocaleString()}`,
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
  }, [dashboardSummary]);

  return {
    leads,
    dashboardSummary,
    metrics,
    topOpportunity,
    isDashboardLoading,
    isSearching,
    errorMessage,
    searchLeads,
  };
}