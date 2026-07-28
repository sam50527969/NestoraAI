import PropTypes from "prop-types";

function formatEventTime(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

function getEventSymbol(eventType, status) {
  if (status === "failed") {
    return "!";
  }

  if (eventType === "mission_started") {
    return "▶";
  }

  if (eventType === "mission_completed") {
    return "✓";
  }

  if (eventType === "mission_blocked") {
    return "‖";
  }

  if (eventType === "task_started") {
    return "●";
  }

  if (eventType === "task_completed") {
    return "✓";
  }

  return "•";
}

function getStatusLabel(status) {
  const labels = {
    running: "Running",
    completed: "Completed",
    failed: "Failed",
    blocked: "Blocked",
    info: "Info",
  };

  return labels[status] || status || "Info";
}

export default function TimelineEvent({ event, isLast = false }) {
  const metadata = event?.metadata || {};
  const symbol = getEventSymbol(
    event?.event_type,
    event?.status,
  );

  return (
    <article
      className={`mission-timeline-event status-${event?.status || "info"}`}
    >
      <div className="mission-timeline-rail">
        <div className="mission-timeline-marker">
          {symbol}
        </div>

        {!isLast && (
          <div className="mission-timeline-line" />
        )}
      </div>

      <div className="mission-timeline-event-content">
        <div className="mission-timeline-event-header">
          <div>
            <h4 className="mission-timeline-executive">
              {event?.executive || "Nestora"}
            </h4>

            <p className="mission-timeline-message">
              {event?.message || "Mission activity recorded."}
            </p>
          </div>

          <div className="mission-timeline-event-meta">
            <span
              className={`mission-timeline-status status-${event?.status || "info"}`}
            >
              {getStatusLabel(event?.status)}
            </span>

            <time
              className="mission-timeline-time"
              dateTime={event?.created_at || undefined}
            >
              {formatEventTime(event?.created_at)}
            </time>
          </div>
        </div>

        {(metadata.task_uid ||
          metadata.sequence_number ||
          metadata.task_count) && (
          <div className="mission-timeline-details">
            {metadata.sequence_number != null && (
              <span>
                Step {metadata.sequence_number}
              </span>
            )}

            {metadata.task_count != null && (
              <span>
                {metadata.task_count} tasks
              </span>
            )}

            {metadata.task_uid && (
              <span title={metadata.task_uid}>
                Task {metadata.task_uid.slice(0, 8)}
              </span>
            )}
          </div>
        )}
      </div>
    </article>
  );
}

TimelineEvent.propTypes = {
  event: PropTypes.shape({
    event_uid: PropTypes.string,
    executive: PropTypes.string,
    event_type: PropTypes.string,
    status: PropTypes.string,
    message: PropTypes.string,
    created_at: PropTypes.string,
    metadata: PropTypes.shape({
      task_uid: PropTypes.string,
      sequence_number: PropTypes.number,
      task_count: PropTypes.number,
    }),
  }).isRequired,
  isLast: PropTypes.bool,
};