import WorkforceCard from "./WorkforceCard";
import "./WorkforceGrid.css";

export default function WorkforceGrid({
  executives = [],
  connectionStatus = "connecting",
}) {
  if (connectionStatus === "connecting" && executives.length === 0) {
    return (
      <div className="workforce-state">
        <div className="workforce-loader" />
        <p>Connecting to the AI workforce...</p>
      </div>
    );
  }

  if (executives.length === 0) {
    return (
      <div className="workforce-state">
        <h3>No AI executives available</h3>
        <p>The workforce registry has not returned any executives yet.</p>
      </div>
    );
  }

  return (
    <div className="workforce-grid">
      {executives.map((executive, index) => (
        <WorkforceCard
          key={
            executive.id
            ?? executive.key
            ?? executive.name
            ?? index
          }
          executive={executive}
        />
      ))}
    </div>
  );
}