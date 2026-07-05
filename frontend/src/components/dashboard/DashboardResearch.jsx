import LeadSearchForm from "../LeadSearchForm";
import LeadTable from "../LeadTable";

function DashboardResearch({ leads, isLoading, onSearch }) {
  return (
    <>
      <section className="panel">
        <p className="eyebrow">Research Agent</p>
        <h2>Find New Leads</h2>
        <LeadSearchForm onSearch={onSearch} />
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

export default DashboardResearch;