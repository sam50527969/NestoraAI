import DashboardResearch from "../../../components/dashboard/DashboardResearch";

export default function ResearchSection({
  leads,
  isLoading,
  errorMessage,
  onSearch,
}) {
  return (
    <section className="dashboard-v2-section">
      <DashboardResearch
        leads={leads}
        isLoading={isLoading}
        errorMessage={errorMessage}
        onSearch={onSearch}
      />
    </section>
  );
}