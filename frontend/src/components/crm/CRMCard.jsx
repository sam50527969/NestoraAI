const STAGES = [
  "New",
  "Contacted",
  "Qualified",
  "Won",
  "Lost",
];

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

function CRMCard({
  lead,
  onSelectLead,
  onStageChange,
  isUpdating,
}) {
  const currentStatus =
    lead.status || "New";

  return (
    <article className="crm-card">
      <button
        type="button"
        className="crm-card-content"
        onClick={() =>
          onSelectLead(lead)
        }
      >
        <div className="crm-card-header">
          <h4>{lead.name}</h4>

          <span
            className={`badge ${getPriorityClass(
              lead.priority,
            )}`}
          >
            {lead.priority || "Medium"}
          </span>
        </div>

        <p className="crm-category">
          {lead.category ||
            "General Business"}
        </p>

        <div className="crm-details">
          <p>
            <span>Phone</span>
            {lead.phone || "No phone"}
          </p>

          <p>
            <span>Website</span>
            {lead.website ||
              "No website"}
          </p>
        </div>
      </button>

      <div className="crm-card-footer">
        <label>
          <span>Pipeline Stage</span>

          <select
            value={currentStatus}
            disabled={isUpdating}
            onChange={(event) =>
              onStageChange(
                lead,
                event.target.value,
              )
            }
            aria-label={`Pipeline stage for ${lead.name}`}
          >
            {STAGES.map((stage) => (
              <option
                value={stage}
                key={stage}
              >
                {stage}
              </option>
            ))}
          </select>
        </label>

        {isUpdating && (
          <span className="crm-card-updating">
            Updating...
          </span>
        )}
      </div>
    </article>
  );
}

export default CRMCard;