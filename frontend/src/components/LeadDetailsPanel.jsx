import { useEffect, useState } from "react";

const STATUS_OPTIONS = ["New", "Contacted", "Qualified", "Won", "Lost"];
const PRIORITY_OPTIONS = ["Low", "Medium", "High"];

function createFormState(lead) {
  return {
    name: lead?.name || "",
    category: lead?.category || "",
    phone: lead?.phone || "",
    website: lead?.website || "",
    address: lead?.address || "",
    status: lead?.status || "New",
    priority: lead?.priority || "Medium",
    notes: lead?.notes || "",
    tags: lead?.tags || "",
    assigned_to: lead?.assigned_to || "",
    last_contacted: lead?.last_contacted || "",
    next_follow_up: lead?.next_follow_up || "",
  };
}

export default function LeadDetailsPanel({ lead, onSave, onClose, isSaving = false }) {
  const [formData, setFormData] = useState(createFormState(lead));

  useEffect(() => {
    setFormData(createFormState(lead));
  }, [lead]);

  if (!lead) {
    return (
      <aside className="lead-details-panel empty">
        <h3>Lead Details</h3>
        <p>Select a saved lead to view notes, status, priority, tags, and follow-up details.</p>
      </aside>
    );
  }

  const updateField = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSave(lead.id, formData);
  };

  return (
    <aside className="lead-details-panel">
      <div className="lead-details-header">
        <div>
          <p className="eyebrow">Lead Details</p>
          <h2>{lead.name || "Unknown Business"}</h2>
        </div>

        <button type="button" className="secondary-button" onClick={onClose}>
          Close
        </button>
      </div>

      <form className="lead-details-form" onSubmit={handleSubmit}>
        <div className="form-grid two-columns">
          <label>
            Business Name
            <input
              type="text"
              value={formData.name}
              onChange={(event) => updateField("name", event.target.value)}
            />
          </label>

          <label>
            Category
            <input
              type="text"
              value={formData.category}
              onChange={(event) => updateField("category", event.target.value)}
            />
          </label>

          <label>
            Status
            <select
              value={formData.status}
              onChange={(event) => updateField("status", event.target.value)}
            >
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>

          <label>
            Priority
            <select
              value={formData.priority}
              onChange={(event) => updateField("priority", event.target.value)}
            >
              {PRIORITY_OPTIONS.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </label>

          <label>
            Phone
            <input
              type="text"
              value={formData.phone}
              onChange={(event) => updateField("phone", event.target.value)}
            />
          </label>

          <label>
            Website
            <input
              type="text"
              value={formData.website}
              onChange={(event) => updateField("website", event.target.value)}
            />
          </label>

          <label>
            Assigned To
            <input
              type="text"
              value={formData.assigned_to}
              onChange={(event) => updateField("assigned_to", event.target.value)}
              placeholder="Example: Sam"
            />
          </label>

          <label>
            Tags
            <input
              type="text"
              value={formData.tags}
              onChange={(event) => updateField("tags", event.target.value)}
              placeholder="Example: cafe, hot lead, Doha"
            />
          </label>

          <label>
            Last Contacted
            <input
              type="date"
              value={formData.last_contacted}
              onChange={(event) => updateField("last_contacted", event.target.value)}
            />
          </label>

          <label>
            Next Follow-up
            <input
              type="date"
              value={formData.next_follow_up}
              onChange={(event) => updateField("next_follow_up", event.target.value)}
            />
          </label>
        </div>

        <label>
          Address
          <textarea
            rows="2"
            value={formData.address}
            onChange={(event) => updateField("address", event.target.value)}
          />
        </label>

        <label>
          Notes
          <textarea
            rows="5"
            value={formData.notes}
            onChange={(event) => updateField("notes", event.target.value)}
            placeholder="Add sales notes, conversation history, objections, next action, or AI observations."
          />
        </label>

        <div className="lead-details-actions">
          <button type="submit" className="primary-button" disabled={isSaving}>
            {isSaving ? "Saving..." : "Save Details"}
          </button>
        </div>
      </form>
    </aside>
  );
}
