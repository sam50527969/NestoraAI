import Badge from "../../../components/ui/Badge";

function getStatusVariant(status) {
  switch (status) {
    case "completed":
      return "success";

    case "running":
      return "primary";

    case "failed":
      return "danger";

    case "waiting":
    case "queued":
      return "warning";

    default:
      return "default";
  }
}

export default function AgentCard({
  name,
  role,
  icon,
  status = "idle",
  progress = 0,
  currentTask,
  current_task,
}) {
  const safeProgress = Math.min(
    Math.max(Number(progress) || 0, 0),
    100
  );

  const displayedTask =
    current_task ||
    currentTask ||
    "Waiting for work";

  return (
    <article className="workforce-agent-card">
      <div className="workforce-agent-header">
        <div className="workforce-agent-identity">
          <span className="workforce-agent-icon">
            {icon}
          </span>

          <div>
            <h3>{name}</h3>
            <p>{role}</p>
          </div>
        </div>

        <Badge variant={getStatusVariant(status)}>
          {status}
        </Badge>
      </div>

      <div className="workforce-agent-task">
        <span>Current Task</span>
        <strong>{displayedTask}</strong>
      </div>

      <div className="workforce-agent-progress-header">
        <span>Progress</span>
        <strong>{safeProgress}%</strong>
      </div>

      <div className="workforce-agent-progress-track">
        <div
          className="workforce-agent-progress-fill"
          style={{ width: `${safeProgress}%` }}
        />
      </div>
    </article>
  );
}