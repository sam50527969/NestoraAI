import {
  CheckCircle2,
  CircleAlert,
  Clock3,
  LoaderCircle,
} from "lucide-react";
import PropTypes from "prop-types";

import "./MissionPipeline.css";

export default function MissionPipeline({
  missions = [],
  loading = false,
}) {
  const running = missions.filter(
    (mission) => mission.status === "running",
  ).length;

  const completed = missions.filter(
    (mission) => mission.status === "completed",
  ).length;

  const failed = missions.filter(
    (mission) => mission.status === "failed",
  ).length;

  const pending =
    missions.length - running - completed - failed;

  const pipelineItems = [
    {
      label: "Running",
      value: running,
      icon: LoaderCircle,
      type: "running",
    },
    {
      label: "Pending",
      value: pending,
      icon: Clock3,
      type: "pending",
    },
    {
      label: "Completed",
      value: completed,
      icon: CheckCircle2,
      type: "completed",
    },
    {
      label: "Failed",
      value: failed,
      icon: CircleAlert,
      type: "failed",
    },
  ];

  const total = missions.length;

  return (
    <section className="mission-pipeline">
      <header className="mission-pipeline-header">
        <div>
          <p>Operations</p>
          <h3>Mission Pipeline</h3>
        </div>

        <span>
          {loading && total === 0
            ? "Loading..."
            : `${total} missions`}
        </span>
      </header>

      <div className="mission-pipeline-list">
        {pipelineItems.map((item) => {
          const Icon = item.icon;
          const percentage =
            total > 0
              ? Math.round((item.value / total) * 100)
              : 0;

          return (
            <article
              key={item.label}
              className={`mission-pipeline-item ${item.type}`}
            >
              <div className="mission-pipeline-item-header">
                <div className="mission-pipeline-label">
                  <span className="mission-pipeline-icon">
                    <Icon
                      size={18}
                      strokeWidth={2.2}
                    />
                  </span>

                  <strong>{item.label}</strong>
                </div>

                <span>{item.value}</span>
              </div>

              <div className="mission-pipeline-bar">
                <div
                  className="mission-pipeline-fill"
                  style={{
                    width: `${percentage}%`,
                  }}
                />
              </div>

              <small>{percentage}% of all missions</small>
            </article>
          );
        })}
      </div>
    </section>
  );
}

MissionPipeline.propTypes = {
  missions: PropTypes.arrayOf(
    PropTypes.shape({
      status: PropTypes.string,
    }),
  ),
  loading: PropTypes.bool,
};
