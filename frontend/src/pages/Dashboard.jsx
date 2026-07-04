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
      subtitle: "Loaded from backend",
      color: "#22c55e",
    },
    {
      title: "Today's Revenue",
      value: "0 QAR",
      subtitle: "Target: 200 QAR",
      color: "#38bdf8",
    },
    {
      title: "Tasks Due Today",
      value: "4",
      subtitle: "Follow-ups and outreach",
      color: "#facc15",
    },
    {
      title: "AI Confidence",
      value: "87%",
      subtitle: "High opportunity score",
      color: "#a78bfa",
    },
  ];

  useEffect(() => {
    async function loadLeads() {
      try {
        const data = await getSampleLeads();
        setLeads(data);
      } catch (error) {
        console.error("Failed to load leads:", error);
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
    } catch (error) {
      console.error(error);
      alert("Unable to fetch businesses.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <section className="cards">
        {kpis.map((kpi) => (
          <KPICard key={kpi.title} {...kpi} />
        ))}
      </section>

      <section className="panel">
        <div>
          <p className="eyebrow">CEO Agent</p>
          <h2>Today’s Recommendation</h2>
        </div>
        <p>
          Focus on finding 20 small businesses in Qatar today. Start with cafés,
          salons, bakeries, and car wash businesses. Offer the 99 QAR Starter
          Business Package.
        </p>
        <button className="secondary">Generate Today’s Plan</button>
      </section>

      <LeadSearchForm onSearch={handleLeadSearch} />

      {isLoading ? (
        <section className="panel">
          <p>Searching real businesses...</p>
        </section>
      ) : (
        <LeadTable leads={leads} />
      )}
    </>
  );
}

export default Dashboard;