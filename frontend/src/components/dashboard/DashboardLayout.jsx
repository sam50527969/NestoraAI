export default function DashboardLayout({
  hero,
  metrics,
  primary,
  secondary,
  lowerLeft,
  lowerRight,
  fullWidth,
}) {
  return (
    <div className="executive-dashboard-layout">
      <div className="dashboard-layout-hero">{hero}</div>

      <div className="dashboard-layout-metrics">{metrics}</div>

      <div className="dashboard-layout-grid">
        <div>{primary}</div>
        <div>{secondary}</div>
        <div>{lowerLeft}</div>
        <div>{lowerRight}</div>
      </div>

      {fullWidth && (
        <div className="dashboard-layout-full">{fullWidth}</div>
      )}
    </div>
  );
}