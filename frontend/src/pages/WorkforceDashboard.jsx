import {
  Activity,
  Radio,
  Sparkles,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import { getPersistedMissions } from "../api/mission";
import ActivityFeed from "../components/commandCenter/ActivityFeed";
import KPIBar from "../components/commandCenter/KPIBar";
import MissionPipeline from "../components/commandCenter/MissionPipeline";
import SystemHealth from "../components/commandCenter/SystemHealth";
import WorkforceGrid from "../components/workforce/WorkforceGrid";
import useWorkforce from "../hooks/useWorkforce";
import useWorkspace from "../workspace/useWorkspace";

import "./WorkforceDashboard.css";

function formatConnectionLabel(status) {
  switch (status) {
    case "connected":
      return "Live";
    case "connecting":
      return "Connecting";
    case "reconnecting":
      return "Reconnecting";
    default:
      return "Offline";
  }
}

export default function WorkforceDashboard() {
  const { activeWorkspace } = useWorkspace();
  const activeBusinessUid =
    activeWorkspace?.business_uid || "";

  const {
    executives,
    connectionStatus,
    lastEventAt,
    workforceSummary,
  } = useWorkforce();

  const [missions, setMissions] = useState([]);
  const [missionsLoading, setMissionsLoading] =
    useState(true);

  const loadMissions = useCallback(async () => {
    setMissionsLoading(true);

    try {
      const response = await getPersistedMissions({
        limit: 100,
        offset: 0,
      });

      setMissions(
        Array.isArray(response?.missions)
          ? response.missions
          : [],
      );
    } catch {
      setMissions([]);
    } finally {
      setMissionsLoading(false);
    }
  }, []);

  useEffect(() => {
    setMissions([]);
    loadMissions();
  }, [activeBusinessUid, loadMissions]);

  const connectionLabel =
    formatConnectionLabel(connectionStatus);

  const isLive = connectionStatus === "connected";

  return (
    <main className="workforce-dashboard">
      <section className="workforce-command-header">
        <div className="workforce-command-copy">
          <div className="workforce-command-eyebrow">
            <Sparkles size={15} strokeWidth={2.2} />
            Executive Operations
          </div>

          <h1>AI Executive Command Center</h1>

          <p>
            Monitor Nestora&apos;s executive workforce,
            active missions, infrastructure, and realtime
            business activity from one operational view.
          </p>
        </div>

        <div
          className={`workforce-live-badge ${
            isLive ? "live" : "offline"
          }`}
        >
          <Radio size={15} strokeWidth={2.3} />

          <span>{connectionLabel}</span>

          <small>Realtime workforce network</small>
        </div>
      </section>

      <KPIBar summary={workforceSummary} />

      <section className="workforce-command-layout">
        <div className="workforce-command-main">
          <section className="workforce-executives-panel">
            <header className="workforce-section-header">
              <div>
                <p>Leadership Team</p>
                <h2>Executive Workforce</h2>
              </div>

              <span>
                <Activity size={14} strokeWidth={2.2} />
                {workforceSummary.active} active now
              </span>
            </header>

            <WorkforceGrid executives={executives} />
          </section>

          <MissionPipeline
            missions={missions}
            loading={missionsLoading}
          />
        </div>

        <aside className="workforce-command-sidebar">
          <ActivityFeed />

          <SystemHealth
            connectionStatus={connectionStatus}
            lastEventAt={lastEventAt}
          />
        </aside>
      </section>
    </main>
  );
}
