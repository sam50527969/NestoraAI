import PropTypes from "prop-types";
import "./MissionKPICards.css";

function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(
    Number(value) || 0,
  );
}

function formatPercentage(value) {
  return `${Math.round(Number(value) || 0)}%`;
}

function calculateMissionMetrics(missions) {
  const total = missions.length;

  const running = missions.filter(
    (mission) =>
      mission.status === "running",
  ).length;

  const completed = missions.filter(
    (mission) =>
      mission.status === "completed",
  ).length;

  const failed = missions.filter(
    (mission) =>
      mission.status === "failed",
  ).length;

  const finished = completed + failed;

  const successRate =
    finished > 0
      ? (completed / finished) * 100
      : 0;

  const totalEstimatedValue = missions.reduce(
    (totalValue, mission) =>
      totalValue +
      (Number(mission.estimated_value) || 0),
    0,
  );

  return {
    total,
    running,
    completed,
    failed,
    successRate,
    totalEstimatedValue,
  };
}

function KPICard({
  label,
  value,
  description,
  status = "default",
}) {
  return (
    <article
      className={`mission-kpi-card status-${status}`}
    >
      <p className="mission-kpi-label">
        {label}
      </p>

      <strong className="mission-kpi-value">
        {value}
      </strong>

      <p className="mission-kpi-description">
        {description}
      </p>
    </article>
  );
}

KPICard.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]).isRequired,
  description: PropTypes.string.isRequired,
  status: PropTypes.oneOf([
    "default",
    "running",
    "completed",
    "failed",
    "value",
  ]),
};

export default function MissionKPICards({
  missions = [],
  loading = false,
}) {
  if (loading && !missions.length) {
    return (
      <section className="mission-kpi-grid">
        {Array.from({ length: 6 }).map(
          (_, index) => (
            <article
              key={index}
              className="mission-kpi-card mission-kpi-loading"
            >
              <div className="mission-kpi-skeleton short" />
              <div className="mission-kpi-skeleton large" />
              <div className="mission-kpi-skeleton medium" />
            </article>
          ),
        )}
      </section>
    );
  }

  const metrics =
    calculateMissionMetrics(missions);

  return (
    <section className="mission-kpi-grid">
      <KPICard
        label="Total Missions"
        value={formatNumber(metrics.total)}
        description="All persisted missions"
      />

      <KPICard
        label="Running"
        value={formatNumber(metrics.running)}
        description="Currently executing"
        status="running"
      />

      <KPICard
        label="Completed"
        value={formatNumber(metrics.completed)}
        description="Successfully finished"
        status="completed"
      />

      <KPICard
        label="Failed"
        value={formatNumber(metrics.failed)}
        description="Requires attention"
        status="failed"
      />

      <KPICard
        label="Success Rate"
        value={formatPercentage(
          metrics.successRate,
        )}
        description="Completed mission ratio"
        status="completed"
      />

      <KPICard
        label="Estimated Value"
        value={formatNumber(
          metrics.totalEstimatedValue,
        )}
        description="Combined mission value"
        status="value"
      />
    </section>
  );
}

MissionKPICards.propTypes = {
  missions: PropTypes.arrayOf(
    PropTypes.shape({
      status: PropTypes.string,
      estimated_value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
    }),
  ),
  loading: PropTypes.bool,
};