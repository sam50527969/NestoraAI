import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getFollowUpMetrics,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";

import "./CEOFollowUpMetrics.css";


function formatNumber(value) {
  return new Intl.NumberFormat(
    "en-US",
  ).format(Number(value) || 0);
}


export default function CEOFollowUpMetrics() {
  const [metrics, setMetrics] =
    useState(null);

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
          await getFollowUpMetrics();

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
    [],
  );


  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);


  const outcomes =
    metrics?.outcomes || {};


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
            <Badge variant="primary">
              {formatNumber(
                outcomes.contacted,
              )}{" "}
              Contacted
            </Badge>

            <Badge variant="success">
              {formatNumber(
                outcomes.qualified,
              )}{" "}
              Qualified
            </Badge>

            <Badge variant="success">
              {formatNumber(
                outcomes.won,
              )}{" "}
              Won
            </Badge>

            <Badge variant="danger">
              {formatNumber(
                outcomes.lost,
              )}{" "}
              Lost
            </Badge>

            <Badge variant="primary">
              {formatNumber(
                outcomes.no_response,
              )}{" "}
              No Response
            </Badge>

            <Badge variant="primary">
              {formatNumber(
                outcomes.rescheduled,
              )}{" "}
              Rescheduled
            </Badge>
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