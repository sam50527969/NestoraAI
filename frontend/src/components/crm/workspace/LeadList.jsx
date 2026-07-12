function getLeadScore(lead) {
  return lead.ai_score ?? 0;
}

function getLeadLocation(lead) {
  return lead.address || lead.location || "Location unavailable";
}

function getPriorityClass(priority) {
  return `priority-${(priority || "medium").toLowerCase()}`;
}

export default function LeadList({
  leads = [],
  selectedLeadId,
  onSelectLead,
}) {
  if (!leads.length) {
    return (
      <div className="crm-v2-empty-list">
        <p className="eyebrow">Lead List</p>
        <h3>No leads found</h3>
        <p>Run an AI mission or save businesses to populate this workspace.</p>
      </div>
    );
  }

  return (
    <div className="crm-v2-list">
      <div className="crm-v2-list-header">
        <div>
          <p className="eyebrow">Lead List</p>
          <h2>{leads.length} Opportunities</h2>
        </div>
      </div>

      <div className="crm-v2-list-items">
        {leads.map((lead) => {
          const isSelected = lead.id === selectedLeadId;

          return (
            <button
              key={lead.id}
              type="button"
              className={`crm-v2-lead-item ${isSelected ? "selected" : ""}`}
              onClick={() => onSelectLead(lead)}
            >
              <div className="crm-v2-lead-main">
                <strong>{lead.name || "Unknown Business"}</strong>
                <span>
                  {lead.category || "Unknown category"} · {getLeadLocation(lead)}
                </span>
              </div>

              <div className="crm-v2-lead-meta">
                <span className={`crm-v2-priority ${getPriorityClass(lead.priority)}`}>
                  {lead.priority || "Medium"}
                </span>

                <span className="crm-v2-score">
                  {getLeadScore(lead)}/100
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}