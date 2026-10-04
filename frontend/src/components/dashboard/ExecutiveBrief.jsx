import Card from "../ui/Card";
import Badge from "../ui/Badge";

export default function ExecutiveBrief({
  currency = "",
  pipelineValue = 0,
  brief = [],
}) {
  const statements = Array.isArray(brief)
    ? brief.filter((item) => typeof item === "string" && item.trim())
    : [];

  return (
    <Card className="executive-brief">
      <div className="executive-brief-header">
        <div>
          <p className="eyebrow">Executive Brief</p>
          <h2>Today's Business Summary</h2>
        </div>
        <Badge variant="default">CRM summary</Badge>
      </div>
      <div className="executive-brief-content">
        <div className="brief-item">
          <span>Pipeline Opportunity</span>
          <strong>
            {[currency, Number(pipelineValue || 0).toLocaleString()]
              .filter(Boolean).join(" ")}
          </strong>
        </div>
        <div className="brief-item">
          <span>Workspace summary</span>
          {statements.length ? (
            <ul>{statements.map((statement, index) => (
              <li key={`${index}-${statement}`}>{statement}</li>
            ))}</ul>
          ) : (
            <p>No workspace summary is available.</p>
          )}
        </div>
      </div>
    </Card>
  );
}
