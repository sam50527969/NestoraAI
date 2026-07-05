import { useEffect, useState } from "react";
import LeadSearchForm from "../components/LeadSearchForm";
import KPICard from "../components/KPICard";
import LeadTable from "../components/LeadTable";
import { getSampleLeads, searchBusinesses } from "../services/api";

function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const kpis = [
    {
      title: "New Leads",
      value: leads.length.toString(),
      subtitle: "Saved opportunities",
      color: "#22c55e",
    },
    {
      title: "Pipeline Value",
      value: "QAR 0",
      subtitle: "Estimated revenue",
      color: "#38bdf8",
    },
    {
      title: "Tasks Today",
      value: "4",
      subtitle: "Pending follow-ups",
      color: "#f59e0b",
    },
    {
      title: "AI Score",
      value: "87%",
      subtitle: "Business confidence",
      color: "#8b5cf6",
    },
  ];

  useEffect(() => {
    async function loadLeads() {
      try {
        const data = await getSampleLeads();
        setLeads(data);
      } catch (err) {
        console.error(err);
      }
    }

    loadLeads();
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

  return (
    <>
      <section className="dashboard-header">
        <div>
          <h2>Welcome back, Sam 👋</h2>
          <p>
            Here's an overview of your business activity and AI recommendations.
          </p>
        </div>
      </section>

      <section className="cards">
        {kpis.map((kpi) => (
          <KPICard key={kpi.title} {...kpi} />
        ))}
      </section>

      <section className="panel">
        <div className="table-header">
          <div>
            <p className="eyebrow">AI CEO</p>
            <h2>Today's Recommendation</h2>
          </div>
          <button className="secondary">Generate Plan</button>
        </div>

        <p>
          Prioritize restaurants, cafés, gyms, salons and automotive businesses
          in Doha today. AI estimates these categories have the highest outreach
          potential based on current activity.
        </p>
      </section>

      <LeadSearchForm onSearch={handleLeadSearch} />

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