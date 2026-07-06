import CRMCard from "./CRMCard";

function CRMColumn({ title, leads, onSelectLead }) {
  return (
    <div className="crm-column">
      <div className="crm-column-header">
        <h3>{title}</h3>
        <span>{leads.length}</span>
      </div>

      <div className="crm-column-body">
        {leads.map((lead) => (
          <CRMCard key={lead.id} lead={lead} onSelectLead={onSelectLead} />
        ))}
      </div>
    </div>
  );
}

export default CRMColumn;