import DashboardResearch from "../../../components/dashboard/DashboardResearch";

export default function ResearchSection({
  leads,
  isLoading,
  onSearch,
}) {
  return (
    <section className="dashboard-v2-section">
      <DashboardResearch
        leads={leads}
        isLoading={isLoading}
        onSearch={onSearch}
      />
    </section>
  );
}