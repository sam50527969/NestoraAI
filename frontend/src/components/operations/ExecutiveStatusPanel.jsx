import { Activity, AlertTriangle, CheckCircle2, Clock3, Radio, RefreshCw, Users } from "lucide-react";
import "./ExecutiveStatusPanel.css";

function formatStatusLabel(status) {
  const normalized = String(status || "idle").trim().toLowerCase();
  const labels = {
    working: "Working", running: "Running", thinking: "Thinking",
    executing: "Executing", reviewing: "Reviewing", waiting: "Waiting",
    paused: "Paused", blocked: "Blocked", error: "Error",
    failed: "Failed", offline: "Offline", idle: "Idle",
  };
  return labels[normalized] || "Idle";
}

function formatLastEvent(value) {
  if (!value) return "No recent event";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "No recent event";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function getStatusIcon(status) {
  const normalized = String(status || "idle").toLowerCase();
  if (["working", "running", "thinking", "executing", "reviewing"].includes(normalized)) {
    return <Activity size={15} strokeWidth={2.2} />;
  }
  if (["waiting", "paused", "blocked"].includes(normalized)) {
    return <Clock3 size={15} strokeWidth={2.2} />;
  }
  if (["error", "failed", "offline"].includes(normalized)) {
    return <AlertTriangle size={15} strokeWidth={2.2} />;
  }
  return <CheckCircle2 size={15} strokeWidth={2.2} />;
}

export default function ExecutiveStatusPanel({
  executives = [],
  summary = {},
  connectionStatus = "connecting",
  lastEventAt = null,
  isLoading = false,
  isRefreshing = false,
  errorMessage = "",
  onRefresh,
}) {
  const isConnected = connectionStatus === "connected";

  return (
    <section className="ops-status-panel">
      <header className="ops-panel-header">
        <div>
          <div className="ops-panel-eyebrow">
            <Users size={15} strokeWidth={2.2} />
            Executive Workforce
          </div>
          <h2>Live Executive Status</h2>
          <p>Realtime activity from Nestora&apos;s executive workforce.</p>
        </div>

        <div className="ops-status-actions">
          <div className={`ops-connection-badge ${isConnected ? "connected" : "disconnected"}`}>
            <Radio size={14} strokeWidth={2.3} />
            <span>{isConnected ? "Live" : connectionStatus}</span>
          </div>

          <button type="button" className="ops-refresh-button" onClick={onRefresh} disabled={isRefreshing}>
            <RefreshCw size={15} className={isRefreshing ? "ops-spin" : ""} />
            Refresh
          </button>
        </div>
      </header>

      <div className="ops-status-summary">
        <article><span>Total</span><strong>{summary.total ?? executives.length}</strong></article>
        <article><span>Active</span><strong>{summary.active ?? 0}</strong></article>
        <article><span>Waiting</span><strong>{summary.waiting ?? 0}</strong></article>
        <article><span>Issues</span><strong>{summary.issues ?? 0}</strong></article>
      </div>

      {errorMessage && (
        <div className="ops-status-error">
          <AlertTriangle size={17} strokeWidth={2.2} />
          <span>{errorMessage}</span>
        </div>
      )}

      {isLoading ? (
        <div className="ops-status-empty">Connecting to executive workforce...</div>
      ) : executives.length === 0 ? (
        <div className="ops-status-empty">No executive status data is available yet.</div>
      ) : (
        <div className="ops-executive-list">
          {executives.map((executive) => (
            <article key={executive.id} className={`ops-executive-row status-${executive.status}`}>
              <div className="ops-executive-main">
                <div className={`ops-executive-icon status-${executive.status}`}>
                  {getStatusIcon(executive.status)}
                </div>
                <div className="ops-executive-copy">
                  <div className="ops-executive-title-row">
                    <strong>{executive.name}</strong>
                    <span>{executive.department}</span>
                  </div>
                  <p>{executive.currentTask}</p>
                </div>
              </div>

              <div className="ops-executive-meta">
                <span className={`ops-executive-status status-${executive.status}`}>
                  {formatStatusLabel(executive.status)}
                </span>
                <small>{executive.progress}% complete</small>
              </div>
            </article>
          ))}
        </div>
      )}

      <footer className="ops-panel-footer">
        Last workforce event: <strong>{formatLastEvent(lastEventAt)}</strong>
      </footer>
    </section>
  );
}