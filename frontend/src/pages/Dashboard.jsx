import StatCard from "../components/StatCard";
import LeadTable from "../components/LeadTable";
import { sampleLeads } from "../data/sampleLeads";

const stats = [
  { label: "New Leads", value: "0", note: "Priority metric" },
  { label: "Today's Revenue", value: "0 QAR", note: "Target: 200 QAR" },
  { label: "Tasks Due Today", value: "0", note: "No overdue tasks" },
];

function Dashboard() {
  return (
    <>
      <section className="cards">
        {stats.map((item) => (
          <StatCard
            key={item.label}
            label={item.label}
            value={item.value}
            note={item.note}
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
      <LeadTable leads={sampleLeads} />
    </>
  );
}

export default Dashboard;