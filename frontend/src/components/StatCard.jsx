function StatCard({ label, value, note }) {
  return (
    <div className="card">
      <p>{label}</p>
      <h2>{value}</h2>
      <span>{note}</span>
    </div>
  );
}

export default StatCard;