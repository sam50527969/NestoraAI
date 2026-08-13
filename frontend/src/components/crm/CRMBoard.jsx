import CRMColumn from "./CRMColumn";

const STAGES = [
  "New",
  "Contacted",
  "Qualified",
  "Won",
  "Lost",
];

function CRMBoard({
  leads,
  onSelectLead,
  onStageChange,
  updatingLeadId,
}) {
  return (
    <div className="crm-board">
      {STAGES.map((stage) => (
        <CRMColumn
          key={stage}
          title={stage}
          leads={leads.filter(
            (lead) =>
              (lead.status || "New") ===
              stage,
          )}
          onSelectLead={onSelectLead}
          onStageChange={onStageChange}
          updatingLeadId={
            updatingLeadId
          }
        />
      ))}
    </div>
  );
}

export default CRMBoard;