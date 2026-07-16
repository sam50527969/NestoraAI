import Card from "../ui/Card";

export default function RecentActivity({ items = [] }) {
  const activityItems = items.length
    ? items
    : [
        "Mission completed successfully",
        "CRM updated with new leads",
        "AI analysis saved",
        "Outreach drafts generated",
      ];

  return (
    <Card className="recent-activity-panel">
      <div className="dashboard-card-header">
        <div>
          <p className="eyebrow">Activity</p>
          <h2>Recent Updates</h2>
        </div>
      </div>

      <div className="recent-activity-list">
        {activityItems.map((item, index) => (
          <div className="recent-activity-item" key={`${item}-${index}`}>
            <span className="activity-dot" />
            <p>{item}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}