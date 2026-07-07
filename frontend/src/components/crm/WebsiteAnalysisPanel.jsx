function WebsiteAnalysisPanel({ analysis }) {
  if (!analysis) return null;

  return (
    <div className="website-analysis-panel">
      <div>
        <p className="eyebrow">Website Intelligence</p>
        <h2>Website Analysis</h2>
      </div>

      <div className="analysis-score">
        <span>Website Score</span>
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
        <h4>Issues</h4>
        <ul>
          {analysis.issues.map((item) => (
            <li key={item}>• {item}</li>
          ))}
        </ul>
      </div>

      <div className="analysis-recommendation">
        <h4>Recommendation</h4>
        <p>{analysis.recommendation}</p>
      </div>
    </div>
  );
}

export default WebsiteAnalysisPanel;