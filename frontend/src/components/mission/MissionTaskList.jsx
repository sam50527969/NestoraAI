import PropTypes from "prop-types";
import "./MissionTaskList.css";

function formatTaskStatus(status) {
  const labels = {
    planned: "Planned",
    pending: "Pending",
    running: "Running",
    completed: "Completed",
    failed: "Failed",
    blocked: "Blocked",
    skipped: "Skipped",
    paused: "Paused",
  };

  return labels[status] || status || "Unknown";
}

function getTaskName(task) {
  return (
    task.title ||
    task.name ||
    task.task_name ||
    task.objective ||
    task.description ||
    "Untitled Task"
  );
}

function getTaskUid(task) {
  return task.task_uid || task.uid || task.id || "";
}

function getTaskSequence(task, index) {
  return (
    task.sequence_number ??
    task.sequence ??
    task.order ??
    index + 1
  );
}

export default function MissionTaskList({
  tasks = [],
  loading = false,
  error = "",
  onRefresh,
}) {
  if (loading) {
    return (
      <section className="mission-task-list-panel">
        <div className="mission-task-list-state">
          Loading mission tasks...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mission-task-list-panel">
        <div className="mission-task-list-state mission-task-list-error">
          <p>{error}</p>

          {onRefresh && (
            <button
              type="button"
              className="mission-task-list-refresh-button"
              onClick={onRefresh}
            >
              Try again
            </button>
          )}
        </div>
      </section>
    );
  }

  if (!tasks.length) {
    return (
      <section className="mission-task-list-panel">
        <div className="mission-task-list-state">
          <p>No tasks are available for this mission.</p>

          {onRefresh && (
            <button
              type="button"
              className="mission-task-list-refresh-button"
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
    <section className="mission-task-list-panel">
      <div className="mission-task-list-header">
        <div>
          <p className="mission-task-list-eyebrow">
            Execution Plan
          </p>

          <h2>Mission Tasks</h2>

          <p className="mission-task-list-count">
            {tasks.length} task
            {tasks.length === 1 ? "" : "s"}
          </p>
        </div>

        {onRefresh && (
          <button
            type="button"
            className="mission-task-list-refresh-button"
            onClick={onRefresh}
          >
            Refresh
          </button>
        )}
      </div>

      <div className="mission-task-list-items">
        {tasks.map((task, index) => {
          const taskUid = getTaskUid(task);
          const sequence = getTaskSequence(task, index);

          return (
            <article
              key={taskUid || `task-${index}`}
              className={`mission-task-item status-${
                task.status || "unknown"
              }`}
            >
              <div className="mission-task-sequence">
                {sequence}
              </div>

              <div className="mission-task-content">
                <div className="mission-task-top-row">
                  <div>
                    <h3>{getTaskName(task)}</h3>

                    {taskUid && (
                      <p
                        className="mission-task-uid"
                        title={String(taskUid)}
                      >
                        {String(taskUid)}
                      </p>
                    )}
                  </div>

                  <span
                    className={`mission-task-status status-${
                      task.status || "unknown"
                    }`}
                  >
                    {formatTaskStatus(task.status)}
                  </span>
                </div>

                {task.description &&
                  task.description !== getTaskName(task) && (
                    <p className="mission-task-description">
                      {task.description}
                    </p>
                  )}

                <div className="mission-task-meta">
                  <span>
                    Executive:{" "}
                    {task.executive ||
                      task.assigned_to ||
                      task.agent ||
                      "Unassigned"}
                  </span>

                  {task.task_type && (
                    <span>
                      Type: {task.task_type}
                    </span>
                  )}

                  {task.attempt_count != null && (
                    <span>
                      Attempts: {task.attempt_count}
                    </span>
                  )}
                </div>

                {task.error_message && (
                  <div className="mission-task-error-message">
                    {task.error_message}
                  </div>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

MissionTaskList.propTypes = {
  tasks: PropTypes.arrayOf(
    PropTypes.shape({
      task_uid: PropTypes.string,
      uid: PropTypes.string,
      id: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
      ]),
      title: PropTypes.string,
      name: PropTypes.string,
      task_name: PropTypes.string,
      objective: PropTypes.string,
      description: PropTypes.string,
      status: PropTypes.string,
      executive: PropTypes.string,
      assigned_to: PropTypes.string,
      agent: PropTypes.string,
      task_type: PropTypes.string,
      sequence_number: PropTypes.number,
      sequence: PropTypes.number,
      order: PropTypes.number,
      attempt_count: PropTypes.number,
      error_message: PropTypes.string,
    }),
  ),
  loading: PropTypes.bool,
  error: PropTypes.string,
  onRefresh: PropTypes.func,
};