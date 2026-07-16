import Button from "../../../components/ui/Button";
import Card from "../../../components/ui/Card";

export default function ExecutiveHero({
  pipelineValue = 0,
  priorityLeads = 0,
  aiConfidence = 0,
  onRunMission,
  onOpenCRM,
  onGenerateProposal,
}) {
  const hour = new Date().getHours();

  let greeting = "Good Evening";

  if (hour < 12) {
    greeting = "Good Morning";
  } else if (hour < 18) {
    greeting = "Good Afternoon";
  }

  return (
    <Card className="dashboard-v2-hero">
      <div className="dashboard-v2-hero-content">
        <p className="eyebrow">Nestora AI</p>

        <h1>{greeting}, Sam 👋</h1>

        <p className="dashboard-v2-hero-copy">
          Your AI has identified today&apos;s highest-value opportunities.
          Review priorities, launch a mission, or continue your sales workflow.
        </p>

        <div className="dashboard-v2-hero-actions">
          <Button onClick={onRunMission}>Run Mission</Button>

          <Button variant="secondary" onClick={onOpenCRM}>
            Open CRM
          </Button>

          <Button variant="secondary" onClick={onGenerateProposal}>
            Generate Proposal
          </Button>
        </div>
      </div>

      <div className="dashboard-v2-hero-stats">
        <div className="dashboard-v2-hero-stat">
          <span>Pipeline</span>
          <strong>QAR {Number(pipelineValue).toLocaleString()}</strong>
        </div>

        <div className="dashboard-v2-hero-stat">
          <span>Priority Leads</span>
          <strong>{priorityLeads}</strong>
        </div>

        <div className="dashboard-v2-hero-stat">
          <span>AI Confidence</span>
          <strong>{aiConfidence}%</strong>
        </div>
      </div>
    </Card>
  );
}