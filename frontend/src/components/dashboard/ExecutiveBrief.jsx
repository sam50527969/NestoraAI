import Card from "../ui/Card";
import Badge from "../ui/Badge";

export default function ExecutiveBrief() {
  return (
    <Card className="executive-brief">
      <div className="executive-brief-header">
        <div>
          <p className="eyebrow">AI Executive Brief</p>
          <h2>Today's Business Summary</h2>
        </div>

        <Badge variant="success">
          Live
        </Badge>
      </div>

      <div className="executive-brief-content">

        <div className="brief-item">
          <span>Pipeline Opportunity</span>
          <strong>QAR 92,500</strong>
        </div>

        <div className="brief-item">
          <span>Top Lead</span>
          <strong>AI Shami Home</strong>
        </div>

        <div className="brief-item">
          <span>AI Recommendation</span>
          <strong>
            Contact AI Shami Home today.
          </strong>
        </div>

        <div className="brief-item">
          <span>Reason</span>

          <p>
            High AI score, phone available,
            website missing and high sales potential.
          </p>
        </div>

      </div>
    </Card>
  );
}