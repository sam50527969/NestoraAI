import { useEffect, useMemo, useState } from "react";

import DashboardLayout from "../components/dashboard/DashboardLayout";
import DashboardResearch from "../components/dashboard/DashboardResearch";
import ExecutiveBrief from "../components/dashboard/ExecutiveBrief";
import ExecutiveHeader from "../components/dashboard/ExecutiveHeader";
import OpportunityPanel from "../components/dashboard/OpportunityPanel";
import QuickActions from "../components/dashboard/QuickActions";
import KPICard from "../components/KPICard";

import ActivityPanel from "../components/dashboard/panels/ActivityPanel";
import AnalyticsPanel from "../components/dashboard/panels/AnalyticsPanel";
import MissionPanel from "../components/dashboard/panels/MissionPanel";
import WorkforcePanel from "../components/dashboard/panels/WorkforcePanel";

import {
  getDashboardSummary,
  getSampleLeads,
  searchBusinesses,
} from "../api";

function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDashboardLoading, setIsDashboardLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      try {
        const [summaryData, leadsData] = await Promise.all([
          getDashboardSummary(),
          getSampleLeads(),
        ]);

        if (!isMounted) {
          return;
        }

        setDashboardSummary(summaryData);
        setLeads(Array.isArray(leadsData) ? leadsData : []);
      } catch (error) {
        console.error("Failed to load dashboard:", error);
      } finally {
        if (isMounted) {
          setIsDashboardLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  async function handleLeadSearch(searchData) {
    try {
      setIsLoading(true);

      const data = await searchBusinesses({
        businessType: searchData.businessType,
        location: searchData.location,
        quantity: searchData.quantity || "20",
      });

      setLeads(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to search businesses:", error);
      alert("Unable to fetch businesses.");
    } finally {
      setIsLoading(false);
    }
  }

  function scrollToSection(sectionId) {
    document
      .getElementById(sectionId)
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  }

  function handleOpenCRM() {
    window.location.href = "/crm";
  }

  function handleGenerateProposal() {
    alert("Proposal Generator will be added in an upcoming sprint.");
  }

  function handleWebsiteAudit() {
    alert("Website Intelligence Center will be added in an upcoming sprint.");
  }

  const topOpportunity = useMemo(() => {
    if (leads.length === 0) {
      return null;
    }

    return [...leads].sort((firstLead, secondLead) => {
      const firstScore =
        firstLead.ai_score ?? firstLead.opportunityScore ?? 0;

      const secondScore =
        secondLead.ai_score ?? secondLead.opportunityScore ?? 0;

      return secondScore - firstScore;
    })[0];
  }, [leads]);

  const kpis = useMemo(() => {
    if (!dashboardSummary?.kpis) {
      return [];
    }

    const summaryKpis = dashboardSummary.kpis;

    return [
      {
        title: "Total Leads",
        value: String(summaryKpis.total_leads ?? 0),
        subtitle: "Saved in CRM",
        color: "#22c55e",
      },
      {
        title: "High Priority",
        value: String(summaryKpis.high_priority_leads ?? 0),
        subtitle: "Best opportunities",
        color: "#f59e0b",
      },
      {
        title: "Qualified",
        value: String(summaryKpis.qualified_leads ?? 0),
        subtitle: "Ready for follow-up",
        color: "#38bdf8",
      },
      {
        title: "Pipeline Value",
        value: `QAR ${Number(
          summaryKpis.pipeline_value ?? 0
        ).toLocaleString("en-US")}`,
        subtitle: `${summaryKpis.won_leads ?? 0} won leads`,
        color: "#8b5cf6",
      },
      {
        title: "AI Score",
        value: `${summaryKpis.ai_score ?? 0}%`,
        subtitle: "Business confidence",
        color: "#22c55e",
      },
    ];
  }, [dashboardSummary]);

  const metrics = (
    <section className="cards">
      {kpis.map((kpi) => (
        <KPICard key={kpi.title} {...kpi} />
      ))}
    </section>
  );

  if (isDashboardLoading) {
    return (
      <main className="dashboard-page">
        <ExecutiveHeader />

        <section className="panel">
          <p>Loading executive dashboard...</p>
        </section>
      </main>
    );
  }

  if (!dashboardSummary) {
    return (
      <main className="dashboard-page">
        <ExecutiveHeader />

        <section className="panel">
          <p>Unable to load the executive dashboard.</p>
        </section>
      </main>
    );
  }

  return (
    <main className="dashboard-page">
      <DashboardLayout
        hero={<ExecutiveHeader />}
        metrics={metrics}
        primary={<ExecutiveBrief />}
        secondary={<OpportunityPanel lead={topOpportunity} />}
        lowerLeft={
          <QuickActions
            onRunMission={() =>
              scrollToSection("mission-control-section")
            }
            onOpenCRM={handleOpenCRM}
            onGenerateProposal={handleGenerateProposal}
            onWebsiteAudit={handleWebsiteAudit}
          />
        }
        lowerRight={
          <ActivityPanel
            activity={dashboardSummary.activity || []}
          />
        }
        fullWidth={
          <>
            <WorkforcePanel />

            <AnalyticsPanel summary={dashboardSummary} />

            <div id="mission-control-section">
              <MissionPanel />
            </div>

            <DashboardResearch
              leads={leads}
              isLoading={isLoading}
              onSearch={handleLeadSearch}
            />
          </>
        }
      />
    </main>
  );
}

export default Dashboard;