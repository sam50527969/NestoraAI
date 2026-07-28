import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Database,
  ListChecks,
  Loader2,
  RefreshCw,
  Target,
} from "lucide-react";

import "./AdminExplorer.css";


const API_BASE_URL = "http://127.0.0.1:8000";


function formatDate(value) {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


function formatMoney(value) {
  if (value === null || value === undefined) {
    return "Not available";
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(value);
}


function StatusBadge({ value }) {
  const normalizedValue =
    value?.toLowerCase().replaceAll(" ", "_") || "unknown";

  return (
    <span
      className={`admin-badge admin-badge-${normalizedValue}`}
    >
      {value || "Unknown"}
    </span>
  );
}


function PriorityBadge({ value }) {
  const normalizedValue =
    value?.toLowerCase().replaceAll(" ", "_") || "medium";

  return (
    <span
      className={`admin-priority admin-priority-${normalizedValue}`}
    >
      {value || "Medium"}
    </span>
  );
}


function ProgressBar({ progress = 0 }) {
  const safeProgress = Math.max(
    0,
    Math.min(Number(progress) || 0, 100)
  );

  return (
    <div className="admin-progress-wrapper">
      <div className="admin-progress-track">
        <div
          className="admin-progress-fill"
          style={{
            width: `${safeProgress}%`,
          }}
        />
      </div>

      <span>{safeProgress}%</span>
    </div>
  );
}


function parseOutputData(value) {
  if (!value) {
    return null;
  }

  if (typeof value === "object") {
    return value;
  }

  if (typeof value !== "string") {
    return value;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}


function formatOutputLabel(value) {
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase()
    );
}


function OutputValue({ value, depth = 0 }) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return (
      <span style={{ opacity: 0.65 }}>
        Not available
      </span>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return (
        <span style={{ opacity: 0.65 }}>
          None
        </span>
      );
    }

    return (
      <ul
        style={{
          margin: "8px 0 0",
          paddingLeft: "22px",
        }}
      >
        {value.map((item, index) => (
          <li
            key={`${index}-${String(item)}`}
            style={{ marginBottom: "7px" }}
          >
            {typeof item === "object" &&
            item !== null ? (
              <OutputValue
                value={item}
                depth={depth + 1}
              />
            ) : (
              String(item)
            )}
          </li>
        ))}
      </ul>
    );
  }

  if (typeof value === "object") {
    return (
      <div
        style={{
          display: "grid",
          gap: "10px",
          marginTop: depth === 0 ? "12px" : "8px",
        }}
      >
        {Object.entries(value).map(
          ([key, nestedValue]) => (
            <div
              key={key}
              style={{
                padding:
                  depth === 0 ? "12px 14px" : "10px 12px",
                border:
                  "1px solid rgba(148, 163, 184, 0.18)",
                borderRadius: "10px",
                background:
                  depth === 0
                    ? "rgba(15, 23, 42, 0.55)"
                    : "rgba(15, 23, 42, 0.32)",
              }}
            >
              <strong
                style={{
                  display: "block",
                  marginBottom: "5px",
                  fontSize: "0.78rem",
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                  opacity: 0.78,
                }}
              >
                {formatOutputLabel(key)}
              </strong>

              <OutputValue
                value={nestedValue}
                depth={depth + 1}
              />
            </div>
          )
        )}
      </div>
    );
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return <span>{String(value)}</span>;
}


function ExecutiveOutput({ outputData }) {
  const parsedOutput = parseOutputData(outputData);

  if (!parsedOutput) {
    return null;
  }

  return (
    <section
      style={{
        marginTop: "18px",
        padding: "18px",
        border:
          "1px solid rgba(96, 165, 250, 0.22)",
        borderRadius: "14px",
        background:
          "linear-gradient(145deg, rgba(15, 23, 42, 0.82), rgba(30, 41, 59, 0.58))",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "12px",
          marginBottom: "12px",
        }}
      >
        <div>
          <span
            style={{
              display: "block",
              marginBottom: "3px",
              color: "#60a5fa",
              fontSize: "0.75rem",
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
            }}
          >
            AI Executive Output
          </span>

          <strong>Business Report</strong>
        </div>

        <CheckCircle2
          size={20}
          aria-hidden="true"
        />
      </div>

      <OutputValue value={parsedOutput} />
    </section>
  );
}


function AdminExplorer() {
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] =
    useState(null);
  const [tasks, setTasks] = useState([]);

  const [missionsLoading, setMissionsLoading] =
    useState(true);
  const [tasksLoading, setTasksLoading] =
    useState(false);

  const [error, setError] = useState("");
  const [taskError, setTaskError] = useState("");


  const loadTasks = useCallback(async (missionUid) => {
    if (!missionUid) {
      setTasks([]);
      return;
    }

    setTasksLoading(true);
    setTaskError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/missions/${missionUid}/tasks`
      );

      if (!response.ok) {
        const errorPayload = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorPayload?.detail ||
            "Unable to load mission tasks."
        );
      }

      const data = await response.json();

      setTasks(data.tasks || []);
    } catch (requestError) {
      setTasks([]);
      setTaskError(
        requestError.message ||
          "Unable to load mission tasks."
      );
    } finally {
      setTasksLoading(false);
    }
  }, []);


  const loadMissions = useCallback(async () => {
    setMissionsLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/missions?limit=100&offset=0`
      );

      if (!response.ok) {
        const errorPayload = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorPayload?.detail ||
            "Unable to load persisted missions."
        );
      }

      const data = await response.json();
      const loadedMissions = data.missions || [];

      setMissions(loadedMissions);

      setSelectedMission((currentMission) => {
        if (loadedMissions.length === 0) {
          return null;
        }

        const matchingMission = loadedMissions.find(
          (mission) =>
            mission.mission_uid ===
            currentMission?.mission_uid
        );

        return matchingMission || loadedMissions[0];
      });
    } catch (requestError) {
      setMissions([]);
      setSelectedMission(null);
      setTasks([]);

      setError(
        requestError.message ||
          "Unable to load persisted missions."
      );
    } finally {
      setMissionsLoading(false);
    }
  }, []);


  useEffect(() => {
    loadMissions();
  }, [loadMissions]);


  useEffect(() => {
    if (!selectedMission?.mission_uid) {
      setTasks([]);
      return;
    }

    loadTasks(selectedMission.mission_uid);
  }, [selectedMission, loadTasks]);


  const completedTasks = tasks.filter(
    (task) => task.status === "completed"
  ).length;

  const pendingTasks = tasks.filter(
    (task) => task.status === "pending"
  ).length;


  return (
    <div className="admin-explorer">
      <section className="admin-header">
        <div>
          <p className="eyebrow">
            Nestora System Administration
          </p>

          <h1>Admin Explorer</h1>

          <p className="admin-header-description">
            Inspect persisted missions, executive tasks,
            priorities, progress, and database relationships.
          </p>
        </div>

        <button
          className="admin-refresh-button"
          type="button"
          onClick={loadMissions}
          disabled={missionsLoading}
        >
          <RefreshCw
            size={17}
            className={
              missionsLoading ? "admin-spin" : ""
            }
          />

          Refresh
        </button>
      </section>


      <section className="admin-summary-grid">
        <article className="admin-summary-card">
          <div className="admin-summary-icon">
            <Database size={21} />
          </div>

          <div>
            <span>Persisted Missions</span>
            <strong>{missions.length}</strong>
          </div>
        </article>

        <article className="admin-summary-card">
          <div className="admin-summary-icon">
            <ListChecks size={21} />
          </div>

          <div>
            <span>Selected Mission Tasks</span>
            <strong>{tasks.length}</strong>
          </div>
        </article>

        <article className="admin-summary-card">
          <div className="admin-summary-icon">
            <CheckCircle2 size={21} />
          </div>

          <div>
            <span>Completed Tasks</span>
            <strong>{completedTasks}</strong>
          </div>
        </article>

        <article className="admin-summary-card">
          <div className="admin-summary-icon">
            <Target size={21} />
          </div>

          <div>
            <span>Pending Tasks</span>
            <strong>{pendingTasks}</strong>
          </div>
        </article>
      </section>


      {error && (
        <div className="admin-error">
          <AlertCircle size={19} />
          <span>{error}</span>
        </div>
      )}


      <section className="admin-explorer-grid">
        <div className="admin-panel admin-missions-panel">
          <div className="admin-panel-heading">
            <div>
              <p className="eyebrow">Database Records</p>
              <h2>Missions</h2>
            </div>

            <span className="admin-record-count">
              {missions.length} records
            </span>
          </div>


          {missionsLoading ? (
            <div className="admin-empty-state">
              <Loader2
                className="admin-spin"
                size={25}
              />

              <p>Loading persisted missions...</p>
            </div>
          ) : missions.length === 0 ? (
            <div className="admin-empty-state">
              <Database size={28} />

              <h3>No persisted missions</h3>

              <p>
                Create an objective from the CEO Agent to
                generate a mission.
              </p>
            </div>
          ) : (
            <div className="admin-mission-list">
              {missions.map((mission) => {
                const isSelected =
                  selectedMission?.mission_uid ===
                  mission.mission_uid;

                return (
                  <button
                    type="button"
                    key={mission.mission_uid}
                    className={
                      isSelected
                        ? "admin-mission-item selected"
                        : "admin-mission-item"
                    }
                    onClick={() =>
                      setSelectedMission(mission)
                    }
                  >
                    <div className="admin-mission-item-top">
                      <h3>{mission.title}</h3>

                      <StatusBadge
                        value={mission.status}
                      />
                    </div>

                    <p>{mission.objective}</p>

                    <div className="admin-mission-item-meta">
                      <PriorityBadge
                        value={mission.priority}
                      />

                      <span>
                        Value:{" "}
                        {formatMoney(
                          mission.estimated_value
                        )}
                      </span>
                    </div>

                    <ProgressBar
                      progress={mission.progress}
                    />
                  </button>
                );
              })}
            </div>
          )}
        </div>


        <div className="admin-panel admin-details-panel">
          {!selectedMission ? (
            <div className="admin-empty-state">
              <Target size={28} />

              <h3>Select a mission</h3>

              <p>
                Choose a mission to inspect its details and
                executive tasks.
              </p>
            </div>
          ) : (
            <>
              <div className="admin-panel-heading">
                <div>
                  <p className="eyebrow">
                    Mission Details
                  </p>

                  <h2>{selectedMission.title}</h2>
                </div>

                <StatusBadge
                  value={selectedMission.status}
                />
              </div>


              <div className="admin-detail-grid">
                <div className="admin-detail-item">
                  <span>Mission UID</span>
                  <strong>
                    {selectedMission.mission_uid}
                  </strong>
                </div>

                <div className="admin-detail-item">
                  <span>Business UID</span>
                  <strong>
                    {selectedMission.business_uid}
                  </strong>
                </div>

                <div className="admin-detail-item">
                  <span>Priority</span>

                  <PriorityBadge
                    value={selectedMission.priority}
                  />
                </div>

                <div className="admin-detail-item">
                  <span>Estimated Value</span>
                  <strong>
                    {formatMoney(
                      selectedMission.estimated_value
                    )}
                  </strong>
                </div>

                <div className="admin-detail-item">
                  <span>Expected ROI</span>
                  <strong>
                    {selectedMission.expected_roi ??
                      "Not available"}
                  </strong>
                </div>

                <div className="admin-detail-item">
                  <span>Created</span>
                  <strong>
                    {formatDate(
                      selectedMission.created_at
                    )}
                  </strong>
                </div>
              </div>


              <div className="admin-objective-box">
                <span>Objective</span>
                <p>{selectedMission.objective}</p>
              </div>


              {selectedMission.description && (
                <div className="admin-objective-box">
                  <span>Description</span>
                  <p>{selectedMission.description}</p>
                </div>
              )}


              <div className="admin-section-divider">
                <div>
                  <p className="eyebrow">
                    AI Workforce
                  </p>

                  <h2>Executive Tasks</h2>
                </div>

                <span className="admin-record-count">
                  {tasks.length} tasks
                </span>
              </div>


              {taskError && (
                <div className="admin-error">
                  <AlertCircle size={19} />
                  <span>{taskError}</span>
                </div>
              )}


              {tasksLoading ? (
                <div className="admin-empty-state">
                  <Loader2
                    className="admin-spin"
                    size={25}
                  />

                  <p>Loading executive tasks...</p>
                </div>
              ) : tasks.length === 0 ? (
                <div className="admin-empty-state compact">
                  <ListChecks size={27} />

                  <h3>No tasks found</h3>

                  <p>
                    This mission does not currently have any
                    persisted tasks.
                  </p>
                </div>
              ) : (
                <div className="admin-task-list">
                  {tasks.map((task) => (
                    <article
                      className="admin-task-card"
                      key={task.task_uid}
                    >
                      <div className="admin-task-heading">
                        <div>
                          <span className="admin-agent-name">
                            {task.agent_name}
                          </span>

                          <h3>{task.title}</h3>
                        </div>

                        <StatusBadge
                          value={task.status}
                        />
                      </div>

                      <p>{task.description}</p>

                      <div className="admin-task-meta">
                        <PriorityBadge
                          value={task.priority}
                        />

                        <span>
                          Sequence {task.sequence_number}
                        </span>

                        <span>
                          Value:{" "}
                          {formatMoney(
                            task.estimated_value
                          )}
                        </span>
                      </div>

                      <ProgressBar
                        progress={task.progress}
                      />

                      <ExecutiveOutput
                        outputData={task.output_data}
                      />
                    </article>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  );
}


export default AdminExplorer;