import "./WorkforceCard.css";

export default function WorkforceCard({
  executive,
}) {
  if (!executive) {
    return null;
  }

  const {
    name,
    department,
    status,
    current_task,
    task,
    progress,
    missions_today,
    success_rate,
  } = executive;

  const normalizedStatus = String(
    status || "idle",
  ).toLowerCase();

  const displayedTask =
    task
    || current_task
    || "Waiting for assignment...";

  const displayedProgress =
    Number.isFinite(Number(progress))
      ? Number(progress)
      : 0;

  const displayedMissions =
    Number.isFinite(Number(missions_today))
      ? Number(missions_today)
      : 0;

  const displayedSuccessRate =
    Number.isFinite(Number(success_rate))
      ? Number(success_rate)
      : 0;

  return (
    <div
      className={`workforce-card status-${normalizedStatus}`}
    >
      <div className="workforce-header">
        <div>
          <h3>{name || "AI Executive"}</h3>
          <p>{department || "Executive"}</p>
        </div>

        <span
          className={`status-badge ${normalizedStatus}`}
        >
          {status || "Idle"}
        </span>
      </div>

      <div className="task-section">
        <strong>Current Task</strong>

        <p>{displayedTask}</p>
      </div>

      <div className="progress-section">
        <div className="progress-label">
          <span>Progress</span>
          <span>{displayedProgress}%</span>
        </div>

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${Math.min(
                Math.max(displayedProgress, 0),
                100,
              )}%`,
            }}
          />
        </div>
      </div>

      <div className="workforce-footer">
        <div>
          <span>Missions</span>
          <strong>{displayedMissions}</strong>
        </div>

        <div>
          <span>Success</span>
          <strong>
            {displayedSuccessRate}%
          </strong>
        </div>
      </div>
    </div>
  );
}