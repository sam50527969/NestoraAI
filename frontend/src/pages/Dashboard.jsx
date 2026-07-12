import { useEffect, useState } from "react";
import MissionControl from "../components/dashboard/MissionControl";
import DashboardResearch from "../components/dashboard/DashboardResearch";
import DashboardSummaryGrid from "../components/dashboard/DashboardSummaryGrid";
import KPICard from "../components/KPICard";
import CEOChat from "../components/agents/ceo/CEOChat";
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
        setLeads(leadsData);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
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

      setLeads(data);
    } catch (err) {
      console.error(err);
      alert("Unable to fetch businesses.");
    } finally {
      setIsLoading(false);
    }
  }

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

  return (
    <>
      <section className="dashboard-header">
        <div>
          <h2>Welcome back, Sam 👋</h2>
          <p>Here is your live CRM-powered business command center for today.</p>
        </div>
      </section>

      <CEOChat />

      {isDashboardLoading ? (
        <section className="panel">
          <p>Loading dashboard summary...</p>
        </section>
      ) : dashboardSummary ? (
        <>
          <section className="cards">
            {kpis.map((kpi) => (
              <KPICard key={kpi.title} {...kpi} />
            ))}
          </section>

          <DashboardSummaryGrid summary={dashboardSummary} />
          <MissionControl />
        </>
      ) : (
        <section className="panel">
          <p>Unable to load dashboard summary.</p>
        </section>
      )}

      <DashboardResearch
        leads={leads}
        isLoading={isLoading}
        onSearch={handleLeadSearch}
      />
    </>
  );
}

export default Dashboard;