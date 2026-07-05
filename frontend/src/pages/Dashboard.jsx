import { useEffect, useState } from "react";
import DashboardResearch from "../components/dashboard/DashboardResearch";
import DashboardSummaryGrid from "../components/dashboard/DashboardSummaryGrid";
import KPICard from "../components/KPICard";
import {
  getDashboardSummary,
  getSampleLeads,
  searchBusinesses,
} from "../services/api";

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
          title: "New Leads",
          value: dashboardSummary.kpis.new_leads.toString(),
          subtitle: "From dashboard API",
          color: "#22c55e",
        },
        {
          title: "Pipeline Value",
          value: `QAR ${dashboardSummary.kpis.pipeline_value.toLocaleString()}`,
          subtitle: "Estimated revenue",
          color: "#38bdf8",
        },
        {
          title: "Tasks Today",
          value: dashboardSummary.kpis.tasks_today.toString(),
          subtitle: "Pending follow-ups",
          color: "#f59e0b",
        },
        {
          title: "AI Score",
          value: `${dashboardSummary.kpis.ai_score}%`,
          subtitle: "Business confidence",
          color: "#8b5cf6",
        },
      ]
    : [];

  return (
    <>
      <section className="dashboard-header">
        <div>
          <h2>Welcome back, Sam 👋</h2>
          <p>Here is your backend-powered business command center for today.</p>
        </div>
      </section>

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