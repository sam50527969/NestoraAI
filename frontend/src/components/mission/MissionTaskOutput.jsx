import PropTypes from "prop-types";
import "./MissionTaskOutput.css";

function parseOutput(value) {
  if (!value) {
    return null;
  }

  if (typeof value === "object") {
    return value;
  }

  if (typeof value === "string") {
    try {
      return JSON.parse(value);
    } catch {
      return {
        result: value,
      };
    }
  }

  return {
    result: value,
  };
}

function humanizeKey(value) {
  return String(value || "")
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

function getExecutive(task) {
  return (
    task?.agent_name ||
    task?.executive ||
    task?.assigned_to ||
    task?.agent ||
    "Executive"
  );
}

function renderPrimitive(value) {
  if (value == null) {
    return "—";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return String(value);
}

function OutputValue({ value, depth = 0 }) {
  if (
    value == null ||
    typeof value !== "object"
  ) {
    return (
      <p className="mission-output-text">
        {renderPrimitive(value)}
      </p>
    );
  }

  if (Array.isArray(value)) {
    if (!value.length) {
      return (
        <p className="mission-output-empty">
          No items
        </p>
      );
    }

    return (
      <div className="mission-output-list">
        {value.map((item, index) => (
          <div
            className="mission-output-list-item"
            key={index}
          >
            <span className="mission-output-list-number">
              {index + 1}
            </span>

            <div>
              <OutputValue
                value={item}
                depth={depth + 1}
              />
            </div>
          </div>
        ))}
      </div>
    );
  }

  const entries = Object.entries(value).filter(
    ([key]) =>
      ![
        "input_data",
        "source_description",
        "reasoning_prompt",
        "experience_reasoning",
        "learning_context",
        "executive_context",
      ].includes(key)
  );

  if (!entries.length) {
    return (
      <p className="mission-output-empty">
        No report data available.
      </p>
    );
  }

  return (
    <div
      className={
        depth === 0
          ? "mission-output-sections"
          : "mission-output-nested"
      }
    >
      {entries.map(([key, item]) => (
        <section
          className="mission-output-section"
          key={key}
        >
          <h4>{humanizeKey(key)}</h4>

          <OutputValue
            value={item}
            depth={depth + 1}
          />
        </section>
      ))}
    </div>
  );
}

OutputValue.propTypes = {
  value: PropTypes.any,
  depth: PropTypes.number,
};

export default function MissionTaskOutput({
  task,
}) {
  if (!task) {
    return (
      <section className="mission-task-output">
        <p className="eyebrow">
          Executive Deliverable
        </p>

        <h2>Executive Report</h2>

        <div className="mission-output-placeholder">
          Select a mission task to inspect the
          executive's saved work.
        </div>
      </section>
    );
  }

  const output = parseOutput(
    task.output_data ||
      task.output ||
      task.result
  );

  return (
    <section className="mission-task-output">
      <div className="mission-output-header">
        <div>
          <p className="eyebrow">
            Executive Deliverable
          </p>

          <h2>{getExecutive(task)} Report</h2>

          <p className="mission-output-task-title">
            {task.title || "Mission Task"}
          </p>
        </div>

        <span
          className={`mission-output-status status-${
            task.status || "unknown"
          }`}
        >
          {task.status || "unknown"}
        </span>
      </div>

      {task.status !== "completed" ? (
        <div className="mission-output-placeholder">
          This executive report will become
          available when the task is completed.
        </div>
      ) : !output ? (
        <div className="mission-output-placeholder">
          This task is completed, but no saved
          output was returned by the task endpoint.
        </div>
      ) : (
        <OutputValue value={output} />
      )}
    </section>
  );
}

MissionTaskOutput.propTypes = {
  task: PropTypes.shape({
    title: PropTypes.string,
    status: PropTypes.string,
    agent_name: PropTypes.string,
    executive: PropTypes.string,
    assigned_to: PropTypes.string,
    agent: PropTypes.string,
    output_data: PropTypes.oneOfType([
      PropTypes.object,
      PropTypes.string,
    ]),
    output: PropTypes.any,
    result: PropTypes.any,
  }),
};