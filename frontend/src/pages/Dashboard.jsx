import { useEffect, useState } from "react";
import LeadSearchForm from "../components/LeadSearchForm";
import KPICard from "../components/KPICard";
import LeadTable from "../components/LeadTable";
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

          <section className="dashboard-grid">
            <div className="panel">
              <p className="eyebrow">AI CEO Brief</p>
              <h2>Today’s Focus</h2>
              <ul className="clean-list">
                {dashboardSummary.ai_brief.map((item) => (
                  <li key={item}>✓ {item}</li>
                ))}
              </ul>
            </div>

            <div className="panel">
              <p className="eyebrow">Tasks</p>
              <h2>Today’s Actions</h2>
              <ul className="clean-list">
                {dashboardSummary.tasks.map((task) => (
                  <li key={task}>□ {task}</li>
                ))}
              </ul>
            </div>

            <div className="panel">
              <p className="eyebrow">Pipeline</p>
              <h2>Lead Stages</h2>
              <div className="pipeline-list">
                {dashboardSummary.pipeline.map((stage) => (
                  <div className="pipeline-row" key={stage.label}>
                    <span>{stage.label}</span>
                    <strong>{stage.value}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <p className="eyebrow">Activity</p>
              <h2>Recent Updates</h2>
              <ul className="clean-list">
                {dashboardSummary.activity.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
          </section>
        </>
      ) : (
        <section className="panel">
          <p>Unable to load dashboard summary.</p>
        </section>
      )}

      <section className="panel">
        <p className="eyebrow">Research Agent</p>
        <h2>Find New Leads</h2>
        <LeadSearchForm onSearch={handleLeadSearch} />
      </section>

      {isLoading ? (
        <section className="panel">
          <p>Searching businesses...</p>
        </section>
      ) : (
        <LeadTable leads={leads} />
      )}
    </>
  );
}

export default Dashboard;