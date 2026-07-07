import { useEffect, useState } from "react";
import Button from "./ui/Button";

const STATUS_OPTIONS = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"];
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

function Field({ label, children }) {
  return (
    <label className="lead-field">
      <span>{label}</span>
      {children}
    </label>
  );
}

export default function LeadDetailsPanel({
  lead,
  onSave,
  onClose,
  isSaving = false,
}) {
  const [formData, setFormData] = useState(createFormState(lead));

  useEffect(() => {
    setFormData(createFormState(lead));
  }, [lead]);

  if (!lead) {
    return (
      <aside className="lead-details-panel empty">
        <p className="eyebrow">Lead Details</p>
        <h3>No lead selected</h3>
        <p>Select a lead from the board or table to view details and use Nestora Copilot.</p>
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
      <div className="lead-profile-card">
        <div>
          <p className="eyebrow">Lead Details</p>
          <h2>{formData.name || "Unknown Business"}</h2>
          <p>{formData.category || "General Business"}</p>
        </div>

        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
      </div>

      <div className="lead-quick-info">
        <div>
          <span>📍 Address</span>
          <strong>{formData.address || "Not available"}</strong>
        </div>

        <div>
          <span>📞 Phone</span>
          <strong>{formData.phone || "Not found"}</strong>
        </div>

        <div>
          <span>🌐 Website</span>
          <strong>{formData.website || "Not found"}</strong>
        </div>
      </div>

      <form className="lead-details-form" onSubmit={handleSubmit}>
        <div className="lead-form-section">
          <h3>Pipeline</h3>

          <div className="form-grid two-columns">
            <Field label="Status">
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
            </Field>

            <Field label="Priority">
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
            </Field>

            <Field label="Assigned To">
              <input
                type="text"
                value={formData.assigned_to}
                onChange={(event) => updateField("assigned_to", event.target.value)}
                placeholder="Example: Sam"
              />
            </Field>

            <Field label="Tags">
              <input
                type="text"
                value={formData.tags}
                onChange={(event) => updateField("tags", event.target.value)}
                placeholder="Example: cafe, hot lead, Doha"
              />
            </Field>
          </div>
        </div>

        <div className="lead-form-section">
          <h3>Follow-up</h3>

          <div className="form-grid two-columns">
            <Field label="Last Contacted">
              <input
                type="date"
                value={formData.last_contacted}
                onChange={(event) =>
                  updateField("last_contacted", event.target.value)
                }
              />
            </Field>

            <Field label="Next Follow-up">
              <input
                type="date"
                value={formData.next_follow_up}
                onChange={(event) =>
                  updateField("next_follow_up", event.target.value)
                }
              />
            </Field>
          </div>
        </div>

        <div className="lead-form-section">
          <h3>Business Info</h3>

          <div className="form-grid two-columns">
            <Field label="Business Name">
              <input
                type="text"
                value={formData.name}
                onChange={(event) => updateField("name", event.target.value)}
              />
            </Field>

            <Field label="Category">
              <input
                type="text"
                value={formData.category}
                onChange={(event) => updateField("category", event.target.value)}
              />
            </Field>

            <Field label="Phone">
              <input
                type="text"
                value={formData.phone}
                onChange={(event) => updateField("phone", event.target.value)}
              />
            </Field>

            <Field label="Website">
              <input
                type="text"
                value={formData.website}
                onChange={(event) => updateField("website", event.target.value)}
              />
            </Field>
          </div>

          <Field label="Address">
            <textarea
              rows="2"
              value={formData.address}
              onChange={(event) => updateField("address", event.target.value)}
            />
          </Field>
        </div>

        <div className="lead-form-section">
          <h3>Notes</h3>

          <Field label="Sales Notes">
            <textarea
              rows="5"
              value={formData.notes}
              onChange={(event) => updateField("notes", event.target.value)}
              placeholder="Add sales notes, conversation history, objections, next action, or AI observations."
            />
          </Field>
        </div>

        <div className="lead-details-actions">
          <Button type="submit" disabled={isSaving}>
            {isSaving ? "Saving..." : "Save Details"}
          </Button>
        </div>
      </form>
    </aside>
  );
}