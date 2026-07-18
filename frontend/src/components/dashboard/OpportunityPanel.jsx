import Badge from "../ui/Badge";
import Card from "../ui/Card";

export default function OpportunityPanel({ lead }) {
  const hasLead = Boolean(lead);

  return (
    <Card className="opportunity-panel">
      <div className="dashboard-card-header">
        <div>
  <p className="eyebrow">Top Opportunity</p>

  <h2 className="opportunity-title">
    {hasLead
      ? lead.name ||
        lead.businessName ||
        "Unnamed Business"
      : "No opportunity available"}
  </h2>
</div>

        <Badge variant={hasLead ? "success" : "default"}>
          {hasLead ? "Recommended" : "Waiting"}
        </Badge>
      </div>

      {hasLead ? (
        <div className="opportunity-panel-content">
          <div className="opportunity-score">
            <span>AI Score</span>
            <strong>{lead.ai_score ?? 0}/100</strong>
          </div>

          <div className="opportunity-detail">
            <span>Category</span>
            <strong>{lead.category || "Unknown"}</strong>
          </div>

          <div className="opportunity-detail">
            <span>Priority</span>
            <strong>{lead.priority || "Medium"}</strong>
          </div>

          <div className="opportunity-recommendation">
            <span>Recommended Action</span>
            <p>
              {lead.ai_recommendation ||
                "Review this lead and prepare a personalized follow-up."}
            </p>
          </div>
        </div>
      ) : (
        <p className="dashboard-empty-copy">
          Run an AI mission or analyze CRM leads to generate a top opportunity.
        </p>
      )}
    </Card>
  );
}