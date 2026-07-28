import PropTypes from "prop-types";

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

function getStatusLabel(status) {
  const labels = {
    planned: "Planned",
    pending: "Pending",
    running: "Running",
    completed: "Completed",
    failed: "Failed",
    blocked: "Blocked",
    paused: "Paused",
  };

  return labels[status] || status || "Unknown";
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
          const missionUid =
            mission.mission_uid ||
            mission.uid ||
            mission.id;

          const isSelected =
            missionUid === selectedMissionUid;

          return (
            <button
              key={missionUid}
              type="button"
              className={`mission-list-item${
                isSelected ? " selected" : ""
              }`}
              onClick={() => onSelectMission?.(mission)}
            >
              <div className="mission-list-item-top">
                <div>
                  <h3>
                    {mission.title ||
                      mission.name ||
                      mission.objective ||
                      "Untitled Mission"}
                  </h3>

                  <p className="mission-list-uid">
                    {missionUid}
                  </p>
                </div>

                <span
                  className={`mission-list-status status-${
                    mission.status || "unknown"
                  }`}
                >
                  {getStatusLabel(mission.status)}
                </span>
              </div>

              {mission.description && (
                <p className="mission-list-description">
                  {mission.description}
                </p>
              )}

              <div className="mission-list-item-footer">
                <span>
                  Priority: {mission.priority || "Normal"}
                </span>

                <span>
                  {formatMissionDate(
                    mission.created_at ||
                      mission.createdAt,
                  )}
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
      created_at: PropTypes.string,
      createdAt: PropTypes.string,
    }),
  ),
  selectedMissionUid: PropTypes.string,
  loading: PropTypes.bool,
  error: PropTypes.string,
  onSelectMission: PropTypes.func,
  onRefresh: PropTypes.func,
};