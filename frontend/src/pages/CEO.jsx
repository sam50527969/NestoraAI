import { useEffect, useState } from "react";

import CEOChat from "../components/agents/ceo/CEOChat";
import Badge from "../components/ui/Badge";
import Card from "../components/ui/Card";
import { getCEOBrief } from "../api";

import "../styles/ceo.css";

export default function CEO() {
  const [brief, setBrief] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadBrief() {
      try {
        setErrorMessage("");
        setBrief(await getCEOBrief());
      } catch (error) {
        console.error("Unable to load CEO brief:", error);
        setErrorMessage("Unable to load the executive brief.");
      } finally {
        setIsLoading(false);
      }
    }

    loadBrief();
  }, []);

  return (
    <main className="ceo-page">
      <Card className="ceo-page-header">
        <div>
          <p className="eyebrow">AI Executive</p>
          <h1>CEO Advisor</h1>
          <p>
            Review your CRM position, strongest opportunities, and recommended
            next actions.
          </p>
        </div>

        <Badge variant="success">Live</Badge>
      </Card>

      {isLoading ? (
        <Card>
          <p>Loading executive brief...</p>
        </Card>
      ) : errorMessage ? (
        <Card className="ceo-error-card">
          <p>{errorMessage}</p>
        </Card>
      ) : (
        <>
          <Card className="ceo-summary-card">
            <p className="eyebrow">Executive Summary</p>
            <h2>Current Position</h2>
            <p>{brief?.summary}</p>
          </Card>

          <section className="ceo-page-grid">
            <Card>
              <p className="eyebrow">Priority Leads</p>
              <h2>Top Opportunities</h2>

              <div className="ceo-priority-list">
                {(brief?.priority || []).map((lead) => (
                  <div className="ceo-priority-item" key={lead.name}>
                    <div>
                      <strong>{lead.name}</strong>
                      <span>{lead.priority} priority</span>
                    </div>

                    <Badge variant="primary">
                      {lead.score}/100
                    </Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <p className="eyebrow">Recommended Actions</p>
              <h2>What to Do Next</h2>

              <div className="ceo-recommendation-list">
                {(brief?.recommendations || []).map((recommendation) => (
                  <div
                    className="ceo-recommendation-item"
                    key={recommendation}
                  >
                    <span>✓</span>
                    <p>{recommendation}</p>
                  </div>
                ))}
              </div>
            </Card>
          </section>
        </>
      )}

      <CEOChat />
    </main>
  );
}