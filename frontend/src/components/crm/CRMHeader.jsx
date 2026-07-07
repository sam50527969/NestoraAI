import Button from "../ui/Button";

function CRMHeader({ viewMode, onViewModeChange, onRefresh }) {
  return (
    <div className="crm-page-header">
      <div>
        <p className="eyebrow">Nestora CRM</p>
        <h1>Sales Pipeline</h1>
        <p className="crm-page-subtitle">
          Manage saved businesses, track pipeline stages, add notes, and prepare
          sales follow-ups.
        </p>
      </div>

      <div className="crm-header-actions">
        <div className="view-toggle">
          <button
            type="button"
            className={viewMode === "board" ? "active" : ""}
            onClick={() => onViewModeChange("board")}
          >
            Board
          </button>

          <button
            type="button"
            className={viewMode === "table" ? "active" : ""}
            onClick={() => onViewModeChange("table")}
          >
            Table
          </button>
        </div>

        <Button variant="secondary" onClick={onRefresh}>
          Refresh
        </Button>
      </div>
    </div>
  );
}

export default CRMHeader;