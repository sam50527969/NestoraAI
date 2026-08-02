import PropTypes from "prop-types";
import "./MissionDetails.css";

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function DetailRow({ label, value }) {
  return (
    <div className="mission-detail-row">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

DetailRow.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.node,
};

export default function MissionDetails({ mission }) {
  if (!mission) {
    return (
      <section className="mission-details-panel">
        <div className="mission-details-empty">
          Select a mission to view its details.
        </div>
      </section>
    );
  }

  return (
    <section className="mission-details-panel">
      <div className="mission-details-header">
        <p className="mission-details-eyebrow">
          Mission Overview
        </p>

        <h2>
          {mission.title ||
            mission.name ||
            mission.objective ||
            "Mission"}
        </h2>
      </div>

      <div className="mission-details-grid">
        <DetailRow
          label="Mission UID"
          value={mission.mission_uid}
        />

        <DetailRow
          label="Status"
          value={mission.status}
        />

        <DetailRow
          label="Priority"
          value={mission.priority}
        />

        <DetailRow
          label="Created"
          value={formatDate(mission.created_at)}
        />

        <DetailRow
          label="Updated"
          value={formatDate(mission.updated_at)}
        />

        <DetailRow
          label="Owner"
          value={mission.owner || "CEO"}
        />

        <DetailRow
          label="Category"
          value={mission.category}
        />

        <DetailRow
          label="Objective"
          value={mission.objective}
        />
      </div>

      {mission.description && (
        <>
          <h3>Description</h3>

          <p className="mission-description">
            {mission.description}
          </p>
        </>
      )}
    </section>
  );
}

MissionDetails.propTypes = {
  mission: PropTypes.object,
};