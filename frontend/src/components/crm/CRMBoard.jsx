import CRMColumn from "./CRMColumn";

const STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"];

function CRMBoard({ leads, onSelectLead }) {
  return (
    <div className="crm-board">
      {STAGES.map((stage) => (
        <CRMColumn
          key={stage}
          title={stage}
          leads={leads.filter((lead) => lead.status === stage)}
          onSelectLead={onSelectLead}
        />
      ))}
    </div>
  );
}

export default CRMBoard;