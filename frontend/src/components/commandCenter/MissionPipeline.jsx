import {
  CheckCircle2,
  CircleAlert,
  Clock3,
  LoaderCircle,
} from "lucide-react";

import "./MissionPipeline.css";

const pipelineItems = [
  {
    label: "Running",
    value: 4,
    icon: LoaderCircle,
    type: "running",
  },
  {
    label: "Pending",
    value: 11,
    icon: Clock3,
    type: "pending",
  },
  {
    label: "Completed",
    value: 89,
    icon: CheckCircle2,
    type: "completed",
  },
  {
    label: "Failed",
    value: 1,
    icon: CircleAlert,
    type: "failed",
  },
];

export default function MissionPipeline() {
  const total = pipelineItems.reduce(
    (sum, item) => sum + item.value,
    0,
  );

  return (
    <section className="mission-pipeline">
      <header className="mission-pipeline-header">
        <div>
          <p>Operations</p>
          <h3>Mission Pipeline</h3>
        </div>

        <span>{total} missions</span>
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