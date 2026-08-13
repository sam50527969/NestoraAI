import CRMCard from "./CRMCard";

function CRMColumn({
  title,
  leads,
  onSelectLead,
  onStageChange,
  updatingLeadId,
}) {
  return (
    <div className="crm-column">
      <div className="crm-column-header">
        <h3>{title}</h3>

        <span>{leads.length}</span>
      </div>

      <div className="crm-column-body">
        {leads.length ? (
          leads.map((lead) => (
            <CRMCard
              key={lead.id}
              lead={lead}
              onSelectLead={
                onSelectLead
              }
              onStageChange={
                onStageChange
              }
              isUpdating={
                updatingLeadId ===
                lead.id
              }
            />
          ))
        ) : (
          <div className="crm-column-empty">
            No leads in this stage.
          </div>
        )}
      </div>
    </div>
  );
}

export default CRMColumn;