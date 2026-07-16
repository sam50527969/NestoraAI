import Card from "../ui/Card";
import Button from "../ui/Button";
import "./executive-header.css";

export default function ExecutiveHeader() {
  const hour = new Date().getHours();

  let greeting = "Good Evening";

  if (hour < 12) greeting = "Good Morning";
  else if (hour < 18) greeting = "Good Afternoon";

  return (
    <Card className="executive-header">

      <div className="executive-header-left">

        <p className="eyebrow">NESTORA AI</p>

        <h1>{greeting}, Sam 👋</h1>

        <p className="executive-description">
          Your AI has identified today's highest-value opportunities.
          Review priorities, launch new missions, or continue your sales
          workflow.
        </p>

        <div className="executive-actions">
          <Button>Run Mission</Button>

          <Button variant="secondary">
            Open CRM
          </Button>

          <Button variant="secondary">
            Generate Proposal
          </Button>
        </div>

      </div>

      <div className="executive-stats">

        <div className="hero-stat">
          <span>Pipeline</span>
          <strong>QAR 92,500</strong>
        </div>

        <div className="hero-stat">
          <span>Priority Leads</span>
          <strong>8</strong>
        </div>

        <div className="hero-stat">
          <span>AI Confidence</span>
          <strong>91%</strong>
        </div>

      </div>

    </Card>
  );
}