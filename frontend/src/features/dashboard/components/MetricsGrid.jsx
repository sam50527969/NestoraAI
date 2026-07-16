import KPICard from "../../../components/KPICard";

export default function MetricsGrid({ metrics = [] }) {
  if (!metrics.length) {
    return null;
  }

  return (
    <section className="dashboard-v2-metrics">
      {metrics.map((metric) => (
        <KPICard key={metric.title} {...metric} />
      ))}
    </section>
  );
}