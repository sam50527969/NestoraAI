function DashboardSummaryGrid({ summary }) {
  return (
    <section className="executive-dashboard-grid">
      <div className="executive-panel ai-brief-panel">
        <div className="panel-title-row">
          <div>
            <p className="eyebrow">AI CEO Brief</p>
            <h2>Today’s Focus</h2>
          </div>
          <span className="panel-icon">🤖</span>
        </div>

        <ul className="executive-list">
          {summary.ai_brief.map((item) => (
            <li key={item}>✓ {item}</li>
          ))}
        </ul>
      </div>

      <div className="executive-panel">
        <p className="eyebrow">Tasks</p>
        <h2>Today’s Actions</h2>
        <ul className="executive-list">
          {summary.tasks.map((task) => (
            <li key={task}>□ {task}</li>
          ))}
        </ul>
      </div>

      <div className="executive-panel">
        <p className="eyebrow">Pipeline</p>
        <h2>Lead Stages</h2>

        <div className="pipeline-list premium">
          {summary.pipeline.map((stage) => (
            <div className="pipeline-row" key={stage.label}>
              <span>{stage.label}</span>
              <strong>{stage.value}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="executive-panel">
        <p className="eyebrow">Activity</p>
        <h2>Recent Updates</h2>
        <ul className="executive-list muted">
          {summary.activity.map((item) => (
            <li key={item}>• {item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}

export default DashboardSummaryGrid;