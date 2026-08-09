import {
  useCallback,
  useEffect,
  useState,
} from "react";

import CEOApprovalQueue from "../components/agents/ceo/CEOApprovalQueue";
import CEOChat from "../components/agents/ceo/CEOChat";
import Badge from "../components/ui/Badge";
import Card from "../components/ui/Card";
import { getCEOBrief } from "../api";

import "../styles/ceo.css";

function formatNumber(value) {
  return new Intl.NumberFormat(
    "en-US",
  ).format(Number(value) || 0);
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "QAR",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-US",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}

function truncateText(
  value,
  maxLength = 240,
) {
  const text = String(value || "").trim();

  if (text.length <= maxLength) {
    return text;
  }

  return `${text
    .slice(0, maxLength)
    .trim()}…`;
}

export default function CEO() {
  const [brief, setBrief] = useState(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");

  const loadBrief = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await getCEOBrief();
      setBrief(response);
    } catch (error) {
      console.error(
        "Unable to load CEO brief:",
        error,
      );

      setErrorMessage(
        "Unable to load the executive brief.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBrief();
  }, [loadBrief]);

  const missionOverview =
    brief?.mission_overview || {};

  const executiveReports =
    brief?.executive_reports || [];

  const priorityLeads =
    brief?.priority || [];

  const recommendations =
    brief?.recommendations || [];

  return (
    <main className="ceo-page">
      <Card className="ceo-page-header">
        <div>
          <p className="eyebrow">
            Autonomous Executive Intelligence
          </p>

          <h1>CEO Agent</h1>

          <p>
            Review company performance,
            mission execution, executive
            deliverables, priority
            opportunities, and recommended
            decisions.
          </p>
        </div>

        <div className="ceo-header-actions">
          <Badge variant="success">
            Live
          </Badge>

          <button
            type="button"
            className="ceo-refresh-button"
            onClick={loadBrief}
            disabled={isLoading}
          >
            {isLoading
              ? "Refreshing..."
              : "Refresh Brief"}
          </button>
        </div>
      </Card>

      {isLoading ? (
        <Card className="ceo-state-card">
          <p>
            Building the executive brief...
          </p>
        </Card>
      ) : errorMessage ? (
        <Card className="ceo-error-card">
          <p>{errorMessage}</p>

          <button
            type="button"
            className="ceo-refresh-button"
            onClick={loadBrief}
          >
            Try Again
          </button>
        </Card>
      ) : (
        <>
          <Card className="ceo-summary-card">
            <div className="ceo-section-heading">
              <div>
                <p className="eyebrow">
                  Executive Summary
                </p>

                <h2>Current Position</h2>
              </div>

              {brief?.generated_at && (
                <span className="ceo-generated-at">
                  Updated{" "}
                  {formatDate(
                    brief.generated_at,
                  )}
                </span>
              )}
            </div>

            <p>{brief?.summary}</p>
          </Card>

          <section className="ceo-kpi-grid">
            <Card className="ceo-kpi-card">
              <span>Total Missions</span>

              <strong>
                {formatNumber(
                  missionOverview.total,
                )}
              </strong>

              <small>
                {formatNumber(
                  missionOverview.running,
                )}{" "}
                currently active
              </small>
            </Card>

            <Card className="ceo-kpi-card success">
              <span>
                Completed Missions
              </span>

              <strong>
                {formatNumber(
                  missionOverview.completed,
                )}
              </strong>

              <small>
                {formatNumber(
                  missionOverview.average_progress,
                )}
                % average progress
              </small>
            </Card>

            <Card className="ceo-kpi-card">
              <span>Mission Value</span>

              <strong>
                {formatCurrency(
                  missionOverview.total_estimated_value,
                )}
              </strong>

              <small>
                Combined estimated value
              </small>
            </Card>

            <Card className="ceo-kpi-card">
              <span>
                CRM Opportunities
              </span>

              <strong>
                {formatNumber(
                  brief?.unique_leads,
                )}
              </strong>

              <small>
                {formatNumber(
                  brief?.high_priority_count,
                )}{" "}
                high priority
              </small>
            </Card>
          </section>

          <CEOApprovalQueue />

          <section className="ceo-page-grid">
            <Card className="ceo-reports-card">
              <div className="ceo-section-heading">
                <div>
                  <p className="eyebrow">
                    Executive Deliverables
                  </p>

                  <h2>
                    Latest Executive Reports
                  </h2>
                </div>

                <Badge variant="primary">
                  {executiveReports.length}
                </Badge>
              </div>

              {executiveReports.length ? (
                <div className="ceo-report-list">
                  {executiveReports.map(
                    (report) => (
                      <article
                        className="ceo-report-item"
                        key={report.task_uid}
                      >
                        <div className="ceo-report-header">
                          <div>
                            <span className="ceo-report-executive">
                              {report.executive}
                            </span>

                            <h3>
                              {report.task_title}
                            </h3>
                          </div>

                          <Badge variant="success">
                            Completed
                          </Badge>
                        </div>

                        <p className="ceo-report-mission">
                          {report.mission_title}
                        </p>

                        <p className="ceo-report-summary">
                          {truncateText(
                            report.summary,
                          )}
                        </p>

                        <div className="ceo-report-meta">
                          <span>
                            {formatCurrency(
                              report.estimated_value,
                            )}
                          </span>

                          <span>
                            {formatDate(
                              report.completed_at,
                            )}
                          </span>
                        </div>
                      </article>
                    ),
                  )}
                </div>
              ) : (
                <p className="ceo-empty-state">
                  No completed executive
                  reports are available yet.
                </p>
              )}
            </Card>

            <Card className="ceo-decisions-card">
              <p className="eyebrow">
                Recommended Decisions
              </p>

              <h2>What to Do Next</h2>

              <div className="ceo-recommendation-list">
                {recommendations.map(
                  (
                    recommendation,
                    index,
                  ) => (
                    <div
                      className="ceo-recommendation-item"
                      key={`${index}-${recommendation}`}
                    >
                      <span>
                        {index + 1}
                      </span>

                      <p>
                        {recommendation}
                      </p>
                    </div>
                  ),
                )}
              </div>
            </Card>
          </section>

          <section className="ceo-page-grid">
            <Card>
              <p className="eyebrow">
                Priority Leads
              </p>

              <h2>Top Opportunities</h2>

              {priorityLeads.length ? (
                <div className="ceo-priority-list">
                  {priorityLeads.map(
                    (lead, index) => (
                      <div
                        className="ceo-priority-item"
                        key={`${lead.name}-${index}`}
                      >
                        <div>
                          <strong>
                            {lead.name}
                          </strong>

                          <span>
                            {lead.priority}{" "}
                            priority
                          </span>

                          {lead.recommendation && (
                            <small>
                              {truncateText(
                                lead.recommendation,
                                120,
                              )}
                            </small>
                          )}
                        </div>

                        <Badge variant="primary">
                          {lead.score}/100
                        </Badge>
                      </div>
                    ),
                  )}
                </div>
              ) : (
                <p className="ceo-empty-state">
                  No qualified opportunities
                  are available.
                </p>
              )}
            </Card>

            <Card>
              <p className="eyebrow">
                Mission Portfolio
              </p>

              <h2>
                Recently Completed
              </h2>

              <div className="ceo-mission-list">
                {(
                  missionOverview.recent_completed ||
                  []
                ).map((mission) => (
                  <article
                    className="ceo-mission-item"
                    key={mission.mission_uid}
                  >
                    <div>
                      <h3>
                        {mission.title}
                      </h3>

                      <p>
                        {truncateText(
                          mission.objective,
                          150,
                        )}
                      </p>
                    </div>

                    <div className="ceo-mission-meta">
                      <span>
                        {formatCurrency(
                          mission.estimated_value,
                        )}
                      </span>

                      <span>
                        {formatDate(
                          mission.completed_at,
                        )}
                      </span>
                    </div>
                  </article>
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