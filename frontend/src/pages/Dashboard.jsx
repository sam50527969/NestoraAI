import LeadSearchForm from "../components/LeadSearchForm";
import KPICard from "../components/KPICard";
import LeadTable from "../components/LeadTable";
import { useState } from "react";
import { sampleLeads } from "../data/sampleLeads";

const kpis = [
  {
    title: "New Leads",
    value: "3",
    subtitle: "Sample leads ready",
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

function Dashboard() {
  const [leads, setLeads] = useState(sampleLeads);

  function handleLeadSearch(searchData) {
  const businessType = searchData.businessType.toLowerCase();
  const location = searchData.location.toLowerCase();
  const quantity = Number(searchData.quantity) || sampleLeads.length;

  const filteredLeads = sampleLeads
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
          <KPICard
            key={kpi.title}
            title={kpi.title}
            value={kpi.value}
            subtitle={kpi.subtitle}
            color={kpi.color}
          />
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