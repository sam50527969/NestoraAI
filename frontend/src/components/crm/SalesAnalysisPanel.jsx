function SalesAnalysisPanel({ analysis }) {
  if (!analysis) return null;

  return (
    <div className="sales-analysis-panel">
      <div>
        <p className="eyebrow">AI Sales Brain</p>
        <h2>Lead Analysis</h2>
      </div>

      <div className="analysis-score">
        <span>Score</span>
        <strong>{analysis.score}/100</strong>
      </div>

      <div className="analysis-section">
        <h4>Strengths</h4>
        <ul>
          {analysis.strengths.map((item) => (
            <li key={item}>✓ {item}</li>
          ))}
        </ul>
      </div>

      <div className="analysis-section">
        <h4>Weaknesses</h4>
        <ul>
          {analysis.weaknesses.map((item) => (
            <li key={item}>• {item}</li>
          ))}
        </ul>
      </div>

      <div className="analysis-recommendation">
        <h4>Recommended Action</h4>
        <p>{analysis.recommendation}</p>
      </div>
    </div>
  );
}

export default SalesAnalysisPanel;