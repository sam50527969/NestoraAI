import {
  Bot,
  Search,
  Globe,
  DollarSign,
  CalendarClock,
  CheckCircle2,
  AlertTriangle,
  PlayCircle,
  PauseCircle,
  Wifi,
  WifiOff,
} from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
} from "react";

import workforceSocket from "../../realtime/workforceSocket";
import "./ActivityFeed.css";

const MAX_EVENTS = 50;

function getEventIcon(event) {
  const eventType =
    event.event_type?.toLowerCase() || "";

  const executive =
    event.executive?.toLowerCase() || "";

  if (
    eventType.includes("failed") ||
    event.status === "failed"
  ) {
    return AlertTriangle;
  }

  if (
    eventType.includes("completed") ||
    event.status === "completed"
  ) {
    return CheckCircle2;
  }

  if (
    eventType.includes("blocked") ||
    event.status === "blocked"
  ) {
    return PauseCircle;
  }

  if (
    eventType.includes("started") ||
    event.status === "running"
  ) {
    return PlayCircle;
  }

  if (
    executive.includes("sales") ||
    executive.includes("research")
  ) {
    return Search;
  }

  if (
    executive.includes("marketing") ||
    executive.includes("website")
  ) {
    return Globe;
  }

  if (executive.includes("finance")) {
    return DollarSign;
  }

  if (
    executive.includes("reception") ||
    executive.includes("follow")
  ) {
    return CalendarClock;
  }

  return Bot;
}

function formatEventTime(value) {
  if (!value) {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const parsedDate = new Date(value);

  if (Number.isNaN(parsedDate.getTime())) {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return parsedDate.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normalizeMissionEvent(message) {
  if (
    !message ||
    message.event !== "mission.event" ||
    !message.data
  ) {
    return null;
  }

  const event = message.data;

  return {
    id:
      event.event_uid ||
      `${event.mission_uid}-${event.event_type}-${Date.now()}`,
    executive: event.executive || "Nestora AI",
    title:
      event.message ||
      `${event.executive || "Nestora AI"} updated a mission.`,
    time: formatEventTime(
      event.created_at || message.timestamp,
    ),
    event_type:
      event.event_type || "mission_event",
    status: event.status || "info",
    mission_uid: event.mission_uid || null,
    metadata: event.metadata || {},
  };
}

export default function ActivityFeed() {
  const [events, setEvents] = useState([]);
  const [connectionStatus, setConnectionStatus] =
    useState(
      workforceSocket.connected
        ? "connected"
        : "connecting",
    );

  const activityListRef = useRef(null);

  useEffect(() => {
    const unsubscribe =
      workforceSocket.subscribe((message) => {
        if (message.event === "socket.connected") {
          setConnectionStatus("connected");
          return;
        }

        if (
          message.event === "socket.disconnected"
        ) {
          setConnectionStatus("disconnected");
          return;
        }

        const normalizedEvent =
          normalizeMissionEvent(message);

        if (!normalizedEvent) {
          return;
        }

        setEvents((currentEvents) => {
          const eventAlreadyExists =
            currentEvents.some(
              (event) =>
                event.id === normalizedEvent.id,
            );

          if (eventAlreadyExists) {
            return currentEvents;
          }

          return [
            ...currentEvents,
            normalizedEvent,
          ].slice(-MAX_EVENTS);
        });
      });

    workforceSocket.connect();

    if (workforceSocket.connected) {
      setConnectionStatus("connected");
    }

    return unsubscribe;
  }, []);

  useEffect(() => {
    const activityList =
      activityListRef.current;

    if (!activityList) {
      return;
    }

    activityList.scrollTop =
      activityList.scrollHeight;
  }, [events]);

  const isConnected =
    connectionStatus === "connected";

  const StatusIcon = isConnected
    ? Wifi
    : WifiOff;

  return (
    <section className="activity-feed">
      <header className="activity-header">
        <div>
          <p>Realtime</p>
          <h3>AI Activity Feed</h3>
        </div>

        <span>
          <StatusIcon
            size={13}
            strokeWidth={2.3}
          />

          {isConnected
            ? " LIVE"
            : connectionStatus === "connecting"
              ? " CONNECTING"
              : " OFFLINE"}
        </span>
      </header>

      <div
        ref={activityListRef}
        className="activity-list"
      >
        {events.length === 0 ? (
          <div className="activity-item">
            <div className="activity-icon">
              <Bot
                size={18}
                strokeWidth={2.2}
              />
            </div>

            <div className="activity-content">
              <strong>
                {isConnected
                  ? "Waiting for mission activity..."
                  : "Connecting to Nestora realtime..."}
              </strong>

              <small>
                Run a mission to see live executive
                updates.
              </small>
            </div>
          </div>
        ) : (
          events.map((event) => {
            const Icon = getEventIcon(event);

            return (
              <div
                key={event.id}
                className="activity-item"
              >
                <div className="activity-icon">
                  <Icon
                    size={18}
                    strokeWidth={2.2}
                  />
                </div>

                <div className="activity-content">
                  <strong>
                    {event.executive}:{" "}
                    {event.title}
                  </strong>

                  <small>{event.time}</small>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}