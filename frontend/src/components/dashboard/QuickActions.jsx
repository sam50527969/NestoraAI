import Button from "../ui/Button";
import Card from "../ui/Card";

export default function QuickActions({
  onRunMission,
  onOpenCRM,
  onGenerateProposal,
  onWebsiteAudit,
}) {
  return (
    <Card className="quick-actions-panel">
      <div className="dashboard-card-header">
        <div>
          <p className="eyebrow">Quick Actions</p>
          <h2>Start Working</h2>
        </div>
      </div>

      <div className="quick-actions-grid">
        <Button onClick={onRunMission} fullWidth>
          Run AI Mission
        </Button>

        <Button variant="secondary" onClick={onOpenCRM} fullWidth>
          Open CRM
        </Button>

        <Button
          variant="secondary"
          onClick={onGenerateProposal}
          fullWidth
        >
          Generate Proposal
        </Button>

        <Button
          variant="secondary"
          onClick={onWebsiteAudit}
          fullWidth
        >
          Audit Website
        </Button>
      </div>
    </Card>
  );
}