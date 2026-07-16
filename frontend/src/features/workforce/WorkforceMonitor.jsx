import Card from "../../components/ui/Card";
import AgentGrid from "./components/AgentGrid";

import "./styles/workforce.css";

export default function WorkforceMonitor({ agents }) {
  return (
    <Card className="workforce-monitor">
      <div className="workforce-monitor-header">
        <div>
          <p className="eyebrow">AI Workforce</p>
          <h2>Agent Monitor</h2>
          <p>
            Track each AI agent as it researches, analyzes, scores, and saves
            business opportunities.
          </p>
        </div>
      </div>

      <AgentGrid agents={agents} />
    </Card>
  );
}