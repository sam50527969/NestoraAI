import { useMemo } from "react";

import Badge from "../ui/Badge";
import Card from "../ui/Card";
import "./AgentStatus.css";

const DEFAULT_AGENTS = [
  {
    id: "ceo",
    name: "CEO Agent",
    role: "Strategy, planning and executive decisions",
    department: "Executive Office",
    status: "Online",
    activity: "Monitoring business priorities",
  },
  {
    id: "marketing",
    name: "Marketing Executive",
    role: "Campaign strategy and customer acquisition",
    department: "Marketing",
    status: "Idle",
    activity: "Ready for assignment",
  },
  {
    id: "follow-up",
    name: "Follow-up Executive",
    role: "Lead nurturing and customer re-engagement",
    department: "Customer Success",
    status: "Idle",
    activity: "Ready for assignment",
  },
  {
    id: "reception",
    name: "Reception Executive",
    role: "Customer communication and inquiry handling",
    department: "Reception",
    status: "Idle",
    activity: "Ready for assignment",
  },
  {
    id: "finance",
    name: "Finance Executive",
    role: "Financial analysis and business performance",
    department: "Finance",
    status: "Idle",
    activity: "Ready for assignment",
  },
  {
    id: "operations",
    name: "Operations Executive",
    role: "Workflow efficiency and operational planning",
    department: "Operations",
    status: "Idle",
    activity: "Ready for assignment",
  },
  {
    id: "quality-control",
    name: "Quality Control Executive",
    role: "Output validation and quality assurance",
    department: "Quality Control",
    status: "Idle",
    activity: "Ready for assignment",
  },
];

function normalizeStatus(status) {
  return String(status || "Idle").trim().toLowerCase();
}

function getStatusVariant(status) {
  const normalizedStatus = normalizeStatus(status);

  if (
    normalizedStatus === "online" ||
    normalizedStatus === "working" ||
    normalizedStatus === "executing" ||
    normalizedStatus === "reviewing" ||
    normalizedStatus === "completed"
  ) {
    return "success";
  }

  return "default";
}

function isAgentActive(status) {
  const normalizedStatus = normalizeStatus(status);

  return [
    "online",
    "working",
    "executing",
    "reviewing",
  ].includes(normalizedStatus);
}

export default function AgentStatus({
  agents = DEFAULT_AGENTS,
  title = "AI Workforce Monitor",
  subtitle = "Live overview of Nestora's executive agents",
}) {
  const workforceSummary = useMemo(() => {
    const safeAgents = Array.isArray(agents) ? agents : [];

    const activeAgents = safeAgents.filter((agent) =>
      isAgentActive(agent.status)
    ).length;

    const idleAgents = safeAgents.filter(
      (agent) => normalizeStatus(agent.status) === "idle"
    ).length;

    const workingAgents = safeAgents.filter((agent) => {
      const status = normalizeStatus(agent.status);

      return ["working", "executing", "reviewing"].includes(status);
    }).length;

    return {
      total: safeAgents.length,
      active: activeAgents,
      idle: idleAgents,
      working: workingAgents,
    };
  }, [agents]);

  const safeAgents = Array.isArray(agents) ? agents : [];

  return (
    <Card className="agent-status-panel">
      <div className="dashboard-card-header">
        <div>
          <p className="eyebrow">AI Workforce</p>
          <h2>{title}</h2>
          <p className="agent-status-subtitle">{subtitle}</p>
        </div>

        <Badge variant="success">
          {workforceSummary.active} Active
        </Badge>
      </div>

      <div className="agent-status-summary">
        <div className="agent-status-summary-item">
          <span>Total Executives</span>
          <strong>{workforceSummary.total}</strong>
        </div>

        <div className="agent-status-summary-item">
          <span>Currently Working</span>
          <strong>{workforceSummary.working}</strong>
        </div>

        <div className="agent-status-summary-item">
          <span>Available</span>
          <strong>{workforceSummary.idle}</strong>
        </div>
      </div>

      <div className="agent-status-list">
        {safeAgents.length === 0 ? (
          <div className="agent-status-empty">
            <strong>No executives available</strong>
            <span>
              Workforce agents will appear here when they are configured.
            </span>
          </div>
        ) : (
          safeAgents.map((agent) => {
            const status = agent.status || "Idle";
            const active = isAgentActive(status);

            return (
              <div
                className={`agent-status-item ${
                  active ? "agent-status-item-active" : ""
                }`}
                key={agent.id || agent.name}
              >
                <div className="agent-status-identity">
                  <div
                    className={`agent-status-indicator ${
                      active ? "agent-status-indicator-active" : ""
                    }`}
                    aria-hidden="true"
                  />

                  <div className="agent-status-details">
                    <div className="agent-status-name-row">
                      <strong>{agent.name}</strong>

                      {agent.department && (
                        <span className="agent-status-department">
                          {agent.department}
                        </span>
                      )}
                    </div>

                    <span className="agent-status-role">
                      {agent.role}
                    </span>

                    <span className="agent-status-activity">
                      {agent.activity || "Ready for assignment"}
                    </span>
                  </div>
                </div>

                <Badge variant={getStatusVariant(status)}>
                  {status}
                </Badge>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}