import {
  useCallback,
  useEffect,
  useState,
} from "react";

import PropTypes from "prop-types";

import {
  downloadFollowUpHistory,
  getFollowUpActivities,
} from "../../../api";

import Badge from "../../ui/Badge";
import Card from "../../ui/Card";

import "./CEOFollowUpHistory.css";


function formatDate(value) {
  if (!value) {
    return "Not scheduled";
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


function formatOutcome(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}


function getOutcomeVariant(outcome) {
  if (
    outcome === "won" ||
    outcome === "qualified"
  ) {
    return "success";
  }

  if (outcome === "lost") {
    return "danger";
  }

  return "primary";
}


export default function CEOFollowUpHistory({
  businessUid,
}) {
  const [activities, setActivities] =
    useState([]);

  const [period, setPeriod] =
    useState("all");

  const [isLoading, setIsLoading] =
    useState(true);

  const [
    errorMessage,
    setErrorMessage,
  ] = useState("");


  const loadActivities = useCallback(
    async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const response =
          await getFollowUpActivities({
            ...getDateFilters(period),
            limit: 100,
          });

        setActivities(
          Array.isArray(response)
            ? response
            : [],
        );
      } catch (error) {
        console.error(
          "Unable to load follow-up history:",
          error,
        );

        setErrorMessage(
          error?.message ||
            "Unable to load follow-up history.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [period],
  );


  useEffect(() => {
    loadActivities();
  }, [loadActivities, businessUid]);


  return (
    <Card className="ceo-follow-up-history">
      <div className="ceo-follow-up-history-header">
        <div>
          <p className="eyebrow">
            CRM Activity
          </p>

          <h2>Follow-up History</h2>

          <p>
            Review recorded outcomes,
            CRM stage changes, notes, and
            scheduled next actions.
          </p>
        </div>

        <div className="ceo-follow-up-history-actions">
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

          <Badge variant="primary">
            {activities.length}
          </Badge>

          <button
            type="button"
            onClick={() =>
              downloadFollowUpHistory(
                getDateFilters(period),
              )
            }
          >
            Export CSV
          </button>

          <button
            type="button"
            onClick={loadActivities}
            disabled={isLoading}
          >
            {isLoading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="ceo-follow-up-history-error">
          {errorMessage}
        </div>
      )}

      {isLoading ? (
        <div className="ceo-follow-up-history-state">
          Loading follow-up history...
        </div>
      ) : activities.length ? (
        <div className="ceo-follow-up-history-list">
          {activities.map((activity) => (
            <article
              className="ceo-follow-up-history-item"
              key={activity.activity_uid}
            >
              <div className="ceo-follow-up-history-item-header">
                <div>
                  <span>
                    {formatDate(
                      activity.created_at,
                    )}
                  </span>

                  <h3>
                    {activity.lead_name}
                  </h3>
                </div>

                <Badge
                  variant={getOutcomeVariant(
                    activity.outcome,
                  )}
                >
                  {formatOutcome(
                    activity.outcome,
                  )}
                </Badge>
              </div>

              <div className="ceo-follow-up-history-meta">
                <div>
                  <span>
                    Previous Stage
                  </span>

                  <strong>
                    {activity.previous_status ||
                      "Not available"}
                  </strong>
                </div>

                <div>
                  <span>New Stage</span>

                  <strong>
                    {activity.new_status ||
                      "Not available"}
                  </strong>
                </div>

                <div>
                  <span>
                    Next Follow-up
                  </span>

                  <strong>
                    {formatDate(
                      activity.next_follow_up,
                    )}
                  </strong>
                </div>
              </div>

              {activity.notes && (
                <div className="ceo-follow-up-history-notes">
                  <span>Notes</span>

                  <p>
                    {activity.notes}
                  </p>
                </div>
              )}

              <div className="ceo-follow-up-history-footer">
                Recorded by{" "}
                {activity.completed_by ||
                  "CEO"}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="ceo-follow-up-history-state success">
          No follow-up outcomes were
          recorded during this period.
        </div>
      )}
    </Card>
  );
}


CEOFollowUpHistory.propTypes = {
  businessUid: PropTypes.string,
};
