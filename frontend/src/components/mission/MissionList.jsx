import PropTypes from "prop-types";
import "./MissionList.css";

function formatMissionDate(value) {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatCompactDate(value) {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(date);
}

function formatValue(value) {
  const number = Number(value);

  if (!Number.isFinite(number) || number <= 0) {
    return "Not set";
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(number);
}

function getStatusLabel(status) {
  const normalizedStatus =
    String(status || "").toLowerCase();

  const labels = {
    planned: "Planned",
    pending: "Pending",
    running: "Running",
    completed: "Completed",
    failed: "Failed",
    blocked: "Blocked",
    paused: "Paused",
    skipped: "Skipped",
  };

  return (
    labels[normalizedStatus] ||
    status ||
    "Unknown"
  );
}

function getProgressValue(mission) {
  const explicitProgress = Number(
    mission.progress ??
      mission.progress_percentage ??
      mission.completion_percentage,
  );

  if (Number.isFinite(explicitProgress)) {
    return Math.min(
      100,
      Math.max(0, explicitProgress),
    );
  }

  const status = String(
    mission.status || "",
  ).toLowerCase();

  if (status === "completed") {
    return 100;
  }

  if (status === "running") {
    return 50;
  }

  if (status === "failed") {
    return 100;
  }

  return 0;
}

function getExecutiveLabel(mission) {
  return (
    mission.executive_name ||
    mission.executive ||
    mission.assigned_executive ||
    mission.department ||
    mission.owner ||
    "AI Workforce"
  );
}

function getExecutiveInitial(mission) {
  const label = getExecutiveLabel(mission).trim();

  return label.charAt(0).toUpperCase() || "N";
}

function getDepartmentLabel(mission) {
  return (
    mission.department ||
    mission.category ||
    mission.mission_type ||
    mission.type ||
    "General Operations"
  );
}

function getPriorityLabel(priority) {
  if (!priority) {
    return "Normal";
  }

  return (
    String(priority).charAt(0).toUpperCase() +
    String(priority).slice(1).toLowerCase()
  );
}

function getMissionTitle(mission) {
  return (
    mission.title ||
    mission.name ||
    mission.objective ||
    "Untitled Mission"
  );
}

function getMissionUid(mission) {
  return (
    mission.mission_uid ||
    mission.uid ||
    mission.id ||
    ""
  );
}

export default function MissionList({
  missions = [],
  selectedMissionUid = "",
  loading = false,
  error = "",
  onSelectMission,
  onRefresh,
}) {
  if (loading) {
    return (
      <section className="mission-list-panel">
        <div className="mission-list-state">
          Loading missions...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mission-list-panel">
        <div className="mission-list-state mission-list-error">
          <p>{error}</p>

          {onRefresh && (
            <button
              type="button"
              className="mission-list-refresh-button"
              onClick={onRefresh}
            >
              Try again
            </button>
          )}
        </div>
      </section>
    );
  }

  if (!missions.length) {
    return (
      <section className="mission-list-panel">
        <div className="mission-list-state">
          <p>No persisted missions are available.</p>

          {onRefresh && (
            <button
              type="button"
              className="mission-list-refresh-button"
              onClick={onRefresh}
            >
              Refresh
            </button>
          )}
        </div>
      </section>
    );
  }

  return (
    <section className="mission-list-panel">
      <div className="mission-list-header">
        <div>
          <p className="mission-list-eyebrow">
            Mission Registry
          </p>

          <h2>Persisted Missions</h2>

          <p className="mission-list-count">
            {missions.length} mission
            {missions.length === 1 ? "" : "s"}
          </p>
        </div>

        {onRefresh && (
          <button
            type="button"
            className="mission-list-refresh-button"
            onClick={onRefresh}
          >
            Refresh
          </button>
        )}
      </div>

      <div className="mission-list-items">
        {missions.map((mission) => {
          const missionUid = getMissionUid(mission);

          const isSelected =
            String(missionUid) ===
            String(selectedMissionUid);

          const status = String(
            mission.status || "unknown",
          ).toLowerCase();

          const progress =
            getProgressValue(mission);

          const priority =
            getPriorityLabel(mission.priority);

          return (
            <button
              key={missionUid}
              type="button"
              className={`mission-list-item mission-card status-${status}${
                isSelected ? " selected" : ""
              }`}
              onClick={() =>
                onSelectMission?.(mission)
              }
            >
              <div className="mission-card-accent" />

              <div className="mission-card-header">
                <div className="mission-card-executive">
                  <span className="mission-card-avatar">
                    {getExecutiveInitial(mission)}
                  </span>

                  <div>
                    <p className="mission-card-executive-name">
                      {getExecutiveLabel(mission)}
                    </p>

                    <p className="mission-list-uid">
                      {missionUid}
                    </p>
                  </div>
                </div>

                <span
                  className={`mission-list-status status-${status}`}
                >
                  {getStatusLabel(mission.status)}
                </span>
              </div>

              <div className="mission-card-body">
                <h3>{getMissionTitle(mission)}</h3>

                {mission.description && (
                  <p className="mission-list-description">
                    {mission.description}
                  </p>
                )}
              </div>

              <div className="mission-card-progress-section">
                <div className="mission-card-progress-header">
                  <span>Mission progress</span>
                  <strong>{progress}%</strong>
                </div>

                <div
                  className="mission-card-progress-track"
                  role="progressbar"
                  aria-label={`${getMissionTitle(
                    mission,
                  )} progress`}
                  aria-valuemin="0"
                  aria-valuemax="100"
                  aria-valuenow={progress}
                >
                  <span
                    className={`mission-card-progress-bar status-${status}`}
                    style={{
                      width: `${progress}%`,
                    }}
                  />
                </div>
              </div>

              <div className="mission-card-metrics">
                <div className="mission-card-metric">
                  <span>Priority</span>
                  <strong
                    className={`priority-${String(
                      mission.priority || "normal",
                    ).toLowerCase()}`}
                  >
                    {priority}
                  </strong>
                </div>

                <div className="mission-card-metric">
                  <span>Department</span>
                  <strong>
                    {getDepartmentLabel(mission)}
                  </strong>
                </div>

                <div className="mission-card-metric">
                  <span>Value</span>
                  <strong>
                    {formatValue(
                      mission.estimated_value ??
                        mission.value ??
                        mission.business_value,
                    )}
                  </strong>
                </div>

                <div className="mission-card-metric">
                  <span>Created</span>
                  <strong>
                    {formatCompactDate(
                      mission.created_at ||
                        mission.createdAt,
                    )}
                  </strong>
                </div>
              </div>

              <div className="mission-list-item-footer">
                <span>
                  Updated{" "}
                  {formatMissionDate(
                    mission.updated_at ||
                      mission.updatedAt ||
                      mission.created_at ||
                      mission.createdAt,
                  )}
                </span>

                <span className="mission-card-open-label">
                  Open mission →
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

MissionList.propTypes = {
  missions: PropTypes.arrayOf(
    PropTypes.shape({
      mission_uid: PropTypes.string,
      uid: PropTypes.string,
      id: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      title: PropTypes.string,
      name: PropTypes.string,
      objective: PropTypes.string,
      description: PropTypes.string,
      status: PropTypes.string,
      priority: PropTypes.string,
      progress: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      progress_percentage: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      completion_percentage:
        PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
        ]),
      executive_name: PropTypes.string,
      executive: PropTypes.string,
      assigned_executive: PropTypes.string,
      owner: PropTypes.string,
      department: PropTypes.string,
      category: PropTypes.string,
      mission_type: PropTypes.string,
      type: PropTypes.string,
      estimated_value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      business_value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      created_at: PropTypes.string,
      createdAt: PropTypes.string,
      updated_at: PropTypes.string,
      updatedAt: PropTypes.string,
    }),
  ),
  selectedMissionUid: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  loading: PropTypes.bool,
  error: PropTypes.string,
  onSelectMission: PropTypes.func,
  onRefresh: PropTypes.func,
};