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
  return (
    task.task_uid ||
    task.uid ||
    task.id ||
    ""
  );
}

function getTaskSequence(task, index) {
  return (
    task.sequence_number ??
    task.sequence ??
    task.order ??
    index + 1
  );
}

function getTaskExecutive(task) {
  return (
    task.agent_name ||
    task.executive ||
    task.assigned_to ||
    task.agent ||
    "Unassigned"
  );
}

export default function MissionTaskList({
  tasks = [],
  selectedTask = null,
  loading = false,
  error = "",
  onSelectTask,
  onRefresh,
}) {
  if (loading) {
    return (
      <section className="mission-task-list">
        <div className="mission-task-list-state">
          Loading mission tasks...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mission-task-list">
        <div className="mission-task-list-state error">
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
      <section className="mission-task-list">
        <div className="mission-task-list-state">
          <p>
            No tasks are available for this
            mission.
          </p>

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

  const selectedTaskUid =
    getTaskUid(selectedTask || {});

  function handleKeyDown(event, task) {
    if (
      event.key === "Enter" ||
      event.key === " "
    ) {
      event.preventDefault();
      onSelectTask?.(task);
    }
  }

  return (
    <section className="mission-task-list">
      <div className="mission-task-list-header">
        <div>
          <span className="mission-task-list-eyebrow">
            Execution Plan
          </span>

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
          const sequence =
            getTaskSequence(task, index);
          const taskName = getTaskName(task);
          const executive =
            getTaskExecutive(task);

          const isSelected = taskUid
            ? taskUid === selectedTaskUid
            : task === selectedTask;

          return (
            <article
              key={
                taskUid || `task-${index}`
              }
              className={[
                "mission-task-item",
                `status-${
                  task.status || "unknown"
                }`,
                isSelected
                  ? "is-selected"
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
              role="button"
              tabIndex={0}
              aria-pressed={isSelected}
              onClick={() =>
                onSelectTask?.(task)
              }
              onKeyDown={(event) =>
                handleKeyDown(event, task)
              }
            >
              <div className="mission-task-sequence">
                {sequence}
              </div>

              <div className="mission-task-content">
                <div className="mission-task-top-row">
                  <div>
                    <h3>{taskName}</h3>

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
                      task.status ||
                      "unknown"
                    }`}
                  >
                    {formatTaskStatus(
                      task.status,
                    )}
                  </span>
                </div>

                {task.description &&
                  task.description !==
                    taskName && (
                    <p className="mission-task-description">
                      {task.description}
                    </p>
                  )}

                <div className="mission-task-meta">
                  <span>
                    Executive: {executive}
                  </span>

                  {task.task_type && (
                    <span>
                      Type: {task.task_type}
                    </span>
                  )}

                  {task.attempt_count !=
                    null && (
                    <span>
                      Attempts:{" "}
                      {task.attempt_count}
                    </span>
                  )}
                </div>

                {task.error_message && (
                  <div className="mission-task-error-message">
                    {task.error_message}
                  </div>
                )}

                <span className="mission-task-view-report">
                  {task.status ===
                  "completed"
                    ? "View executive report"
                    : "View task details"}
                </span>
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
      agent_name: PropTypes.string,
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
  selectedTask: PropTypes.object,
  loading: PropTypes.bool,
  error: PropTypes.string,
  onSelectTask: PropTypes.func,
  onRefresh: PropTypes.func,
};