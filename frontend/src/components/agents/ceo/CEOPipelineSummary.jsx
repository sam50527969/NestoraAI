import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getPipelineSummary,
} from "../../../api";

import Card from "../../ui/Card";

import "./CEOPipelineSummary.css";

const PIPELINE_STAGES = [
  {
    key: "new",
    label: "New",
  },
  {
    key: "contacted",
    label: "Contacted",
  },
  {
    key: "qualified",
    label: "Qualified",
  },
  {
    key: "won",
    label: "Won",
  },
  {
    key: "lost",
    label: "Lost",
  },
];

function formatNumber(value) {
  return new Intl.NumberFormat(
    "en-US",
  ).format(Number(value) || 0);
}

function formatCurrency(value) {
  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "QAR",
      maximumFractionDigits: 0,
    },
  ).format(Number(value) || 0);
}

export default function CEOPipelineSummary() {
  const [summary, setSummary] =
    useState(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");

  const loadSummary = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getPipelineSummary();

        setSummary(response);
      } catch (error) {
        console.error(
          "Unable to load CRM pipeline:",
          error,
        );

        setErrorMessage(
          error?.message ||
            "Unable to load the CRM pipeline.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  const stages =
    summary?.stages || {};

  const highestStageCount = Math.max(
    1,
    ...PIPELINE_STAGES.map(
      ({ key }) =>
        Number(stages[key]) || 0,
    ),
  );

  return (
    <Card className="ceo-pipeline-summary">
      <div className="ceo-pipeline-header">
        <div>
          <p className="eyebrow">
            CRM Pipeline
          </p>

          <h2>
            Opportunity Pipeline
          </h2>

          <p>
            Monitor lead stages, active
            opportunity value, and expected
            revenue.
          </p>
        </div>

        <button
          type="button"
          onClick={loadSummary}
          disabled={isLoading}
        >
          {isLoading
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>

      {errorMessage && (
        <div className="ceo-pipeline-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-pipeline-state">
          Loading CRM pipeline...
        </div>
      ) : summary ? (
        <>
          <div className="ceo-pipeline-kpis">
            <div>
              <span>Total Leads</span>

              <strong>
                {formatNumber(
                  summary.total_leads,
                )}
              </strong>

              <small>
                Unique CRM opportunities
              </small>
            </div>

            <div>
              <span>
                Active Pipeline
              </span>

              <strong>
                {formatCurrency(
                  summary
                    .active_pipeline_value,
                )}
              </strong>

              <small>
                New, contacted, and qualified
              </small>
            </div>

            <div className="weighted">
              <span>
                Weighted Pipeline
              </span>

              <strong>
                {formatCurrency(
                  summary
                    .weighted_pipeline_value,
                )}
              </strong>

              <small>
                Adjusted by closing probability
              </small>
            </div>

            <div className="won">
              <span>Won Value</span>

              <strong>
                {formatCurrency(
                  summary.won_value,
                )}
              </strong>

              <small>
                Confirmed converted value
              </small>
            </div>
          </div>

          <div className="ceo-pipeline-stage-chart">
            <div className="ceo-pipeline-chart-header">
              <div>
                <h3>
                  Pipeline Stages
                </h3>

                <p>
                  Current distribution of CRM
                  opportunities.
                </p>
              </div>

              <span>
                {formatCurrency(
                  summary
                    .total_estimated_value,
                )}{" "}
                total value
              </span>
            </div>

            <div className="ceo-pipeline-stages">
              {PIPELINE_STAGES.map(
                ({ key, label }) => {
                  const count =
                    Number(
                      stages[key],
                    ) || 0;

                  const width =
                    count > 0
                      ? Math.max(
                          4,
                          (
                            count /
                            highestStageCount
                          ) * 100,
                        )
                      : 0;

                  return (
                    <div
                      className={`ceo-pipeline-stage stage-${key}`}
                      key={key}
                    >
                      <div className="ceo-pipeline-stage-label">
                        <span>{label}</span>

                        <strong>
                          {formatNumber(
                            count,
                          )}
                        </strong>
                      </div>

                      <div
                        className="ceo-pipeline-stage-track"
                        role="progressbar"
                        aria-label={`${label} leads`}
                        aria-valuenow={count}
                        aria-valuemin="0"
                        aria-valuemax={
                          highestStageCount
                        }
                      >
                        <span
                          style={{
                            width: `${width}%`,
                          }}
                        />
                      </div>
                    </div>
                  );
                },
              )}
            </div>

            <div className="ceo-pipeline-value-footer">
              <div>
                <span>Lost Value</span>

                <strong>
                  {formatCurrency(
                    summary.lost_value,
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Unweighted Total
                </span>

                <strong>
                  {formatCurrency(
                    summary
                      .total_estimated_value,
                  )}
                </strong>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="ceo-pipeline-state">
          No CRM pipeline information is
          available.
        </div>
      )}
    </Card>
  );
}