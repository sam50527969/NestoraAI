import Badge from "../ui/Badge";
import Card from "../ui/Card";

const DEFAULT_AGENTS = [
  {
    name: "CEO Agent",
    role: "Strategy and priorities",
    status: "Ready",
    variant: "success",
  },
  {
    name: "Sales Agent",
    role: "Lead scoring and outreach",
    status: "Ready",
    variant: "success",
  },
  {
    name: "Research Agent",
    role: "Business discovery",
    status: "Ready",
    variant: "success",
  },
  {
    name: "Marketing Agent",
    role: "Campaigns and proposals",
    status: "Idle",
    variant: "default",
  },
];

export default function AgentStatus({ agents = DEFAULT_AGENTS }) {
  return (
    <Card className="agent-status-panel">
      <div className="dashboard-card-header">
        <div>
          <p className="eyebrow">AI Workforce</p>
          <h2>Agent Status</h2>
        </div>
      </div>

      <div className="agent-status-list">
        {agents.map((agent) => (
          <div className="agent-status-item" key={agent.name}>
            <div>
              <strong>{agent.name}</strong>
              <span>{agent.role}</span>
            </div>

            <Badge variant={agent.variant}>
              {agent.status}
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  );
}