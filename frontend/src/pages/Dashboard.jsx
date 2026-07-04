import LeadSearchForm from "../components/LeadSearchForm";
import KPICard from "../components/KPICard";
import LeadTable from "../components/LeadTable";
import { useEffect, useState } from "react";


function Dashboard() {
  const [allLeads, setAllLeads] = useState([]);
  const [leads, setLeads] = useState([]);
  
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
        const response = await fetch("http://127.0.0.1:8000/leads");
        const data = await response.json();
        setAllLeads(data);
        setLeads(data);
      } catch (error) {
        console.error("Failed to load leads:", error);
      }
    }

    loadLeads();
  }, []);

  function handleLeadSearch(searchData) {
    const businessType = searchData.businessType.toLowerCase();
    const location = searchData.location.toLowerCase();
    const quantity = Number(searchData.quantity) || allLeads.length;

    const filteredLeads = allLeads
      .filter((lead) => {
        const matchesCategory = lead.category.toLowerCase().includes(businessType);
        const matchesLocation = lead.location.toLowerCase().includes(location);
        return matchesCategory && matchesLocation;
      })
      .slice(0, quantity);

    setLeads(filteredLeads);
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
      <LeadTable leads={leads} />
    </>
  );
}

export default Dashboard;