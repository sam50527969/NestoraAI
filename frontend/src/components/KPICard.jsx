function KPICard({ title, value, subtitle, color }) {
  return (
    <div
      style={{
        background: "#111827",
        borderRadius: "16px",
        padding: "22px",
        border: "1px solid #1f2937",
      }}
    >
      <p
        style={{
          color: "#94a3b8",
          fontSize: "14px",
          marginBottom: "12px",
        }}
      >
        {title}
      </p>

      <h2
        style={{
          color: color || "#ffffff",
          fontSize: "34px",
          marginBottom: "8px",
        }}
      >
        {value}
      </h2>

      <p
        style={{
          color: "#64748b",
          fontSize: "13px",
        }}
      >
        {subtitle}
      </p>
    </div>
  );
}

export default KPICard;