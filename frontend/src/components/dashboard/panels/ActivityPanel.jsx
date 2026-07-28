import RecentActivity from "../RecentActivity";

function ActivityPanel({ activity }) {
  return <RecentActivity items={activity || []} />;
}

export default ActivityPanel;