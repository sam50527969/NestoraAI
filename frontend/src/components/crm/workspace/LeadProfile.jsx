function parseStoredList(value) {
  if (!value) return [];

  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function formatAnalyzedAt(value) {
  if (!value) return "Not analyzed yet";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Not analyzed yet";
  }

  return date.toLocaleString();
}

export default function LeadProfile({ lead }) {
  if (!lead) {
    return (
      <div className="crm-v2-empty-profile">
        <p className="eyebrow">AI Sales Workspace</p>
        <h2>No lead selected</h2>
        <p>
          Choose a lead to view its AI score, opportunity, recommendation, and
          analysis history.
        </p>
      </div>
    );
  }

  const strengths = parseStoredList(lead.ai_strengths);
  const weaknesses = parseStoredList(lead.ai_weaknesses);

  return (
    <div className="crm-v2-profile">
      <div className="crm-v2-profile-header">
        <div>
          <p className="eyebrow">AI Sales Workspace</p>
          <h2>{lead.name || "Unknown Business"}</h2>
          <p>
            {lead.category || "Unknown category"} ·{" "}
            {lead.address || "Location unavailable"}
          </p>
        </div>

        <div className="crm-v2-score-card">
          <span>AI Score</span>
          <strong>{lead.ai_score ?? 0}/100</strong>
        </div>
      </div>

      <section className="crm-v2-profile-section">
        <h3>Opportunity</h3>
        <p>{lead.ai_opportunity || "No opportunity analysis stored yet."}</p>
      </section>

      <section className="crm-v2-profile-section">
        <h3>Recommended Action</h3>
        <p>
          {lead.ai_recommendation ||
            "No recommendation has been generated yet."}
        </p>
      </section>

      <div className="crm-v2-insight-grid">
        <section className="crm-v2-profile-section">
          <h3>Strengths</h3>

          {strengths.length ? (
            <ul>
              {strengths.map((item) => (
                <li key={item}>✓ {item}</li>
              ))}
            </ul>
          ) : (
            <p>No strengths stored yet.</p>
          )}
        </section>

        <section className="crm-v2-profile-section">
          <h3>Weaknesses</h3>

          {weaknesses.length ? (
            <ul>
              {weaknesses.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          ) : (
            <p>No weaknesses stored yet.</p>
          )}
        </section>
      </div>

      <section className="crm-v2-profile-section">
        <h3>Contact Details</h3>

        <div className="crm-v2-contact-grid">
          <div>
            <span>Phone</span>
            <strong>{lead.phone || "Not found"}</strong>
          </div>

          <div>
            <span>Website</span>
            <strong>{lead.website || "Not found"}</strong>
          </div>

          <div>
            <span>Priority</span>
            <strong>{lead.priority || "Medium"}</strong>
          </div>

          <div>
            <span>Last AI Analysis</span>
            <strong>{formatAnalyzedAt(lead.ai_analyzed_at)}</strong>
          </div>
        </div>
      </section>
    </div>
  );
}