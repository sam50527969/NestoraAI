import { useEffect, useMemo, useState } from "react";

import CEOChat from "../components/agents/ceo/CEOChat";
import AgentStatus from "../components/dashboard/AgentStatus";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import DashboardResearch from "../components/dashboard/DashboardResearch";
import DashboardSummaryGrid from "../components/dashboard/DashboardSummaryGrid";
import ExecutiveBrief from "../components/dashboard/ExecutiveBrief";
import ExecutiveHeader from "../components/dashboard/ExecutiveHeader";
import MissionControl from "../components/dashboard/MissionControl";
import OpportunityPanel from "../components/dashboard/OpportunityPanel";
import QuickActions from "../components/dashboard/QuickActions";
import RecentActivity from "../components/dashboard/RecentActivity";
import KPICard from "../components/KPICard";

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
    async function loadDashboard() {
      try {
        const [summaryData, leadsData] = await Promise.all([
          getDashboardSummary(),
          getSampleLeads(),
        ]);

        setDashboardSummary(summaryData);
        setLeads(Array.isArray(leadsData) ? leadsData : []);
      } catch (error) {
        console.error("Failed to load dashboard:", error);
      } finally {
        setIsDashboardLoading(false);
      }
    }

    loadDashboard();
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
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function handleOpenCRM() {
    window.location.href = "/crm";
  }

  function handleGenerateProposal() {
    alert("Proposal Generator will be added in the upcoming sprint.");
  }

  function handleWebsiteAudit() {
    alert("Website Intelligence Center will be added in the upcoming sprint.");
  }

  const topOpportunity = useMemo(() => {
    if (!leads.length) return null;

    return [...leads].sort(
      (firstLead, secondLead) =>
        (secondLead.ai_score ?? secondLead.opportunityScore ?? 0) -
        (firstLead.ai_score ?? firstLead.opportunityScore ?? 0)
    )[0];
  }, [leads]);

  const kpis = dashboardSummary
    ? [
        {
          title: "Total Leads",
          value: dashboardSummary.kpis.total_leads.toString(),
          subtitle: "Saved in CRM",
          color: "#22c55e",
        },
        {
          title: "High Priority",
          value: dashboardSummary.kpis.high_priority_leads.toString(),
          subtitle: "Best opportunities",
          color: "#f59e0b",
        },
        {
          title: "Qualified",
          value: dashboardSummary.kpis.qualified_leads.toString(),
          subtitle: "Ready for follow-up",
          color: "#38bdf8",
        },
        {
          title: "Pipeline Value",
          value: `QAR ${dashboardSummary.kpis.pipeline_value.toLocaleString()}`,
          subtitle: `${dashboardSummary.kpis.won_leads} won leads`,
          color: "#8b5cf6",
        },
        {
          title: "AI Score",
          value: `${dashboardSummary.kpis.ai_score}%`,
          subtitle: "Business confidence",
          color: "#22c55e",
        },
      ]
    : [];

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
            onRunMission={() => scrollToSection("mission-control-section")}
            onOpenCRM={handleOpenCRM}
            onGenerateProposal={handleGenerateProposal}
            onWebsiteAudit={handleWebsiteAudit}
          />
        }
        lowerRight={
          <RecentActivity items={dashboardSummary.activity || []} />
        }
        fullWidth={
          <>
            <AgentStatus />

            <CEOChat />

            <DashboardSummaryGrid summary={dashboardSummary} />

            <div id="mission-control-section">
              <MissionControl />
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