import LeadList from "./LeadList";
import LeadProfile from "./LeadProfile";

export default function CRMWorkspace({
  leads = [],
  selectedLead,
  onSelectLead,
}) {
  return (
    <section className="crm-v2-workspace">
      <aside className="crm-v2-lead-list">
        <LeadList
          leads={leads}
          selectedLeadId={selectedLead?.id}
          onSelectLead={onSelectLead}
        />
      </aside>

      <main className="crm-v2-lead-profile">
        <LeadProfile lead={selectedLead} />
      </main>
    </section>
  );
}