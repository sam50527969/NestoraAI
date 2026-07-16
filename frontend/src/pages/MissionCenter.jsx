import { useState } from "react";

import Card from "../components/ui/Card";
import MissionControl from "../components/dashboard/MissionControl";
import "../styles/mission-center.css";

export default function MissionCenter() {
  const [mission, setMission] = useState(null);

  return (
    <main className="mission-center-page">
      <Card className="mission-center-header">
        <p className="eyebrow">AI Workforce</p>

        <h1>Mission Center</h1>

        <p>
          Launch autonomous AI missions that research businesses,
          analyze opportunities, enrich CRM records and prepare
          outreach automatically.
        </p>
      </Card>

      <MissionControl
        onMissionChange={setMission}
      />

      <Card>
        <p className="eyebrow">
          Live Mission Activity
        </p>

        <h2>Activity Feed</h2>

        {!mission && (
          <p>
            Start a mission to see live activity.
          </p>
        )}

        {mission?.activity?.length > 0 && (
          <div className="mission-activity-feed">
            {[...mission.activity]
              .reverse()
              .map((item, index) => (
                <div
                  key={index}
                  className="mission-activity-item"
                >
                  <strong>
                    {item.time}
                  </strong>

                  <span>
                    {item.agent}
                  </span>

                  <p>{item.message}</p>
                </div>
              ))}
          </div>
        )}
      </Card>

      <Card>
        <p className="eyebrow">
          Mission Roadmap
        </p>

        <h2>Coming Next</h2>

        <ul className="mission-roadmap-list">
          <li>
            <span className="mission-roadmap-status complete">
              ✓
            </span>
            Live mission progress
          </li>

          <li>
            <span className="mission-roadmap-status complete">
              ✓
            </span>
            Mission activity
          </li>

          <li>
            <span className="mission-roadmap-status planned">
              •
            </span>
            Parallel AI workers
          </li>

          <li>
            <span className="mission-roadmap-status planned">
              •
            </span>
            Pause / Resume
          </li>

          <li>
            <span className="mission-roadmap-status planned">
              •
            </span>
            Mission logs
          </li>

          <li>
            <span className="mission-roadmap-status planned">
              •
            </span>
            AI cost tracking
          </li>
        </ul>
      </Card>
    </main>
  );
}