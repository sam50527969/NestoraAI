import {
  useCallback,
  useEffect,
  useState,
} from "react";

import PropTypes from "prop-types";

import {
  getFollowUpMetrics,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";

import "./CEOFollowUpMetrics.css";

const OUTCOME_ITEMS = [
  {
    key: "contacted",
    label: "Contacted",
    variant: "primary",
  },
  {
    key: "qualified",
    label: "Qualified",
    variant: "success",
  },
  {
    key: "won",
    label: "Won",
    variant: "success",
  },
  {
    key: "lost",
    label: "Lost",
    variant: "danger",
  },
  {
    key: "no_response",
    label: "No Response",
    variant: "primary",
  },
  {
    key: "rescheduled",
    label: "Rescheduled",
    variant: "primary",
  },
];

function formatNumber(value) {
  return new Intl.NumberFormat(
    "en-US",
  ).format(Number(value) || 0);
}

function formatDatePart(date) {
  const year = date.getFullYear();

  const month = String(
    date.getMonth() + 1,
  ).padStart(2, "0");

  const day = String(
    date.getDate(),
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getDateFilters(period) {
  if (period === "all") {
    return {};
  }

  const endDate = new Date();
  const startDate = new Date();

  if (period === "7_days") {
    startDate.setDate(
      startDate.getDate() - 6,
    );
  } else if (period === "30_days") {
    startDate.setDate(
      startDate.getDate() - 29,
    );
  }

  return {
    startDate:
      `${formatDatePart(startDate)}T00:00:00`,
    endDate:
      `${formatDatePart(endDate)}T23:59:59`,
  };
}

export default function CEOFollowUpMetrics({
  businessUid,
}) {
  const [metrics, setMetrics] =
    useState(null);

  const [period, setPeriod] =
    useState("all");

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");

  const loadMetrics = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getFollowUpMetrics(
            getDateFilters(period),
          );

        setMetrics(response);
      } catch (error) {
        console.error(
          "Unable to load follow-up metrics:",
          error,
        );

        setErrorMessage(
          error?.message ||
            "Unable to load follow-up metrics.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [period],
  );

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics, businessUid]);

  const outcomes =
    metrics?.outcomes || {};

  const highestOutcomeCount = Math.max(
    1,
    ...OUTCOME_ITEMS.map(
      ({ key }) =>
        Number(outcomes[key]) || 0,
    ),
  );

  return (
    <Card className="ceo-follow-up-metrics">
      <div className="ceo-follow-up-metrics-header">
        <div>
          <p className="eyebrow">
            CRM Performance
          </p>

          <h2>Follow-up Metrics</h2>

          <p>
            Measure engagement, responses,
            qualification, and conversion
            from recorded CRM follow-ups.
          </p>
        </div>

        <div className="ceo-follow-up-metrics-actions">
          <label>
            <span>Period</span>

            <select
              value={period}
              onChange={(event) =>
                setPeriod(
                  event.target.value,
                )
              }
              disabled={isLoading}
            >
              <option value="all">
                All Time
              </option>

              <option value="today">
                Today
              </option>

              <option value="7_days">
                Last 7 Days
              </option>

              <option value="30_days">
                Last 30 Days
              </option>
            </select>
          </label>

          <button
            type="button"
            onClick={loadMetrics}
            disabled={isLoading}
          >
            {isLoading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="ceo-follow-up-metrics-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-follow-up-metrics-state">
          Loading follow-up metrics...
        </div>
      ) : metrics ? (
        <>
          <div className="ceo-follow-up-metrics-grid">
            <div>
              <span>Total Activities</span>

              <strong>
                {formatNumber(
                  metrics.total_activities,
                )}
              </strong>

              <small>
                Recorded follow-up actions
              </small>
            </div>

            <div>
              <span>Unique Leads</span>

              <strong>
                {formatNumber(
                  metrics.unique_leads,
                )}
              </strong>

              <small>
                Businesses followed up
              </small>
            </div>

            <div className="success">
              <span>Response Rate</span>

              <strong>
                {formatNumber(
                  metrics.response_rate,
                )}
                %
              </strong>

              <small>
                {formatNumber(
                  metrics.response_count,
                )}{" "}
                recorded responses
              </small>
            </div>

            <div className="success">
              <span>Win Rate</span>

              <strong>
                {formatNumber(
                  metrics.win_rate,
                )}
                %
              </strong>

              <small>
                Converted follow-up outcomes
              </small>
            </div>
          </div>

          <div className="ceo-follow-up-outcome-summary">
            {OUTCOME_ITEMS.map(
              ({
                key,
                label,
                variant,
              }) => (
                <Badge
                  variant={variant}
                  key={key}
                >
                  {formatNumber(
                    outcomes[key],
                  )}{" "}
                  {label}
                </Badge>
              ),
            )}
          </div>

          <div className="ceo-follow-up-outcome-chart">
            <div className="ceo-follow-up-outcome-chart-header">
              <div>
                <h3>
                  Outcome Distribution
                </h3>

                <p>
                  Recorded results for the
                  selected period.
                </p>
              </div>

              <span>
                {formatNumber(
                  metrics.total_activities,
                )}{" "}
                total
              </span>
            </div>

            <div className="ceo-follow-up-outcome-bars">
              {OUTCOME_ITEMS.map(
                ({ key, label }) => {
                  const count =
                    Number(
                      outcomes[key],
                    ) || 0;

                  const width =
                    count > 0
                      ? Math.max(
                          5,
                          (
                            count /
                            highestOutcomeCount
                          ) * 100,
                        )
                      : 0;

                  return (
                    <div
                      className={`ceo-follow-up-outcome-row outcome-${key}`}
                      key={key}
                    >
                      <div className="ceo-follow-up-outcome-label">
                        <span>{label}</span>

                        <strong>
                          {formatNumber(
                            count,
                          )}
                        </strong>
                      </div>

                      <div
                        className="ceo-follow-up-outcome-track"
                        role="progressbar"
                        aria-label={label}
                        aria-valuenow={count}
                        aria-valuemin="0"
                        aria-valuemax={
                          highestOutcomeCount
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
          </div>
        </>
      ) : (
        <div className="ceo-follow-up-metrics-state">
          No follow-up metrics are
          available.
        </div>
      )}
    </Card>
  );
}


CEOFollowUpMetrics.propTypes = {
  businessUid: PropTypes.string,
};
