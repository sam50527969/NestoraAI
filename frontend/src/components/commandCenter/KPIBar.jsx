import {
  Activity,
  Bot,
 CheckCircle2,
  CircleAlert,
  Clock3,
  Cpu,
} from "lucide-react";

import "./KPIBar.css";

const ICONS = {
  executives: Bot,
  active: Activity,
  waiting: Clock3,
  idle: CheckCircle2,
  errors: CircleAlert,
  load: Cpu,
};

function KPICard({
  icon,
  label,
  value,
  helper,
}) {
  const Icon = icon;

  return (
    <article className="kpi-card">
      <div className="kpi-icon">
        <Icon
          size={20}
          strokeWidth={2.2}
        />
      </div>

      <div className="kpi-content">
        <span>{label}</span>

        <strong>{value}</strong>

        <small>{helper}</small>
      </div>
    </article>
  );
}

export default function KPIBar({
  summary,
}) {
  const aiLoad =
    summary.active === 0
      ? "Low"
      : summary.active < 3
      ? "Normal"
      : "High";

  return (
    <section className="kpi-grid">
      <KPICard
        icon={ICONS.executives}
        label="Executives"
        value={summary.total}
        helper="AI leaders"
      />

      <KPICard
        icon={ICONS.active}
        label="Active"
        value={summary.active}
        helper="Working now"
      />

      <KPICard
        icon={ICONS.waiting}
        label="Waiting"
        value={summary.waiting}
        helper="Awaiting input"
      />

      <KPICard
        icon={ICONS.idle}
        label="Idle"
        value={summary.idle}
        helper="Ready"
      />

      <KPICard
        icon={ICONS.errors}
        label="Errors"
        value={summary.error}
        helper="Need attention"
      />

      <KPICard
        icon={ICONS.load}
        label="AI Load"
        value={aiLoad}
        helper="Realtime estimate"
      />
    </section>
  );
}