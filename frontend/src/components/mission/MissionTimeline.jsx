import PropTypes from "prop-types";

import TimelineEvent from "./TimelineEvent";
import "./MissionTimeline.css";

export default function MissionTimeline({
  missionUid,
  events = [],
  loading = false,
  error = "",
  onRefresh,
}) {
  if (!missionUid) {
    return (
      <section className="mission-timeline-panel">
        <div className="mission-timeline-empty">
          Select a mission to view its execution timeline.
        </div>
      </section>
    );
  }

  if (loading) {
    return (
      <section className="mission-timeline-panel">
        <div className="mission-timeline-loading">
          Loading mission timeline...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mission-timeline-panel">
        <div className="mission-timeline-error">
          <p>{error}</p>

          {onRefresh && (
            <button
              type="button"
              className="mission-timeline-refresh-button"
              onClick={onRefresh}
            >
              Try again
            </button>
          )}
        </div>
      </section>
    );
  }

  if (!events.length) {
    return (
      <section className="mission-timeline-panel">
        <div className="mission-timeline-empty">
          <p>No execution events are available for this mission.</p>

          {onRefresh && (
            <button
              type="button"
              className="mission-timeline-refresh-button"
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
    <section className="mission-timeline-panel">
      <div className="mission-timeline-panel-header">
        <div>
          <p className="mission-timeline-eyebrow">
            AI Workforce Activity
          </p>

          <h3>Mission Timeline</h3>

          <p className="mission-timeline-subtitle">
            {events.length} recorded event
            {events.length === 1 ? "" : "s"}
          </p>
        </div>

        {onRefresh && (
          <button
            type="button"
            className="mission-timeline-refresh-button"
            onClick={onRefresh}
          >
            Refresh
          </button>
        )}
      </div>

      <div className="mission-timeline-list">
        {events.map((event, index) => (
          <TimelineEvent
            key={event.event_uid || `${event.event_type}-${index}`}
            event={event}
            isLast={index === events.length - 1}
          />
        ))}
      </div>
    </section>
  );
}

MissionTimeline.propTypes = {
  missionUid: PropTypes.string,
  events: PropTypes.arrayOf(
    PropTypes.shape({
      event_uid: PropTypes.string,
      event_type: PropTypes.string,
    }),
  ),
  loading: PropTypes.bool,
  error: PropTypes.string,
  onRefresh: PropTypes.func,
};