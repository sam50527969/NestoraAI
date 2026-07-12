import { useEffect, useState } from "react";
import Button from "../ui/Button";
import { startMission, getMissionStatus } from "../../api";

function MissionControl() {
  const [mission, setMission] = useState(null);
  const [isStarting, setIsStarting] = useState(false);

  useEffect(() => {
    if (!mission?.mission_id) return;
    if (mission.status === "completed" || mission.status === "failed") return;

    const intervalId = setInterval(async () => {
      try {
        const latestMission = await getMissionStatus(mission.mission_id);
        setMission(latestMission);
      } catch (error) {
        console.error("Failed to refresh mission status", error);
      }
    }, 3000);

    return () => clearInterval(intervalId);
  }, [mission?.mission_id, mission?.status]);

  async function handleStartMission() {
    setIsStarting(true);

    try {
      const startedMission = await startMission({
        business_type: "restaurant",
        location: "doha",
        quantity: 5,
        analyze_websites: true,
        generate_outreach: true,
      });

      setMission(startedMission);
    } catch (error) {
      console.error(error);
      alert("Unable to start mission.");
    } finally {
      setIsStarting(false);
    }
  }

  return (
    <section className="executive-panel mission-control">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">AI Workforce</p>
          <h2>Mission Control</h2>
        </div>
        <span className="panel-icon">🤖</span>
      </div>

      <p className="mission-description">
        Start an AI mission to search, analyze, and prepare outreach for new
        business opportunities.
      </p>

      <Button onClick={handleStartMission} disabled={isStarting}>
        {isStarting ? "Starting Mission..." : "▶ Start AI Mission"}
      </Button>

      {mission && (
        <div className="mission-status-card">
          <div>
            <span>Status</span>
            <strong>{mission.status}</strong>
          </div>

          <div>
            <span>Progress</span>
            <strong>{mission.progress}%</strong>
          </div>

          <div>
            <span>Current Step</span>
            <strong>{mission.current_step}</strong>
          </div>

          <div>
            <span>Searched</span>
            <strong>{mission.searched}</strong>
          </div>

          <div>
            <span>Analyzed</span>
            <strong>{mission.analyzed}</strong>
          </div>

          <div>
            <span>Outreach</span>
            <strong>{mission.outreach_generated}</strong>
          </div>

          <div className="mission-progress-bar">
            <div style={{ width: `${mission.progress}%` }} />
          </div>
        </div>
      )}
    </section>
  );
}

export default MissionControl;