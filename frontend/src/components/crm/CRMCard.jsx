function getPriorityClass(priority) {
  switch (priority) {
    case "High":
      return "priority-high";
    case "Medium":
      return "priority-medium";
    default:
      return "priority-low";
  }
}

function CRMCard({ lead, onSelectLead }) {
  return (
    <button type="button" className="crm-card" onClick={() => onSelectLead(lead)}>
      <div className="crm-card-header">
        <h4>{lead.name}</h4>

        <span className={`badge ${getPriorityClass(lead.priority)}`}>
          {lead.priority || "Medium"}
        </span>
      </div>

      <p className="crm-category">{lead.category || "General Business"}</p>

      <div className="crm-details">
        <p>📞 {lead.phone || "No phone"}</p>
        <p>🌐 {lead.website || "No website"}</p>
      </div>

      <div className="crm-footer">
        <span className="status-chip">{lead.status || "New"}</span>
      </div>
    </button>
  );
}

export default CRMCard;