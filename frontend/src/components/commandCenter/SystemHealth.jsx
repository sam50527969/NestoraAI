import {
  Activity,
  CircleCheck,
  Cpu,
  Radio,
  Server,
  Wifi,
} from "lucide-react";

import "./SystemHealth.css";

const healthItems = [
  {
    label: "API",
    value: "Healthy",
    detail: "FastAPI responding",
    icon: Server,
    status: "healthy",
  },
  {
    label: "WebSocket",
    value: "Connected",
    detail: "Realtime channel active",
    icon: Wifi,
    status: "healthy",
  },
  {
    label: "AI Load",
    value: "Normal",
    detail: "Within operating range",
    icon: Cpu,
    status: "normal",
  },
  {
    label: "Event Stream",
    value: "Live",
    detail: "Receiving workforce events",
    icon: Radio,
    status: "healthy",
  },
];

export default function SystemHealth({
  connectionStatus = "connected",
  lastEventAt = null,
}) {
  const formattedLastEvent = lastEventAt
    ? new Date(lastEventAt).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "Waiting for event";

  return (
    <section className="system-health">
      <header className="system-health-header">
        <div>
          <p>Infrastructure</p>
          <h3>System Health</h3>
        </div>

        <span
          className={`system-health-status ${
            connectionStatus === "connected"
              ? "connected"
              : "disconnected"
          }`}
        >
          <Activity size={13} />
          {connectionStatus}
        </span>
      </header>

      <div className="system-health-list">
        {healthItems.map((item) => {
          const Icon = item.icon;

          const isWebSocket = item.label === "WebSocket";

          const displayedValue = isWebSocket
            ? connectionStatus === "connected"
              ? "Connected"
              : "Offline"
            : item.value;

          const displayedStatus =
            isWebSocket && connectionStatus !== "connected"
              ? "error"
              : item.status;

          return (
            <article
              key={item.label}
              className={`system-health-item ${displayedStatus}`}
            >
              <div className="system-health-icon">
                <Icon size={18} strokeWidth={2.2} />
              </div>

              <div className="system-health-content">
                <span>{item.label}</span>
                <strong>{displayedValue}</strong>
                <small>{item.detail}</small>
              </div>

              <CircleCheck
                className="system-health-check"
                size={18}
                strokeWidth={2.2}
              />
            </article>
          );
        })}
      </div>

      <footer className="system-health-footer">
        <span>Last realtime event</span>
        <strong>{formattedLastEvent}</strong>
      </footer>
    </section>
  );
}