import { useNavigate } from "react-router-dom";

import AgentStatus from "../../components/dashboard/AgentStatus";
import ExecutiveBrief from "../../components/dashboard/ExecutiveBrief";
import OpportunityPanel from "../../components/dashboard/OpportunityPanel";
import QuickActions from "../../components/dashboard/QuickActions";
import RecentActivity from "../../components/dashboard/RecentActivity";
import ExecutiveOperationsCenter from "../../components/operations/ExecutiveOperationsCenter";

import CEOSection from "./components/CEOSection";
import ExecutiveHero from "./components/ExecutiveHero";
import MetricsGrid from "./components/MetricsGrid";
import ResearchSection from "./components/ResearchSection";
import useWorkspace from "../../workspace/useWorkspace";
import useDashboardData from "./hooks/useDashboardData";

import "./styles/dashboard.css";


export default function DashboardV2() {
  const navigate = useNavigate();

  const {
    activeWorkspace,
  } = useWorkspace();

  const businessUid =
    activeWorkspace?.business_uid || "";

  const currency =
    activeWorkspace?.finances?.currency || "";

  const {
    leads,
    dashboardSummary,
    metrics,
    topOpportunity,
    isDashboardLoading,
    isSearching,
    errorMessage,
    searchLeads,
  } = useDashboardData({
    businessUid,
    currency,
  });


  function scrollToMissionControl() {
    document
      .getElementById("dashboard-v2-research")
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  }


  if (isDashboardLoading) {
    return (
      <main className="dashboard-v2-page">
        <section className="dashboard-v2-state">
          Loading executive dashboard...
        </section>
      </main>
    );
  }


  if (errorMessage || !dashboardSummary) {
    return (
      <main className="dashboard-v2-page">
        <section className="dashboard-v2-state dashboard-v2-error">
          {errorMessage
            || "Unable to load the executive dashboard."}
        </section>
      </main>
    );
  }


  const kpis = dashboardSummary.kpis || {};


  return (
    <main className="dashboard-v2-page">
      <ExecutiveHero
        pipelineValue={kpis.pipeline_value}
        currency={currency}
        priorityLeads={kpis.high_priority_leads}
        aiConfidence={kpis.ai_score}
        onRunMission={scrollToMissionControl}
        onOpenCRM={() => navigate("/crm")}
        onGenerateProposal={() =>
          navigate("/proposal")
        }
      />

      <MetricsGrid metrics={metrics} />

      <ExecutiveOperationsCenter />

      <section className="dashboard-v2-grid">
        <ExecutiveBrief
          currency={currency}
          pipelineValue={kpis.pipeline_value}
        />

        <OpportunityPanel
          lead={topOpportunity}
        />

        <QuickActions
          onRunMission={scrollToMissionControl}
          onOpenCRM={() => navigate("/crm")}
          onGenerateProposal={() =>
            navigate("/proposal")
          }
          onWebsiteAudit={() =>
            navigate("/website-intelligence")
          }
        />

        <RecentActivity
          items={
            dashboardSummary.activity || []
          }
        />
      </section>

      <AgentStatus />

      <CEOSection />

      <div id="dashboard-v2-research">
        <ResearchSection
          leads={leads}
          isLoading={isSearching}
          onSearch={searchLeads}
        />
      </div>
    </main>
  );
}